import pytest
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

@pytest.fixture
def sample_question():
    """Sample question for testing"""
    return "What is the main topic?"

@pytest.fixture
def sample_pdf_path():
    """Path to a sample PDF for testing"""
    return "tests/fixtures/sample.pdf"

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    class MockResponse:
        def __init__(self):
            self.content = "This is a test answer"
    return MockResponse()

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Cleanup test files after each test"""
    yield
    # Cleanup logic here if needed
    test_db = "test_chroma_db"
    if os.path.exists(test_db):
        import shutil
        shutil.rmtree(test_db)
