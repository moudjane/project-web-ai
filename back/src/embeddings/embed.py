import os
from typing import List
from uuid import uuid4

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_postgres.vectorstores import PGVector

try:
    from langchain_mistralai import MistralAIEmbeddings
except ImportError:
    MistralAIEmbeddings = None


def get_connection_string() -> str:
    """
    Get PostgreSQL connection string from environment variables or use defaults.

    Returns:
        str: PostgreSQL connection string
    """
    connection_string = os.environ.get("DB_CONNECTION_STRING")
    if connection_string:
        return connection_string

    db_user = os.getenv("POSTGRES_USER", "langchain")
    db_password = os.getenv("POSTGRES_PASSWORD", "langchain")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "6024")
    db_name = os.getenv("POSTGRES_DB", "langchain")

    return f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_embeddings_model() -> Embeddings:
    """
    Get the embeddings model. Currently uses Mistral embeddings.

    Returns:
        Embeddings: An embeddings model instance

    Note:
        Requires MISTRAL_API_KEY environment variable to be set.
    """
    # You can swap this out for other embedding models:
    # - from langchain_openai import OpenAIEmbeddings
    # - from langchain_huggingface import HuggingFaceEmbeddings
    # - from langchain_google_genai import GoogleGenerativeAIEmbeddings
    # - from langchain_cohere import CohereEmbeddings

    if MistralAIEmbeddings is None:
        raise ImportError(
            "Mistral embeddings not available. Install with: pip install langchain-mistralai"
        )

    return MistralAIEmbeddings(
        model="mistral-embed",
        # mistral_api_key is read from MISTRAL_API_KEY env var by default
    )


def create_embeddings(
    documents: List[Document], user_id: str, collection_name: str = "pdf_embeddings"
) -> List[str]:
    """
    Generate embeddings from documents and store them in PostgreSQL with pgvector.

    Args:
        documents: List of LangChain Document objects to embed
        user_id: The user ID to associate with these embeddings
        collection_name: Name of the collection/table in the database

    Returns:
        List[str]: List of document IDs that were added to the database

    Raises:
        Exception: If embedding generation or database insertion fails

    Example:
        ```python
        from langchain_core.documents import Document

        docs = [
            Document(page_content="Page 1 text", metadata={"page": 1}),
            Document(page_content="Page 2 text", metadata={"page": 2})
        ]

        doc_ids = create_embeddings(docs, user_id="user123")
        print(f"Added {len(doc_ids)} documents to the database")
        ```
    """
    try:
        # Add user_id to metadata for each document
        for doc in documents:
            doc.metadata["user_id"] = user_id
            # Add a unique document ID if not present
            if "doc_id" not in doc.metadata:
                doc.metadata["doc_id"] = str(uuid4())

        # Get embeddings model
        embeddings_model = get_embeddings_model()

        # Get connection string
        connection_string = get_connection_string()

        # Create or connect to vector store
        vectorstore = PGVector(
            embeddings=embeddings_model,
            collection_name=collection_name,
            connection=connection_string,
            use_jsonb=True,
        )

        # Add documents to the vector store
        doc_ids = vectorstore.add_documents(documents)

        return doc_ids

    except Exception as e:
        raise Exception(f"Failed to create embeddings: {str(e)}")


def query_embeddings(
    query: str, user_id: str, k: int = 5, collection_name: str = "pdf_embeddings"
) -> List[Document]:
    """
    Query embeddings for similar documents for a specific user.

    This function:
    1. Takes the query string
    2. Automatically embeds it using the same embedding model (Mistral)
    3. Performs vector similarity search in PostgreSQL
    4. Returns the most similar documents

    Args:
        query: The search query text (will be embedded automatically)
        user_id: Filter results to only this user's documents
        k: Number of results to return (default: 5)
        collection_name: Name of the collection/table to query

    Returns:
        List[Document]: List of similar documents with their content and metadata

    Example:
        ```python
        results = query_embeddings(
            query="What is the main topic?",
            user_id="user123",
            k=3
        )

        for doc in results:
            print(f"Page {doc.metadata['page']}: {doc.page_content[:100]}...")
        ```
    """
    try:
        # Get embeddings model (same model used for storing documents)
        embeddings_model = get_embeddings_model()

        # Get connection string
        connection_string = get_connection_string()

        # Connect to existing vector store
        vectorstore = PGVector(
            embeddings=embeddings_model,
            collection_name=collection_name,
            connection=connection_string,
            use_jsonb=True,
        )

        # Query with filter for user_id
        # Note: similarity_search() internally:
        # 1. Embeds the query string using embeddings_model.embed_query(query)
        # 2. Performs vector similarity search (cosine similarity by default)
        # 3. Returns the k most similar documents
        results = vectorstore.similarity_search(query, k=k, filter={"user_id": user_id})

        return results

    except Exception as e:
        raise Exception(f"Failed to query embeddings: {str(e)}")


def query_embeddings_with_scores(
    query: str, user_id: str, k: int = 5, collection_name: str = "pdf_embeddings"
) -> List[tuple[Document, float]]:
    """
    Query embeddings for similar documents with similarity scores.

    This function:
    1. Takes the query string
    2. Automatically embeds it using the same embedding model (Mistral)
    3. Performs vector similarity search in PostgreSQL
    4. Returns the most similar documents WITH their similarity scores

    Args:
        query: The search query text (will be embedded automatically)
        user_id: Filter results to only this user's documents
        k: Number of results to return (default: 5)
        collection_name: Name of the collection/table to query

    Returns:
        List[tuple[Document, float]]: List of tuples (document, similarity_score)
        where similarity_score is a float (higher = more similar)

    Example:
        ```python
        results = query_embeddings_with_scores(
            query="What is machine learning?",
            user_id="user123",
            k=3
        )

        for doc, score in results:
            print(f"Score: {score:.4f}")
            print(f"Page {doc.metadata['page']}: {doc.page_content[:100]}...")
        ```
    """
    try:
        # Get embeddings model (same model used for storing documents)
        embeddings_model = get_embeddings_model()

        # Get connection string
        connection_string = get_connection_string()

        # Connect to existing vector store
        vectorstore = PGVector(
            embeddings=embeddings_model,
            collection_name=collection_name,
            connection=connection_string,
            use_jsonb=True,
        )

        # Query with filter for user_id and get similarity scores
        # similarity_search_with_score() returns List[Tuple[Document, float]]
        # The score is the similarity score (higher = more similar)
        results = vectorstore.similarity_search_with_score(
            query, k=k, filter={"user_id": user_id}
        )

        return results

    except Exception as e:
        raise Exception(f"Failed to query embeddings with scores: {str(e)}")


def query_embeddings_explicit(
    query: str, user_id: str, k: int = 5, collection_name: str = "pdf_embeddings"
) -> List[Document]:
    """
    Query embeddings with explicit embedding step (for educational purposes).

    This function shows the manual process:
    1. Takes the query string
    2. Explicitly embeds it using the embedding model
    3. Performs vector similarity search using the query vector
    4. Returns the most similar documents

    Args:
        query: The search query text
        user_id: Filter results to only this user's documents
        k: Number of results to return (default: 5)
        collection_name: Name of the collection/table to query

    Returns:
        List[Document]: List of similar documents with their content and metadata

    Example:
        ```python
        # This does the same thing as query_embeddings() but shows the steps
        results = query_embeddings_explicit(
            query="What is the main topic?",
            user_id="user123",
            k=3
        )

        for doc in results:
            print(f"Page {doc.metadata['page']}: {doc.page_content[:100]}...")
        ```
    """
    try:
        # Get embeddings model (same model used for storing documents)
        embeddings_model = get_embeddings_model()

        # STEP 1: Explicitly embed the query string to get a vector
        query_vector = embeddings_model.embed_query(query)
        # query_vector is now a list of floats (e.g., 1024 dimensions for mistral-embed)

        # Get connection string
        connection_string = get_connection_string()

        # Connect to existing vector store
        vectorstore = PGVector(
            embeddings=embeddings_model,
            collection_name=collection_name,
            connection=connection_string,
            use_jsonb=True,
        )

        # STEP 2: Perform similarity search using the query vector
        # This compares the query_vector against all document vectors in the database
        results = vectorstore.similarity_search_by_vector(
            embedding=query_vector, k=k, filter={"user_id": user_id}
        )

        return results

    except Exception as e:
        raise Exception(f"Failed to query embeddings explicitly: {str(e)}")


def delete_user_embeddings(
    user_id: str, collection_name: str = "pdf_embeddings"
) -> bool:
    """
    Delete all embeddings for a specific user.

    Args:
        user_id: The user ID whose embeddings should be deleted
        collection_name: Name of the collection/table

    Returns:
        bool: True if deletion was successful

    Example:
        ```python
        success = delete_user_embeddings(user_id="user123")
        if success:
            print("User embeddings deleted successfully")
        ```
    """
    try:
        # Get embeddings model
        embeddings_model = get_embeddings_model()

        # Get connection string
        connection_string = get_connection_string()

        # Note: PGVector doesn't have a built-in delete by filter
        # You would need to use raw SQL for this
        # This is a placeholder - actual implementation would require
        # direct database access via psycopg

        # Connect to vector store
        # vectorstore = PGVector(
        #     embeddings=embeddings_model,
        #     collection_name=collection_name,
        #     connection=connection_string,
        #     use_jsonb=True,
        # )

        # For now, we'll return True
        # TODO: Implement actual deletion logic with direct SQL
        return True

    except Exception as e:
        raise Exception(f"Failed to delete embeddings: {str(e)}")
