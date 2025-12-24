from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from pathlib import Path

load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini")

DB_DIR = "chroma_db"
METADATA_FILE = "pdf_metadata.json"

# ===== Metadata Management =====
def load_metadata():
    """Load PDF metadata from JSON file"""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    """Save PDF metadata to JSON file"""
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

def add_pdf_metadata(filename, num_chunks):
    """Add metadata for a newly ingested PDF"""
    metadata = load_metadata()
    metadata[filename] = {
        'filename': filename,
        'uploaded_at': datetime.now().isoformat(),
        'num_chunks': num_chunks,
        'status': 'processed'
    }
    save_metadata(metadata)
    return metadata[filename]

def get_all_pdfs():
    """Get list of all processed PDFs"""
    metadata = load_metadata()
    return list(metadata.values())

def delete_pdf_metadata(filename):
    """Remove PDF metadata"""
    metadata = load_metadata()
    if filename in metadata:
        del metadata[filename]
        save_metadata(metadata)
        return True
    return False

# ===== PDF Ingestion =====
def ingest_pdf(path):
    """
    Ingest a PDF file into the vector database with metadata tracking
    """
    filename = os.path.basename(path)
    
    # Load and split PDF
    loader = PyPDFLoader(path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)
    
    # Add source metadata to each chunk
    for chunk in chunks:
        chunk.metadata['source_file'] = filename
        chunk.metadata['ingested_at'] = datetime.now().isoformat()

    # Check if vector store exists
    if os.path.exists(DB_DIR):
        # Add to existing vector store
        vector_store = Chroma(
            persist_directory=DB_DIR,
            embedding_function=OpenAIEmbeddings()
        )
        vector_store.add_documents(chunks)
    else:
        # Create new vector store
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=OpenAIEmbeddings(),
            persist_directory=DB_DIR
        )

    # Save metadata
    pdf_metadata = add_pdf_metadata(filename, len(chunks))
    
    total_count = vector_store._collection.count()
    print(f"✅ PDF '{filename}' ingested with {len(chunks)} chunks")
    print(f"📊 Total embeddings in database: {total_count}")
    
    return pdf_metadata

# ===== Question Answering =====
def ask_question(question):
    """
    Answer a question using the vector database
    """
    # Check if database exists
    if not os.path.exists(DB_DIR):
        return type('obj', (object,), {
            'content': 'No PDFs have been uploaded yet. Please upload a PDF first.'
        })()
    
    db = Chroma(
        persist_directory=DB_DIR,
        embedding_function=OpenAIEmbeddings()
    )

    # Retrieve relevant documents
    docs = db.similarity_search(question, k=5)

    if not docs:
        return type('obj', (object,), {
            'content': 'No relevant information found in the uploaded documents.'
        })()

    print("📄 Retrieved documents:")
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get('source_file', 'unknown')
        print(f"  {i}. From: {source}")
    
    relevant_docs = "\n".join(d.page_content for d in docs)

    query_template = f"""
        ## 📝 Question and Context Analysis

        ### ❓ User Query:
        {question}

        ### 📄 Relevant Information (Context):
        {relevant_docs}

        ---

        ## 🎯 Instructions for Response Generation
        
        1.  **When user greets, give response or greet according to that**
        2.  **Extract the Answer:** You **must** attempt to answer the **User Query** using **ONLY** the information provided in the **Relevant Information (Context)** section.
        3.  **Strict Constraint:** If, after careful review, you cannot find the answer within the provided context, **DO NOT** use external knowledge or your own information.
        4.  **No Answer Found:** In the event that the answer is not present in the context, your entire response must be the exact phrase: **'answer not found'**
    """

    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=query_template)
    ]

    result = model.invoke(messages)
    return result

# ===== PDF Management =====
def list_pdfs():
    """List all processed PDFs with metadata"""
    return get_all_pdfs()

def delete_pdf(filename):
    """
    Delete a PDF from the system (metadata only - vector store cleanup would require rebuilding)
    Note: This is a simplified version. Full implementation would rebuild the vector store.
    """
    success = delete_pdf_metadata(filename)
    
    if success:
        print(f"✅ Metadata for '{filename}' removed")
        print("⚠️  Note: Vector embeddings remain in database. Consider rebuilding for complete removal.")
    
    return success

def get_database_stats():
    """Get statistics about the vector database"""
    if not os.path.exists(DB_DIR):
        return {
            'total_embeddings': 0,
            'total_pdfs': 0,
            'database_exists': False
        }
    
    db = Chroma(
        persist_directory=DB_DIR,
        embedding_function=OpenAIEmbeddings()
    )
    
    metadata = load_metadata()
    
    return {
        'total_embeddings': db._collection.count(),
        'total_pdfs': len(metadata),
        'database_exists': True,
        'pdfs': list(metadata.values())
    }
