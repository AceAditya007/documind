
import pymupdf
from pathlib import Path


# Step 1: Extract text from PDF
def extract_text_from_pdf(file_path: str) -> str:
    extracted_text = []

    with pymupdf.open(file_path) as pdf:
        for page in pdf:
            page_text = page.get_text("text")
            extracted_text.append(page_text)

    return "\n".join(extracted_text)


# Step 2: Split text into chunks
def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])

        if end >= len(text):
            break

        start = end - overlap

    return chunks


# Step 3: Run and test
if __name__ == "__main__":
    pdf_files = list(Path("uploads").glob("*.pdf"))

    if not pdf_files:
        print("No uploaded PDFs found.")
    else:
        text = extract_text_from_pdf(str(pdf_files[0]))

        chunks = chunk_text(text)

        print("Total chunks:", len(chunks))
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i + 1}: {len(chunk)} characters")
        print("\nFirst chunk:")
        print(chunks[0])

def extract_pages_from_pdf(file_path):
    pages = []

    with pymupdf.open(file_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text")

            if text.strip():
                pages.append({
                    "page": page_number,
                    "text": text
                })

    return pages
