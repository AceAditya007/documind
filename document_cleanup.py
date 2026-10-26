
import re
from pathlib import Path

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from database import get_document_by_id, delete_document


def delete_document_completely(document_id: int):

    # 1. Check SQLite record
    document = get_document_by_id(document_id)

    if document is None:
        return False

    # 2. Connect to ChromaDB
    embeddings = OllamaEmbeddings(model="all-minilm")

    vector_db = Chroma(
        collection_name="documind_v2",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )

    # 3. Find chunks belonging to the document
    records = vector_db.get(
        where={"document_id": document_id},
        include=["metadatas"]
    )

    chunk_ids = records["ids"]
    metadatas = records["metadatas"] or []

    # 4. Find the stored PDF filename
    stored_files = {
        metadata["stored_filename"]
        for metadata in metadatas
        if metadata and metadata.get("stored_filename")
    }

    if len(stored_files) > 1:
        raise ValueError("Conflicting stored filenames")

    stored_filename = next(iter(stored_files), None)

    file_path = None

    if stored_filename:
        if not re.fullmatch(r"[0-9a-f]{32}\.pdf", stored_filename):
            raise ValueError("Invalid stored filename")

        file_path = Path("uploads") / stored_filename

    # 5. Remove vectors from ChromaDB
    if chunk_ids:
        vector_db.delete(ids=chunk_ids)

    # 6. Remove the physical PDF
    if file_path is not None:
        file_path.unlink(missing_ok=True)

    # 7. Remove SQLite metadata
    deleted = delete_document(document_id)

    if not deleted:
        raise RuntimeError("SQLite record deletion failed")

    return True
