# Garden Tracker Application

A gardening tracking application that uses Ollama Llama3.2 for plant knowledge, FastAPI for the backend, and Streamlit for the frontend. The application helps gardeners track their plants and provides AI-powered harvest information.

## Features

- Add and track plants with their details (name, species, planting date, location)
- AI-powered harvest information using Ollama Llama3.2
- Interactive web interface with Streamlit
- RESTful API backend with FastAPI
- Neo4j database integration for storing plant data and user interactions
- Docker containerization for easy deployment

## Prerequisites

- Docker and Docker Compose installed
- At least 8GB of RAM (for Ollama)
- Neo4j database (included in Docker setup)

## Deployment

1. Clone the repository:
```bash
git clone <repository-url>
cd garden
```

2. Start the application using Docker Compose:
```bash
docker-compose up --build
```

This will start four services:
- Frontend (Streamlit) on http://localhost:8501
- Backend (FastAPI) on http://localhost:8000
- Ollama service on http://localhost:11434
- Neo4j database on http://localhost:7474

3. Pull the Llama3.2 model (first time only):
```bash
docker exec -it garden-tracker-ollama-1 ollama pull llama3.2
```

## Usage

1. Open your browser and navigate to http://localhost:8501
2. Use the form to add new plants with their details:
   - Plant Name
   - Species
   - Date Planted
   - Location
3. The application will automatically query Ollama for harvest information
4. View your plants and their harvest information in the expandable list below the form
5. Delete plants using the delete button in each plant's card


## Architecture

- **Frontend**: Streamlit application providing an intuitive user interface for plant management
- **Backend**: FastAPI application handling:
  - Plant CRUD operations
  - Ollama integration for harvest information
  - Neo4j database integration
- **Ollama**: Local LLM service providing plant knowledge using Llama3.2 model
- **Neo4j**: Graph database storing plant data and user interactions

## Environment Variables

- `OLLAMA_HOST`: Hostname of the Ollama service (default: localhost)
- `API_URL`: URL of the backend API (default: http://localhost:8000)
- `NEO4J_URI`: Neo4j database connection URI
- `NEO4J_USER`: Neo4j database username
- `NEO4J_PASSWORD`: Neo4j database password

## API Endpoints

- `POST /plants/`: Add a new plant
- `GET /plants/`: Get all plants
- `GET /plants/{plant_id}`: Get a specific plant
- `DELETE /plants/{plant_id}`: Delete a plant
- `GET /interactions/`: Get all user interactions 