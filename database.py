
import sqlite3

def create_table():
    conn = sqlite3.connect("documind.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            status TEXT DEFAULT 'uploaded'
        )
    """)

    conn.commit()
    conn.close()


def add_document(filename):
    conn = sqlite3.connect("documind.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO documents (filename) VALUES (?)",
        (filename,)
    )

    conn.commit()
    document_id = cursor.lastrowid
    conn.close()

    return document_id


def get_documents():
    conn = sqlite3.connect("documind.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents")

    documents = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return documents


def get_document_by_id(document_id):
    conn = sqlite3.connect("documind.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM documents WHERE id = ?",
        (document_id,)
    )

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def delete_document(document_id):
    conn = sqlite3.connect("documind.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM documents WHERE id = ?",
        (document_id,)
    )

    deleted_count = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted_count > 0

def update_document(document_id, filename):
    conn = sqlite3.connect("documind.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE documents SET filename = ? WHERE id = ?",
        (filename, document_id)
    )

    updated_count = cursor.rowcount

    conn.commit()
    conn.close()

    return updated_count > 0
