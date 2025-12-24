import pytest
import os
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

class TestRAGFunctions:
    """Test RAG module functions"""
    
    def test_metadata_operations(self):
        """Test metadata save and load operations"""
        from rag import save_metadata, load_metadata
        
        test_metadata = {
            "test.pdf": {
                "filename": "test.pdf",
                "uploaded_at": "2024-01-01T00:00:00",
                "num_chunks": 10,
                "status": "processed"
            }
        }
        
        # Save metadata
        save_metadata(test_metadata)
        
        # Load and verify
        loaded = load_metadata()
        assert "test.pdf" in loaded
        assert loaded["test.pdf"]["num_chunks"] == 10
        
        # Cleanup
        if os.path.exists("pdf_metadata.json"):
            os.remove("pdf_metadata.json")
    
    def test_add_pdf_metadata(self):
        """Test adding PDF metadata"""
        from rag import add_pdf_metadata, load_metadata
        
        metadata = add_pdf_metadata("test.pdf", 15)
        
        assert metadata["filename"] == "test.pdf"
        assert metadata["num_chunks"] == 15
        assert metadata["status"] == "processed"
        assert "uploaded_at" in metadata
        
        # Verify it was saved
        loaded = load_metadata()
        assert "test.pdf" in loaded
        
        # Cleanup
        if os.path.exists("pdf_metadata.json"):
            os.remove("pdf_metadata.json")
    
    def test_delete_pdf_metadata(self):
        """Test deleting PDF metadata"""
        from rag import add_pdf_metadata, delete_pdf_metadata, load_metadata
        
        # Add metadata
        add_pdf_metadata("test.pdf", 10)
        
        # Delete it
        success = delete_pdf_metadata("test.pdf")
        assert success == True
        
        # Verify deletion
        loaded = load_metadata()
        assert "test.pdf" not in loaded
        
        # Try deleting non-existent
        success = delete_pdf_metadata("nonexistent.pdf")
        assert success == False
        
        # Cleanup
        if os.path.exists("pdf_metadata.json"):
            os.remove("pdf_metadata.json")
    
    def test_get_all_pdfs(self):
        """Test getting all PDFs"""
        from rag import add_pdf_metadata, get_all_pdfs
        
        # Add some PDFs
        add_pdf_metadata("test1.pdf", 10)
        add_pdf_metadata("test2.pdf", 20)
        
        pdfs = get_all_pdfs()
        assert len(pdfs) == 2
        assert any(pdf["filename"] == "test1.pdf" for pdf in pdfs)
        assert any(pdf["filename"] == "test2.pdf" for pdf in pdfs)
        
        # Cleanup
        if os.path.exists("pdf_metadata.json"):
            os.remove("pdf_metadata.json")
    
    @patch('rag.Chroma')
    @patch('rag.OpenAIEmbeddings')
    def test_get_database_stats_no_db(self, mock_embeddings, mock_chroma):
        """Test database stats when no database exists"""
        from rag import get_database_stats
        
        # Ensure no database exists
        if os.path.exists("chroma_db"):
            import shutil
            shutil.rmtree("chroma_db")
        
        stats = get_database_stats()
        assert stats["total_embeddings"] == 0
        assert stats["total_pdfs"] == 0
        assert stats["database_exists"] == False
    
    @patch('rag.ChatOpenAI')
    @patch('rag.Chroma')
    @patch('rag.OpenAIEmbeddings')
    def test_ask_question_no_database(self, mock_embeddings, mock_chroma, mock_chat):
        """Test asking question when no database exists"""
        from rag import ask_question
        
        # Ensure no database exists
        if os.path.exists("chroma_db"):
            import shutil
            shutil.rmtree("chroma_db")
        
        result = ask_question("What is this?")
        assert "No PDFs have been uploaded" in result.content
    
    @patch('rag.model')
    @patch('rag.Chroma')
    @patch('rag.OpenAIEmbeddings')
    def test_ask_question_with_results(self, mock_embeddings, mock_chroma_class, mock_model):
        """Test asking question with mock results"""
        from rag import ask_question
        
        # Create mock document
        mock_doc = Mock()
        mock_doc.page_content = "This is test content"
        mock_doc.metadata = {"source_file": "test.pdf"}
        
        # Mock Chroma instance
        mock_chroma_instance = Mock()
        mock_chroma_instance.similarity_search.return_value = [mock_doc]
        mock_chroma_class.return_value = mock_chroma_instance
        
        # Mock model response
        mock_response = Mock()
        mock_response.content = "This is a test answer"
        mock_model.invoke.return_value = mock_response
        
        # Create fake database directory
        os.makedirs("chroma_db", exist_ok=True)
        
        try:
            result = ask_question("What is this?")
            # Verify the mock was called
            assert mock_model.invoke.called
            assert result.content == "This is a test answer"
        finally:
            # Cleanup
            if os.path.exists("chroma_db"):
                import shutil
                shutil.rmtree("chroma_db")

class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_list_pdfs(self):
        """Test listing PDFs"""
        from rag import add_pdf_metadata, list_pdfs
        
        add_pdf_metadata("test.pdf", 10)
        pdfs = list_pdfs()
        
        assert len(pdfs) >= 1
        assert isinstance(pdfs, list)
        
        # Cleanup
        if os.path.exists("pdf_metadata.json"):
            os.remove("pdf_metadata.json")
    
    def test_delete_pdf(self):
        """Test delete PDF function"""
        from rag import add_pdf_metadata, delete_pdf
        
        add_pdf_metadata("test.pdf", 10)
        success = delete_pdf("test.pdf")
        
        assert success == True
        
        # Cleanup
        if os.path.exists("pdf_metadata.json"):
            os.remove("pdf_metadata.json")
