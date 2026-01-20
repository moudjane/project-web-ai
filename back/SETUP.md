# Setup Guide

This guide will walk you through setting up the PDF Embeddings API from scratch.

## Prerequisites

- Python 3.14 or higher
- Docker (for PostgreSQL with pgvector)
- Mistral API key
- `uv` package manager (or pip)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the `back` directory:

```bash
# Required
MISTRAL_API_KEY=your-mistral-api-key-here

# Optional (these are the defaults)
POSTGRES_USER=langchain
POSTGRES_PASSWORD=langchain
POSTGRES_HOST=localhost
POSTGRES_PORT=6024
POSTGRES_DB=langchain
```

**Important**: Never commit your `.env` file to version control!

### 3. Get Your Mistral API Key

1. Go to [Mistral AI Platform](https://console.mistral.ai/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

### 4. Start PostgreSQL with pgvector

```bash
# Using the Makefile
make db

# Or manually with Docker
docker run --name pgvector-container \
  -e POSTGRES_USER=langchain \
  -e POSTGRES_PASSWORD=langchain \
  -e POSTGRES_DB=langchain \
  -p 6024:5432 \
  -d pgvector/pgvector:pg16
```

**Verify the database is running:**

```bash
docker ps | grep pgvector-container
```

You should see the container running.

### 5. Initialize the Database

The vector store tables will be created automatically when you first upload a PDF. However, you can verify the connection:

```bash
# Connect to the database
docker exec -it pgvector-container psql -U langchain -d langchain

# Inside psql, check if pgvector extension is available
\dx

# Exit psql
\q
```

### 6. Start the FastAPI Server

```bash
# Using the Makefile
make run

# Or manually
uv run fastapi run main.py

# Or with uvicorn directly
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

### 7. Verify the Setup

**Check the health endpoint:**

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

**View API documentation:**

Open your browser and navigate to:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 8. Test the PDF Upload

**Prepare a test PDF:**

```bash
# Encode a PDF to base64
base64 -w 0 test.pdf > encoded.txt

# Send the request
curl -X POST "http://localhost:8000/upload-pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_base64": "'$(cat encoded.txt)'",
    "user_id": "test-user-123",
    "filename": "test.pdf"
  }'
```

**Expected response:**

```json
{
  "message": "PDF processed and embeddings created successfully",
  "filename": "test.pdf",
  "user_id": "test-user-123",
  "pages_processed": 5,
  "embeddings_created": 5,
  "document_ids": ["uuid1", "uuid2", "uuid3", "uuid4", "uuid5"]
}
```

## Troubleshooting

### Issue: "Could not connect to PostgreSQL"

**Solution:**
- Ensure Docker is running
- Check if the PostgreSQL container is running: `docker ps`
- Verify the port is not already in use: `netstat -an | grep 6024`
- Check connection string in your `.env` file

### Issue: "Mistral API key not found"

**Solution:**
- Verify your `.env` file exists in the `back` directory
- Check that `MISTRAL_API_KEY` is set correctly
- Make sure the API key is valid and has credits
- Restart the FastAPI server after adding the key

### Issue: "Invalid base64 string"

**Solution:**
- Ensure the PDF is properly base64 encoded
- Remove any line breaks from the base64 string
- Use `-w 0` flag with base64 command on Linux/Mac
- On Windows, use PowerShell's `[Convert]::ToBase64String()`

### Issue: "No text could be extracted from the PDF"

**Solution:**
- Verify the PDF contains text (not just images)
- For scanned PDFs, you'll need OCR preprocessing
- Try a different PDF file
- Check if the PDF is corrupted

### Issue: Port 6024 already in use

**Solution:**
```bash
# Stop the existing container
docker stop pgvector-container
docker rm pgvector-container

# Or use a different port
docker run --name pgvector-container \
  -e POSTGRES_USER=langchain \
  -e POSTGRES_PASSWORD=langchain \
  -e POSTGRES_DB=langchain \
  -p 6025:5432 \
  -d pgvector/pgvector:pg16

# Update POSTGRES_PORT in .env to 6025
```

## Database Management

### View stored embeddings

```bash
# Connect to the database
docker exec -it pgvector-container psql -U langchain -d langchain

# List tables
\dt

# Query embeddings (example)
SELECT * FROM langchain_pg_collection;
SELECT * FROM langchain_pg_embedding LIMIT 5;
```

### Reset the database

```bash
# Stop and remove the container
docker stop pgvector-container
docker rm pgvector-container

# Start fresh
make db
```

### Backup the database

```bash
# Create a backup
docker exec pgvector-container pg_dump -U langchain langchain > backup.sql

# Restore from backup
cat backup.sql | docker exec -i pgvector-container psql -U langchain -d langchain
```

## Development Tips

### Enable auto-reload

The server runs with `--reload` by default, so code changes will automatically restart the server.

### View logs

```bash
# FastAPI logs appear in your terminal

# PostgreSQL logs
docker logs pgvector-container
```

### Testing different embedding models

Edit `src/embeddings/embed.py` and modify the `get_embeddings_model()` function:

```python
# Current: Using Mistral
return MistralAIEmbeddings(model="mistral-embed")

# Or use OpenAI embeddings
from langchain_openai import OpenAIEmbeddings
return OpenAIEmbeddings(model="text-embedding-3-small")

# Or use HuggingFace embeddings (free, local)
from langchain_huggingface import HuggingFaceEmbeddings
return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
```

## Next Steps

Once your setup is complete:

1. Explore the API documentation at http://localhost:8000/docs
2. Implement query endpoints for semantic search
3. Add authentication and authorization
4. Implement document management features
5. Scale with production-grade PostgreSQL

## Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Mistral AI Documentation](https://docs.mistral.ai/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)