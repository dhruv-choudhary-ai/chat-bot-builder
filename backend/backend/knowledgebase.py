# knowledgebase.py
import os
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document as LangchainDocument
from typing import List

from backend.connectors.models import Document, TextSection

# ----------------------------
# Paths
# ----------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
faq_path = os.path.join(current_dir, "uploaded_docs/FAQ.txt")
upload_dir = os.path.join(current_dir, "uploaded_docs")

os.makedirs(upload_dir, exist_ok=True)

# ----------------------------
# Initialize embeddings
# ----------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="thenlper/gte-small",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

def convert_to_langchain_documents(documents: List[Document]) -> List[LangchainDocument]:
    """Converts a list of custom Document objects to Langchain's Document objects."""
    langchain_docs = []
    for doc in documents:
        page_content = ""
        for section in doc.sections:
            if isinstance(section, TextSection):
                page_content += section.text + "\n\n"
        
        metadata = doc.metadata.copy()
        # Convert any list values in metadata to comma-separated strings for ChromaDB
        for key, value in metadata.items():
            if isinstance(value, list):
                metadata[key] = ", ".join(map(str, value))

        metadata["source"] = doc.source.value
        metadata["doc_id"] = doc.id
        metadata["semantic_identifier"] = doc.semantic_identifier
        if doc.doc_updated_at:
            metadata["doc_updated_at"] = doc.doc_updated_at.isoformat()

        langchain_docs.append(
            LangchainDocument(page_content=page_content.strip(), metadata=metadata)
        )
    return langchain_docs

def add_documents_to_knowledge_base(documents: List[Document], persist_directory: str = None):
    """
    Adds a list of documents to the Chroma vector store.
    """
    if not documents:
        print("No documents to add to the knowledge base.")
        return

    langchain_docs = convert_to_langchain_documents(documents)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    document_chunks = text_splitter.split_documents(langchain_docs)

    if not document_chunks:
        print("No document chunks to add to the knowledge base.")
        return

    if persist_directory is None:
        persist_directory = os.path.join(current_dir, "chroma_db")

    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )
    vectorstore.add_documents(document_chunks)
    print(f"✅ Knowledgebase updated with {len(documents)} documents.")


def update_knowledge_base(persist_directory: str = None):
    """
    Loads all documents from the uploaded_docs directory, splits them into chunks,
    and updates the Chroma vector store.
    """
    documents = []
    if os.path.exists(faq_path):
        faq_loader = TextLoader(faq_path, encoding="utf-8")
        documents.extend(faq_loader.load())

    for file in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, file)
        if file.endswith(".pdf"):
            pdf_loader = PyPDFLoader(file_path)
            documents.extend(pdf_loader.load())
        elif file.endswith(".txt"):
            text_loader = TextLoader(file_path, encoding="utf-8")
            documents.extend(text_loader.load())

    if not documents:
        print("No local documents to update in the knowledge base.")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    document_chunks = text_splitter.split_documents(documents)

    if not document_chunks:
        print("No document chunks to add to the knowledge base.")
        return

    if persist_directory is None:
        persist_directory = os.path.join(current_dir, "../chroma_db")

    # Initialize from directory to add to existing DB
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )
    vectorstore.add_documents(document_chunks)
    print("✅ Knowledgebase updated with FAQ + uploaded documents.")

# Initial update when the application starts
# update_knowledge_base()
