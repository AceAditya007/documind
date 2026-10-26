# DocuMind – AI-Powered Document Q&A System

**A Python-based Retrieval-Augmented Generation (RAG) backend that enables users to upload PDF documents and ask natural-language questions using locally hosted AI models.**

DocuMind combines **FastAPI, LangChain, Ollama, ChromaDB, and SQLite** to provide document-grounded question answering through REST APIs.

## Overview

DocuMind is a backend-focused AI application designed to retrieve relevant information from uploaded PDF documents and generate context-aware responses.

Instead of relying solely on an LLM's pre-trained knowledge, the application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant document passages before generating an answer.

The system runs locally using Ollama, allowing document processing and inference without requiring a cloud LLM API.

## Key Features

- **PDF Upload:** Upload PDF documents through FastAPI endpoints.
- **Automatic Document Indexing:** Extract and process document content immediately after upload.
- **Text Chunking:** Split large documents into smaller overlapping text segments.
- **Vector Embeddings:** Generate document embeddings using the `all-minilm` model.
- **Semantic Search:** Retrieve relevant document chunks using ChromaDB.
- **AI-Powered Q&A:** Generate responses using the locally hosted Qwen3 1.7B language model.
- **Document-Specific Retrieval:** Filter search results using document IDs to avoid mixing content from different PDFs.
- **Source References:** Return original filenames, page numbers, and retrieved text chunks.
- **Database Management:** Manage document metadata using SQLite CRUD operations.
- **REST API Documentation:** Test endpoints through FastAPI's automatically generated Swagger UI.
- **Document Cleanup:** Includes logic for deleting document metadata, stored files, and indexed vectors.

## Tech Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| API Validation | Pydantic |
| ASGI Server | Uvicorn |
| RAG Framework | LangChain |
| LLM Runtime | Ollama |
| Language Model | Qwen3 1.7B |
| Embedding Model | all-minilm |
| Vector Database | ChromaDB |
| Relational Database | SQLite |
| PDF Processing | PyMuPDF |
| API Testing | Swagger UI |

## System Architecture

```text
                    CLIENT / SWAGGER UI
                            |
                            v
                      FASTAPI BACKEND
                            |
                +-----------+-----------+
                |                       |
                v                       v
          PDF UPLOAD API             QUESTION API
                |                       |
                v                       v
          PDF VALIDATION           PYDANTIC VALIDATION
                |                       |
                v                       v
          LOCAL PDF STORAGE        DOCUMENT ID FILTER
                |                       |
                v                       v
          PyMuPDF EXTRACTION       QUERY EMBEDDING
                |                       |
                v                       v
            TEXT CHUNKING          CHROMADB SEARCH
                |                       |
                v                       v
           OLLAMA EMBEDDINGS      RELEVANT PDF CHUNKS
                |                       |
                v                       v
            CHROMADB STORAGE       QWEN3 VIA OLLAMA
                |                       |
                v                       v
           DOCUMENT INDEX          GENERATED ANSWER
                |                       |
                +-----------+-----------+
                            |
                            v
                    JSON RESPONSE
```

SQLite stores document metadata, while ChromaDB stores document embeddings and their associated source metadata.

## How the RAG Pipeline Works

### 1. Document Upload

The user uploads a PDF through the `/upload` endpoint. FastAPI receives and validates the file before saving it locally.

### 2. Text Extraction

PyMuPDF reads the
