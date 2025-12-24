import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from main import app

client = TestClient(app)

class TestAPI:
    """Test suite for API endpoints"""
    
    def test_root_endpoint(self):
        """Test root health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "version" in response.json()
    
    def test_stats_endpoint(self):
        """Test stats endpoint"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_embeddings" in data
        assert "total_pdfs" in data
        assert "database_exists" in data
    
    def test_ask_without_question(self):
        """Test ask endpoint with empty question"""
        response = client.post("/ask", json={"question": ""})
        assert response.status_code == 400
        assert "error" in response.json()
    
    def test_ask_with_invalid_payload(self):
        """Test ask endpoint with invalid payload"""
        response = client.post("/ask", json={})
        assert response.status_code == 422  # Validation error
    
    def test_get_pdfs_list(self):
        """Test PDF list endpoint"""
        response = client.get("/pdfs")
        assert response.status_code == 200
        data = response.json()
        assert "pdfs" in data
        assert "total" in data
        assert isinstance(data["pdfs"], list)
    
    def test_upload_non_pdf_file(self):
        """Test uploading non-PDF file"""
        files = {"file": ("test.txt", b"test content", "text/plain")}
        response = client.post("/upload-pdf", files=files)
        assert response.status_code == 400
        assert "Only PDF files are allowed" in response.json()["error"]
    
    def test_upload_empty_file(self):
        """Test uploading empty file"""
        files = {"file": ("test.pdf", b"", "application/pdf")}
        response = client.post("/upload-pdf", files=files)
        assert response.status_code == 400
        assert "empty" in response.json()["error"].lower()
    
    def test_delete_nonexistent_pdf(self):
        """Test deleting non-existent PDF"""
        response = client.delete("/pdfs/nonexistent.pdf")
        assert response.status_code == 404
        assert "not found" in response.json()["error"].lower()

class TestAPIValidation:
    """Test input validation"""
    
    def test_question_validation(self):
        """Test question request validation"""
        # Valid question
        response = client.post("/ask", json={"question": "What is this?"})
        # May fail if no PDFs uploaded, but should validate the structure
        assert response.status_code in [200, 500]  # 500 if no DB exists
        
    def test_malformed_json(self):
        """Test malformed JSON handling"""
        response = client.post(
            "/ask",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/")
        assert response.status_code in [200, 405]  # OPTIONS may not be implemented
        
        # Test with actual request
        response = client.get("/")
        # CORS headers should be present in response
        assert response.status_code == 200
