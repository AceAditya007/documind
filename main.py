
from pathlib import Path
import uuid
from document_cleanup import delete_document_completely
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from database import (
    create_table,
    add_document,
    get_documents,
    get_document_by_id,
    delete_document,
    update_document
)

from rag_answer import generate_answer
from indexer import index_pdf


# ==========================================
# INITIALIZE APPLICATION
# ==========================================

app = FastAPI(
    title="DocuMind API",
    description="AI-Powered RAG Document Q&A System",
    version="1.0.0"
)

create_table()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ==========================================
# PYDANTIC MODELS
# ==========================================

class Question(BaseModel):
    document_id: int = Field(gt=0)
    question: str = Field(min_length=3)


class Document(BaseModel):
    filename: str = Field(min_length=3)


# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():
    return {
        "message": "Welcome to DocuMind",
        "status": "running"
    }


# ==========================================
# AI-POWERED DOCUMENT QUESTION ANSWERING
# ==========================================

@app.post("/ask")
def ask_question(data: Question):

    # Verify the document exists in SQLite
    document = get_document_by_id(data.document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Retrieve chunks and generate AI answer
    try:
        result = generate_answer(
            question=data.question,
            document_id=data.document_id
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="RAG service is currently unavailable"
        ) from exc

    return {
        "document_id": data.document_id,
        "question": data.question,
        "answer": result["answer"],
        "sources": result["sources"]
    }


# ==========================================
# CREATE DOCUMENT METADATA
# ==========================================

@app.post("/documents", status_code=201)
def create_document(data: Document):

    document_id = add_document(data.filename)

    return {
        "message": "Document record created",
        "id": document_id,
        "filename": data.filename
    }


# ==========================================
# GET ALL DOCUMENTS
# ==========================================

@app.get("/documents")
def list_documents():
    return get_documents()


# ==========================================
# GET DOCUMENT BY ID
# ==========================================

@app.get("/documents/{document_id}")
def read_document(document_id: int):

    document = get_document_by_id(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


# ==========================================
# UPDATE DOCUMENT METADATA
# ==========================================

@app.put("/documents/{document_id}")
def edit_document(document_id: int, data: Document):

    updated = update_document(
        document_id,
        data.filename
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {
        "message": "Document updated successfully",
        "id": document_id,
        "filename": data.filename
    }


# ==========================================
# DELETE DOCUMENT METADATA
# ==========================================

@app.delete("/documents/{document_id}")
def remove_document(document_id: int):

    deleted = delete_document(document_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {
        "message": "Document metadata deleted successfully"
    }


# ==========================================
# PDF UPLOAD + AUTOMATIC INDEXING
# ==========================================

@app.post("/upload", status_code=201)
async def upload_pdf(file: UploadFile = File(...)):

    # Validate PDF extension
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # Read uploaded file
    file_content = await file.read()

    # Maximum file size: 5 MB
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File exceeds 5 MB limit"
        )

    # Basic PDF signature check
    if not file_content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file"
        )

    # Generate unique storage filename
    stored_filename = f"{uuid.uuid4().hex}.pdf"

    file_path = UPLOAD_DIR / stored_filename

    document_id = None

    try:
        # Save the PDF
        file_path.write_bytes(file_content)

        # Create SQLite record first to obtain ID
        document_id = add_document(file.filename)

        # Extract, chunk, embed and index PDF
        total_chunks = await run_in_threadpool(
            index_pdf,
            file_path,
            file.filename,
            stored_filename,
            document_id
        )

    except ValueError as exc:

        if document_id is not None:
            delete_document(document_id)

        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    except Exception as exc:

        if document_id is not None:
            delete_document(document_id)

        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=503,
            detail="PDF processing or indexing failed"
        ) from exc

    return {
        "message": "PDF uploaded and indexed successfully",
        "id": document_id,
        "filename": file.filename,
        "stored_filename": stored_filename,
        "total_chunks": total_chunks
    }
