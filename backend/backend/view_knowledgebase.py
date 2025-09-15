import os
import pprint

from langchain_chroma import Chroma
from backend.knowledgebase import embeddings


def view_documents(limit: int = 5):
    """
    Connects to the ChromaDB vector store and prints a sample of documents.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    persist_dir = os.path.join(current_dir, "../chroma_db")

    if not os.path.exists(persist_dir):
        print("Knowledge base (ChromaDB) not found. Please run the sync script first.")
        return

    print("Connecting to the knowledge base...")
    vectorstore = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
    )

    total_docs = vectorstore._collection.count()
    print(f"Found {total_docs} documents in the knowledge base.")
    
    if total_docs == 0:
        return

    limit = min(limit, total_docs)
    print(f"Showing metadata for the first {limit} documents:\n")

    # The get() method retrieves documents and their metadata.
    results = vectorstore.get(limit=limit)

    # Use pprint for readable output of the metadata
    pprint.pprint(results.get("metadatas"))


if __name__ == "__main__":
    # You can change the limit here if you want to see more documents
    view_documents(limit=5)
