
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from pdf_processor import extract_pages_from_pdf, chunk_text


def index_pdf(file_path, original_filename, stored_filename, document_id):

    # Extract text separately from each PDF page
    pages = extract_pages_from_pdf(str(file_path))

    all_chunks = []
    metadatas = []
    ids = []

    chunk_index = 0

    for page in pages:
        page_number = page["page"]
        page_text = page["text"]

        # Chunk each page independently
        chunks = chunk_text(page_text)

        for chunk in chunks:
            if not chunk.strip():
                continue

            all_chunks.append(chunk)

            metadatas.append({
                "document_id": document_id,
                "source": original_filename,
                "stored_filename": stored_filename,
                "page": page_number,
                "chunk_index": chunk_index
            })

            ids.append(
                f"document_{document_id}_chunk_{chunk_index}"
            )

            chunk_index += 1

    if not all_chunks:
        raise ValueError("No readable text found in PDF")

    embeddings = OllamaEmbeddings(model="all-minilm")

    vector_db = Chroma(
        collection_name="documind_v2",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )

    # Save chunks with source metadata
    vector_db.add_texts(
        texts=all_chunks,
        ids=ids,
        metadatas=metadatas
    )

    print(f"Document {document_id} indexed successfully")
    print(f"Total chunks: {len(all_chunks)}")

    return len(all_chunks)
