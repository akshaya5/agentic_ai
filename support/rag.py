import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
import os
from pypdf import PdfReader

client = chromadb.PersistentClient(path="./chroma_db")

embbeding_fn = DefaultEmbeddingFunction()
collection = client.get_or_create_collection(
    name="coolbreeze_docs",
    embedding_function=embbeding_fn
)


def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks=[]
    current_chunk =[]
    current_size = 0

    for word in words:
        current_chunk.append(word)
        current_size += len(word) +1

        if current_size >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk=[]
            current_size=0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def load_documents():
    doc_path= "support/documents/"

    documents=[]
    ids=[]

    for filename in os.listdir(doc_path):
        if filename.endswith(".pdf"):
            file = os.path.join(doc_path, filename)
            reader = PdfReader(file)

            full_text =""
            for text in reader.pages:
                full_text += text.extract_text()

            chunks = chunk_text(full_text, 500)
            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                ids.append(f"#{filename}_#{i}")

    if documents:
        collection.add(documents=documents, ids=ids)

    print(f"Loaded #{len(documents)} in db")

def search_knowledge_base(query):
    results = collection.query(query_texts=[query], n_results=3)

    if not results["documents"][0]:
        return "No relevant information found in compant document"

    matched_chunks = results["documents"][0]
    return "\n\n".join(matched_chunks)