
from pathlib import Path
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from pdf_processor import (
    extract_text_from_pdf,
    chunk_text
)

# Step 1: Find uploaded PDF
pdf_files = list(Path("uploads").glob("*.pdf"))

if not pdf_files:
    raise FileNotFoundError("No PDF found")

pdf_path = pdf_files[0]

# Step 2: Extract text
text = extract_text_from_pdf(str(pdf_path))

# Step 3: Split into chunks
chunks = chunk_text(text)

print("Total chunks:", len(chunks))

# Step 4: Create embedding model
embeddings = OllamaEmbeddings(model="all-minilm")

# Step 5: Create persistent vector database
vector_db = Chroma(
    collection_name="documind",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# Step 6: Store chunks, avoiding repeat insertion
ids = [f"demo_chunk_{i}" for i in range(len(chunks))]

vector_db.delete(ids=ids) if vector_db.get(ids=ids)["ids"] else None

vector_db.add_texts(
    texts=chunks,
    ids=ids
)

print("Chunks indexed successfully!")

# Step 7: Search by meaning
question = "What programming languages does Aditya know?"

results = vector_db.similarity_search(
    question,
    k=2
)

print("\nMost relevant chunks:")

for i, doc in enumerate(results):
    print(f"\nResult {i + 1}:")
    print(doc.page_content[:500])

vector_db = Chroma(
    collection_name="documind_v2",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)