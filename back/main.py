import base64

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.embeddings.embed import create_embeddings, query_embeddings_with_scores
from src.embeddings.loader import pdf_to_documents

load_dotenv()

app = FastAPI(title="PDF Embeddings API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PDFUploadRequest(BaseModel):
    pdf_base64: str = Field(..., description="PDF file encoded as base64 string")
    user_id: str = Field(
        ..., description="User ID to associate with the PDF embeddings"
    )
    filename: str = Field(
        default="document.pdf", description="Optional filename for the PDF"
    )


class QueryRequest(BaseModel):
    query: str = Field(..., description="Search query text")
    user_id: str = Field(..., description="User ID to filter documents")
    k: int = Field(
        default=5, ge=1, le=50, description="Number of results to return (1-50)"
    )


@app.post("/upload-pdf")
async def upload_pdf(request: PDFUploadRequest):
    """
    Endpoint to receive a PDF file as base64 and process it for embeddings.

    Args:
        request: PDFUploadRequest containing:
            - pdf_base64: Base64 encoded PDF file (required)
            - user_id: User ID to associate with embeddings (required)
            - filename: Name of the PDF file (optional, defaults to "document.pdf")

    Returns:
        JSON response with:
            - message: Success message
            - filename: Name of the uploaded file
            - user_id: User ID associated with the embeddings
            - pages_processed: Number of pages processed
            - embeddings_created: Number of embeddings created
            - document_ids: List of document IDs added to the database

    Raises:
        HTTPException 400: If base64 is invalid or file is not a valid PDF
        HTTPException 500: If an unexpected error occurs during processing

    Example curl command:
        ```bash
        # First, encode your PDF to base64
        base64 -w 0 your_document.pdf > encoded.txt

        # Then send the request
        curl -X POST "http://localhost:8000/upload-pdf" \\
          -H "Content-Type: application/json" \\
          -d '{
            "pdf_base64": "'$(cat encoded.txt)'",
            "user_id": "user123",
            "filename": "your_document.pdf"
          }'
        ```

    Example response:
        ```json
        {
            "message": "PDF processed and embeddings created successfully",
            "filename": "your_document.pdf",
            "user_id": "user123",
            "pages_processed": 5,
            "embeddings_created": 5,
            "document_ids": ["uuid1", "uuid2", "uuid3", "uuid4", "uuid5"]
        }
        ```
    """
    try:
        # Validate base64 string
        try:
            pdf_bytes = base64.b64decode(request.pdf_base64)
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid base64 string: {str(e)}"
            )

        # Validate PDF header (PDF files start with %PDF)
        if not pdf_bytes.startswith(b"%PDF"):
            raise HTTPException(
                status_code=400,
                detail="The provided file does not appear to be a valid PDF",
            )

        # Convert PDF bytes to LangChain Documents
        documents = pdf_to_documents(pdf_bytes, request.filename)

        if not documents:
            raise HTTPException(
                status_code=400, detail="No text could be extracted from the PDF"
            )

        # Generate embeddings and store in PostgreSQL
        document_ids = create_embeddings(
            documents=documents,
            user_id=request.user_id,
            collection_name="pdf_embeddings",
        )

        return {
            "message": "PDF processed and embeddings created successfully",
            "filename": request.filename,
            "user_id": request.user_id,
            "pages_processed": len(documents),
            "embeddings_created": len(document_ids),
            "document_ids": document_ids,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the PDF: {str(e)}",
        )


@app.post("/query")
async def query_documents(request: QueryRequest):
    """
    Endpoint to perform semantic search on user's documents.

    This endpoint:
    1. Takes the query string and embeds it using Mistral AI (same model as upload)
    2. Performs vector similarity search in PostgreSQL
    3. Returns the most similar documents with similarity scores

    Args:
        request: QueryRequest containing:
            - query: Search query text (required)
            - user_id: User ID to filter documents (required)
            - k: Number of results to return (optional, default: 5, max: 50)

    Returns:
        JSON response with:
            - query: The original search query
            - user_id: User ID that was searched
            - results_count: Number of results returned
            - results: List of matching documents with content, metadata, and similarity scores

    Raises:
        HTTPException 400: If query is empty
        HTTPException 404: If no documents found for user
        HTTPException 500: If search fails

    Example curl command:
        ```bash
        curl -X POST "http://localhost:8000/query" \\
          -H "Content-Type: application/json" \\
          -d '{
            "query": "What is machine learning?",
            "user_id": "user123",
            "k": 5
          }'
        ```

    Example response:
        ```json
        {
            "query": "What is machine learning?",
            "user_id": "user123",
            "results_count": 3,
            "results": [
                {
                    "content": "Machine learning is a subset of artificial intelligence...",
                    "metadata": {
                        "source": "ml_basics.pdf",
                        "page": 1,
                        "user_id": "user123",
                        "doc_id": "uuid-123"
                    },
                    "similarity_score": 0.92
                },
                ...
            ]
        }
        ```
    """
    try:
        # Validate query
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Perform semantic search with similarity scores
        # This function:
        # 1. Embeds the query string using Mistral (same model as documents)
        # 2. Performs vector similarity search in PostgreSQL
        # 3. Returns top k similar documents with their similarity scores
        results_with_scores = query_embeddings_with_scores(
            query=request.query,
            user_id=request.user_id,
            k=request.k,
            collection_name="pdf_embeddings",
        )

        # Check if any results found
        if not results_with_scores:
            return {
                "query": request.query,
                "user_id": request.user_id,
                "results_count": 0,
                "results": [],
                "message": "No documents found for this user or no matches for the query",
            }

        # Format results
        results = []
        for doc, score in results_with_scores:
            results.append(
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score,
                }
            )

        return {
            "query": request.query,
            "user_id": request.user_id,
            "results_count": len(results),
            "results": results,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred during search: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
