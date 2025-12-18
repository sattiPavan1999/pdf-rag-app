from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import shutil
import os

load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini")

DB_DIR = "chroma_db"

def ingest_pdf(path):

    loader = PyPDFLoader(path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)

    vector_store = Chroma.from_documents(
        chunks,
        OpenAIEmbeddings(),
        persist_directory=DB_DIR
    )
    print(f"✅ Vector DB created with {vector_store._collection.count()} embeddings")

def ask_question(question):
    db = Chroma(
        persist_directory=DB_DIR,
        embedding_function=OpenAIEmbeddings()
    )

    docs = db.similarity_search(question, k=5)

    print("docs: \n", docs)
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
