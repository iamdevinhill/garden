# Garden Tracker Application

A gardening tracking application that uses Ollama Llama2 for plant knowledge, FastAPI for the backend, and Streamlit for the frontend.

## Prerequisites

- Docker and Docker Compose installed
- At least 8GB of RAM (for Ollama)

## Deployment

1. Clone the repository:
```bash
git clone <repository-url>
cd garden-tracker
```

2. Start the application using Docker Compose:
```bash
docker-compose up --build
```

This will start three services:
- Frontend (Streamlit) on http://localhost:8501
- Backend (FastAPI) on http://localhost:8000
- Ollama service on http://localhost:11434

3. Pull the Llama2 model (first time only):
```bash
docker exec -it garden-tracker-ollama-1 ollama pull llama2
```

## Usage

1. Open your browser and navigate to http://localhost:8501
2. Use the form to add new plants with their details
3. The application will automatically query Ollama for harvest information
4. View your plants and their harvest information in the list below the form

## Development

To run the application locally without Docker:

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start Ollama:
```bash
ollama serve
```

3. In a separate terminal, start the backend:
```bash
cd backend
uvicorn main:app --reload
```

4. In another terminal, start the frontend:
```bash
cd frontend
streamlit run app.py
```

## Architecture

- **Frontend**: Streamlit application for user interface
- **Backend**: FastAPI application handling plant data and Ollama integration
- **Ollama**: Local LLM service providing plant knowledge using Llama2 model

## Environment Variables

- `OLLAMA_HOST`: Hostname of the Ollama service (default: localhost)
- `API_URL`: URL of the backend API (default: http://localhost:8000) 