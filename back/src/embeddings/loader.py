import io
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def pdf_to_documents(
    pdf_bytes: bytes, filename: str = "document.pdf"
) -> List[Document]:
    """
    Convert PDF bytes to a list of LangChain Document objects.

    Args:
        pdf_bytes: The PDF file content as bytes
        filename: Optional filename for metadata (defaults to "document.pdf")

    Returns:
        List[Document]: A list of Document objects, typically one per page

    Raises:
        Exception: If PDF processing fails

    Example:
        ```python
        with open("example.pdf", "rb") as f:
            pdf_bytes = f.read()

        documents = pdf_to_documents(pdf_bytes, "example.pdf")
        for i, doc in enumerate(documents):
            print(f"Page {i+1}: {doc.page_content[:100]}...")
            print(f"Metadata: {doc.metadata}")
        ```
    """
    # Create a temporary file-like object from bytes
    pdf_file = io.BytesIO(pdf_bytes)

    # Note: PyPDFLoader typically requires a file path, so we'll use PyPDFium2Loader
    # or pypdf directly for in-memory processing
    from pypdf import PdfReader

    documents = []

    try:
        # Read PDF from bytes
        pdf_reader = PdfReader(pdf_file)

        # Extract text from each page
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()

            # Create Document with metadata
            doc = Document(
                page_content=text,
                metadata={
                    "source": filename,
                    "page": page_num,
                    "total_pages": len(pdf_reader.pages),
                },
            )
            documents.append(doc)

        return documents

    except Exception as e:
        raise Exception(f"Failed to process PDF: {str(e)}")


def pdf_to_documents_with_loader(pdf_path: str) -> List[Document]:
    """
    Alternative function that uses PyPDFLoader for file-based loading.
    This is useful when you have a PDF file path instead of bytes.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List[Document]: A list of Document objects

    Example:
        ```python
        documents = pdf_to_documents_with_loader("path/to/file.pdf")
        ```
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    return documents
