# PDF RAG Application

A modern, AI-powered PDF question-answering system using Retrieval-Augmented Generation (RAG). Upload PDF documents and ask questions about their content using OpenAI's GPT-4o-mini.

## ✨ Features

- 🎨 **Modern UI** - Beautiful dark theme with glassmorphism and smooth animations
- 📄 **Multi-PDF Support** - Upload and manage multiple PDF documents
- 💬 **Intelligent Q&A** - Ask questions and get accurate answers from your documents
- 💾 **Conversation History** - Persistent chat history using localStorage
- 🔍 **Semantic Search** - Advanced vector-based document retrieval
- 🐳 **Docker Ready** - Full containerization support for easy deployment
- 🧪 **Comprehensive Tests** - Unit and integration tests with pytest
- 📊 **Logging & Monitoring** - Production-ready logging system

## 🏗️ Architecture

```
pdf-rag-app/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── rag.py           # RAG logic & vector DB
│   └── uploads/         # Uploaded PDFs
├── frontend/            # Vanilla JS frontend
│   ├── index.html       # UI structure
│   ├── style.css        # Modern styling
│   └── app.js           # Frontend logic
├── tests/               # Test suite
├── Dockerfile           # Container configuration
└── docker-compose.yml   # Multi-container setup
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- (Optional) Docker & Docker Compose

### Local Development

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd pdf-rag-app-5
   ```

2. **Create virtual environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp env.template .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Start backend**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

6. **Open frontend**
   - Open `frontend/index.html` in your browser
   - Or visit `http://localhost:8000/ui`

### Docker Deployment

1. **Configure environment**
   ```bash
   cp env.template .env
   # Add your OPENAI_API_KEY to .env
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

📊 Useful Commands
bash
# View container status
docker-compose ps
# View logs
docker-compose logs -f backend
# Stop containers (keeps data)
docker-compose stop
# Start again
docker-compose start
# Stop and remove (keeps data in volumes)
docker-compose down
# Rebuild after code changes
docker-compose up -d --build


3. **Access the application**
   - Frontend: `http://localhost`
   - API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/stats` | Database statistics |
| POST | `/upload-pdf` | Upload PDF file |
| POST | `/ask` | Ask question |
| GET | `/pdfs` | List uploaded PDFs |
| DELETE | `/pdfs/{filename}` | Delete PDF |

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern web framework
- **LangChain** - LLM orchestration
- **ChromaDB** - Vector database
- **OpenAI** - GPT-4o-mini for Q&A
- **PyPDF** - PDF processing

### Frontend
- **Vanilla JavaScript** - No framework overhead
- **Modern CSS** - Dark theme with animations
- **LocalStorage** - Client-side persistence

### DevOps
- **Docker** - Containerization
- **Nginx** - Reverse proxy
- **GitHub Actions** - CI/CD pipeline
- **Pytest** - Testing framework

## 📝 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_api_key_here

# Optional
APP_ENV=development
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### RAG Configuration

Edit `backend/rag.py` to customize:
- `chunk_size`: Text chunk size (default: 800)
- `chunk_overlap`: Overlap between chunks (default: 100)
- `k`: Number of similar chunks to retrieve (default: 5)

## 🎨 UI Features

- **Drag & Drop** - Upload PDFs by dragging
- **Real-time Status** - Loading indicators and status messages
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Dark Theme** - Easy on the eyes
- **Smooth Animations** - Polished user experience

## 🔒 Security

- Input validation on all endpoints
- File type and size restrictions
- CORS configuration
- Security headers (X-Frame-Options, etc.)
- Environment variable protection

## 📊 Monitoring

The application includes comprehensive logging:

```python
# Logs include:
- API requests and responses
- PDF processing status
- Error tracking
- Database operations
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/`
5. Submit a pull request

## 📄 License

MIT License - feel free to use this project for learning or production.

## 🐛 Troubleshooting

### Common Issues

**Issue**: "No PDFs have been uploaded yet"
- **Solution**: Upload a PDF first before asking questions

**Issue**: "Upload failed"
- **Solution**: Check file is valid PDF and under 10MB

**Issue**: "answer not found"
- **Solution**: Question may not be answerable from PDF content

### Logs

Check backend logs for detailed error information:
```bash
# Docker
docker-compose logs backend

# Local
# Logs appear in terminal where uvicorn is running
```

## 🎯 Roadmap

- [ ] Add conversation export (PDF/JSON)
- [ ] Support for more document types (DOCX, TXT)
- [ ] Multi-language support
- [ ] User authentication
- [ ] Cloud deployment guides (AWS, GCP, Azure)
- [ ] Advanced RAG techniques (HyDE, Multi-query)

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/docs`

---

Built with ❤️ using FastAPI, LangChain, and OpenAI
