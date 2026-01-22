# PDF Embeddings API

A FastAPI application that processes PDF files and generates embeddings using LangChain and PostgreSQL with pgvector.

## Features

- Upload PDF files as base64 encoded strings
- Extract text from PDFs using LangChain document loaders
- Generate embeddings using Mistral embeddings
- Store embeddings in PostgreSQL with pgvector
- Associate embeddings with user IDs for multi-tenant support

## Requirements

- Python >= 3.14
- PostgreSQL with pgvector extension
- Docker (for running PostgreSQL)
- Mistral API key (for generating embeddings)

## Installation

**Important:** After cloning or modifying dependencies, always run:

```bash
# Install dependencies using uv
uv sync

# Or using pip
pip install -e .
```

This will install:
- `fastapi` - Web framework
- `langchain` - LLM framework
- `langchain-community` - Community loaders
- `langchain-mistralai` - Mistral embeddings
- `langchain-postgres` - PostgreSQL vector store
- `pypdf` - PDF text extraction
- `psycopg` - PostgreSQL driver

### 2. Configure Environment Variables

Create a `.env` file in the `back` directory:

```bash
# Mistral API Key (required for embeddings)
MISTRAL_API_KEY=your_mistral_api_key_here

# PostgreSQL Configuration (optional, defaults shown)
POSTGRES_USER=langchain
POSTGRES_PASSWORD=langchain
POSTGRES_HOST=localhost
POSTGRES_PORT=6024
POSTGRES_DB=langchain
```

## Running the Application

### Option 1: Using Docker Compose (Recommended)

This is the easiest way to run both the backend and database together.

1. **Create a `.env` file** in the `back` directory:

```bash
# Required: Mistral API Key for embeddings
MISTRAL_API_KEY=your_mistral_api_key_here

# Optional: PostgreSQL Configuration (defaults shown)
POSTGRES_USER=langchain
POSTGRES_PASSWORD=langchain
POSTGRES_DB=langchain
POSTGRES_PORT=6024
```

2. **Start both services**:

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL with pgvector on port 6024
- Start the FastAPI backend on port 8000
- Create a persistent volume for database data
- Connect both services on a private network

3. **View logs**:

```bash
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# Just database
docker-compose logs -f db
```

4. **Stop services**:

```bash
# Stop but keep data
docker-compose down

# Stop and remove data
docker-compose down -v
```

The API will be available at `http://localhost:8000`

### Option 2: Local Development

If you want to run the backend locally (outside Docker):

1. **Set up your Mistral API Key**:

```bash
export MISTRAL_API_KEY=your_mistral_api_key_here
```

Or add it to your `.env` file.

2. **Start PostgreSQL with pgvector**:

```bash
make db
```

This will start a PostgreSQL container with:
- Database: `langchain`
- User: `langchain`
- Password: `langchain`
- Port: `6024`

3. **Start the FastAPI server**:

```bash
make run
```

The API will be available at `http://localhost:8000`

### 4. Quick Test

Use the included test script to verify everything works:

```bash
# Test with auto-generated PDF
python test_upload.py

# Test with your own PDF
python test_upload.py path/to/your/document.pdf

# Test with custom user ID
python test_upload.py --user-id my-user-123

# Test with different API URL
python test_upload.py --api-url http://localhost:8000
```

The test script will:
- Check API health
- Load or create a test PDF
- Encode it to base64
- Upload tocumentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### POST /upload-pdf

Upload a PDF file as base64 encoded string, extract text, generate embeddings, and store them in PostgreSQL.

**Request Body:**
```json
{
  "pdf_base64": "JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PC...",
  "user_id": "user123",
  "filename": "document.pdf"
}
```

**Response (200 OK):**
```json
{
  "message": "PDF processed and embeddings created successfully",
  "filename": "document.pdf",
  "user_id": "user123",
  "pages_processed": 5,
  "embeddings_created": 5,
  "document_ids": ["uuid1", "uuid2", "uuid3", "uuid4", "uuid5"]
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Invalid base64 string: ..."
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "detail": "An error occurred while processing the PDF: ..."
}
```

### POST /query

Perform semantic search on uploaded documents using natural language queries.

**Request Body:**
```json
{
  "query": "What is machine learning?",
  "user_id": "user123",
  "k": 5
}
```

**Parameters:**
- `query` (string, required): Search query text
- `user_id` (string, required): User ID to filter documents
- `k` (integer, optional): Number of results to return (default: 5, min: 1, max: 50)

**Response (200 OK):**
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
    {
      "content": "AI and machine learning algorithms...",
      "metadata": {
        "source": "ai_guide.pdf",
        "page": 3,
        "user_id": "user123",
        "doc_id": "uuid-456"
      },
      "similarity_score": 0.87
    }
  ]
}
```

**Response (200 OK - No Results):**
```json
{
  "query": "quantum physics",
  "user_id": "user123",
  "results_count": 0,
  "results": [],
  "message": "No documents found for this user or no matches for the query"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Query cannot be empty"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "detail": "An error occurred during search: ..."
}
```

### GET /health

Health check endpoint.

**Response (200 OK):**
```json
{
  "status": "healthy"
}
```

## Usage Examples

### Using curl

```bash
# Encode your PDF file to base64
base64 -w 0 your_document.pdf > encoded.txt

# Upload the PDF (Linux/Mac)
curl -X POST "http://localhost:8000/upload-pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_base64": "'$(cat encoded.txt)'",
    "user_id": "user123",
    "filename": "your_document.pdf"
  }'

# Query the documents
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "user_id": "user123",
    "k": 5
  }'

# For Windows PowerShell
$base64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("your_document.pdf"))
$body = @{
    pdf_base64 = $base64
    user_id = "user123"
    filename = "your_document.pdf"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/upload-pdf" -Method Post -Body $body -ContentType "application/json"

# Query documents
$queryBody = @{
    query = "What is machine learning?"
    user_id = "user123"
    k = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post -Body $queryBody -ContentType "application/json"
```

### Using Python

```python
import base64
import requests

# Upload PDF
with open("your_document.pdf", "rb") as f:
    pdf_base64 = base64.b64encode(f.read()).decode('utf-8')

upload_response = requests.post(
    "http://localhost:8000/upload-pdf",
    json={
        "pdf_base64": pdf_base64,
        "user_id": "user123",
        "filename": "your_document.pdf"
    }
)
print("Upload:", upload_response.json())

# Query documents
query_response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "What is machine learning?",
        "user_id": "user123",
        "k": 5
    }
)
print("Query:", query_response.json())
```

### Using JavaScript/Node.js

```javascript
const fs = require('fs');
const axios = require('axios');

// Upload PDF
const pdfBuffer = fs.readFileSync('your_document.pdf');
const pdfBase64 = pdfBuffer.toString('base64');

axios.post('http://localhost:8000/upload-pdf', {
    pdf_base64: pdfBase64,
    user_id: 'user123',
    filename: 'your_document.pdf'
})
.then(response => console.log('Upload:', response.data))
.catch(error => console.error(error.response.data));

// Query documents
axios.post('http://localhost:8000/query', {
    query: 'What is machine learning?',
    user_id: 'user123',
    k: 5
})
.then(response => console.log('Query:', response.data))
.catch(error => console.error(error.response.data));
```

## Database Connection

### When using Docker Compose:
The backend connects to the database using the service name:
```
postgresql://langchain:langchain@db:5432/langchain
```

### When running locally:
The backend connects to PostgreSQL on your host:
```
postgresql://langchain:langchain@localhost:6024/langchain
```

### Environment Variables

The connection can be configured using:
- `POSTGRES_HOST` - Database host (default: `localhost`, Docker: `db`)
- `POSTGRES_PORT` - Database port (default: `6024`, inside Docker: `5432`)
- `POSTGRES_USER` - Database user (default: `langchain`)
- `POSTGRES_PASSWORD` - Database password (default: `langchain`)
- `POSTGRES_DB` - Database name (default: `langchain`)

Or use a complete connection string:
- `DB_CONNECTION_STRING` - Full PostgreSQL connection URL (overrides individual settings)

## Development

### Project Structure

```
back/
├── main.py                      # FastAPI application entry point
├── loader.py                    # PDF to Document conversion
├── test_upload.py              # Test script for API
├── src/
│   └── embeddings/
│       └── embed.py            # Embeddings generation and storage
├── pyproject.toml              # Project dependencies
├── Makefile                    # Common commands (run, db)
├── README.md                   # API documentation
├── SETUP.md                    # Setup instructions
├── SUMMARY.md                  # Project overview
├── CHECKLIST.md                # Setup checklist
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
└── .venv/                      # Virtual environment
```

## How It Works

1. **PDF Upload**: Client sends a base64-encoded PDF with a user_id
2. **Text Extraction**: The PDF is converted to LangChain Documents (one per page) using `pypdf`
3. **Embedding Generation**: Each document is embedded using Mistral's `mistral-embed` model
4. **Storage**: Embeddings are stored in PostgreSQL with pgvector, associated with the user_id
5. **Metadata**: Each embedding includes metadata (filename, page number, user_id, document_id)

## Next Steps

- [x] Add query/search endpoints for semantic search
- [ ] Add document management endpoints (list, delete)
- [ ] Support for other embedding models (OpenAI, HuggingFace, Cohere, etc.)
- [ ] Implement document chunking for large PDFs
- [ ] Add authentication and authorization
- [ ] Add relevance threshold filtering
- [ ] Implement hybrid search (keyword + semantic)

## License

TBD