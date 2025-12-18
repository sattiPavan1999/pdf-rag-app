from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from rag import ingest_pdf, ask_question
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile):
    file_path = f"uploads/current.pdf"

    contents = await file.read()

    if not contents:
        return {"error": "Uploaded file is empty"}

    with open(file_path, "wb") as f:
        f.write(contents)

    print("Saved file size:", os.path.getsize(file_path))

    ingest_pdf(file_path)
    return {"message": "PDF processed"}


@app.post("/ask")
def ask(data: QuestionRequest):
    answer = ask_question(data.question)

    return {"answer": answer.content}


app.mount("/ui", StaticFiles(directory="../frontend", html=True), name="frontend")