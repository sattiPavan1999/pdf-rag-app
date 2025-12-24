from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from rag import ingest_pdf, ask_question, list_pdfs, delete_pdf, get_database_stats
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="PDF RAG API",
    description="AI-powered PDF question answering system",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ===== Request/Response Models =====
class QuestionRequest(BaseModel):
    question: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "What is the main topic of the document?"
                }
            ]
        }
    }

class QuestionResponse(BaseModel):
    answer: str
    
class UploadResponse(BaseModel):
    message: str
    filename: str
    num_chunks: int
    
class PDFListResponse(BaseModel):
    pdfs: list
    total: int

class StatsResponse(BaseModel):
    total_embeddings: int
    total_pdfs: int
    database_exists: bool

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

# ===== Endpoints =====

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "PDF RAG API is running",
        "version": "2.0.0"
    }

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get database statistics"""
    try:
        stats = get_database_stats()
        logger.info(f"Stats requested: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile):
    """
    Upload and process a PDF file
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        
        # Validate file size (10MB limit)
        contents = await file.read()
        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )
        
        file_size = len(contents)
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds 10MB limit (got {file_size / 1024 / 1024:.2f}MB)"
            )
        
        # Ensure uploads directory exists
        os.makedirs("uploads", exist_ok=True)
        
        # Save file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(contents)
        
        logger.info(f"Saved file: {file.filename} ({file_size} bytes)")
        
        # Process PDF
        metadata = ingest_pdf(file_path)
        
        logger.info(f"Successfully processed: {file.filename}")
        
        return UploadResponse(
            message="PDF processed successfully",
            filename=file.filename,
            num_chunks=metadata['num_chunks']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(e)}"
        )

@app.post("/ask", response_model=QuestionResponse)
async def ask(data: QuestionRequest):
    """
    Ask a question about uploaded PDFs
    """
    try:
        # Validate question
        if not data.question or not data.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )
        
        logger.info(f"Question received: {data.question}")
        
        # Get answer
        result = ask_question(data.question)
        
        logger.info(f"Answer generated: {result.content[:100]}...")
        
        return QuestionResponse(answer=result.content)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to answer question: {str(e)}"
        )

@app.get("/pdfs", response_model=PDFListResponse)
async def get_pdfs():
    """
    Get list of all uploaded PDFs
    """
    try:
        pdfs = list_pdfs()
        logger.info(f"PDF list requested: {len(pdfs)} PDFs")
        return PDFListResponse(
            pdfs=pdfs,
            total=len(pdfs)
        )
    except Exception as e:
        logger.error(f"Error listing PDFs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list PDFs: {str(e)}"
        )

@app.delete("/pdfs/{filename}")
async def delete_pdf_endpoint(filename: str):
    """
    Delete a PDF from the system
    """
    try:
        success = delete_pdf(filename)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"PDF '{filename}' not found"
            )
        
        # Optionally delete the physical file
        file_path = f"uploads/{filename}"
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
        
        logger.info(f"PDF deleted: {filename}")
        
        return {
            "message": f"PDF '{filename}' deleted successfully",
            "filename": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete PDF: {str(e)}"
        )

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Mount frontend (optional - for serving UI from backend)
# Only mount if frontend directory exists (to avoid issues during testing)
frontend_dir = "../frontend"
if os.path.exists(frontend_dir):
    app.mount("/ui", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)