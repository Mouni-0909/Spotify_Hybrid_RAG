# Spotify Hybrid RAG AI Assistant

## Project Overview

Spotify Hybrid RAG AI Assistant is an AI-powered chatbot developed to answer questions about Spotify's system architecture and technologies.

The application uses Retrieval-Augmented Generation (RAG) to retrieve information from PDF documents and a Neo4j knowledge graph.

It supports three retrieval methods:

1. **Vector RAG** – Retrieves relevant information from PDF documents using FAISS.
2. **Graph RAG** – Retrieves relationships and structured information from Neo4j.
3. **Hybrid RAG** – Combines vector search and knowledge graph retrieval to generate context-based answers.

The application is built using Python, LangChain, FastAPI, Streamlit, FAISS, Neo4j, and OpenAI.

It is deployed using Docker on a Hostinger VPS with a custom domain and HTTPS.

## Live Application

**Website:** https://spotify.mounika-ai.sbs

**GitHub Repository:** https://github.com/Mouni-0909/Spotify_Hybrid_RAG

## Project Objectives

- Build an AI chatbot using Retrieval-Augmented Generation.
- Extract information from Spotify architecture documentation.
- Store document embeddings in a FAISS vector database.
- Use Neo4j to retrieve relationships between system components.
- Implement Vector RAG, Graph RAG, and Hybrid RAG.
- Develop a user-friendly chatbot interface using Streamlit.
- Connect the frontend to a FastAPI backend.
- Containerize and deploy the application using Docker.
- Make the application accessible through a secure public URL.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development |
| LangChain | RAG workflow |
| OpenAI | AI-powered answer generation |
| FAISS | Vector database |
| Neo4j Aura | Knowledge graph database |
| FastAPI | Backend API |
| Streamlit | Frontend user interface |
| Docker | Application containerization |
| Docker Compose | Multi-container management |
| Nginx | Reverse proxy |
| Traefik | HTTPS routing and SSL |
| Hostinger VPS | Cloud hosting |
| GitHub | Version control |

## Application Architecture

The application follows this workflow:

```text
User
 |
 v
Streamlit Frontend
 |
 v
FastAPI Backend
 |
 v
Select Retrieval Mode
 |
 +-----------------------+
 |           |           |
 v           v           v
Vector RAG  Graph RAG   Hybrid RAG
 |           |           |
FAISS       Neo4j       FAISS + Neo4j
 |           |           |
 +-----------+-----------+
             |
             v
         OpenAI LLM
             |
             v
       Generated Answer
             |
             v
      Streamlit Chatbot
```

## Features

### 1. Vector RAG

- Loads Spotify architecture information from a PDF.
- Splits the document into smaller chunks.
- Generates embeddings for the document content.
- Stores embeddings in FAISS.
- Retrieves relevant document information based on user questions.
- Uses the retrieved context to generate answers.

### 2. Graph RAG

- Uses Neo4j Aura as a knowledge graph database.
- Stores relationships between Spotify architecture components.
- Retrieves structured information from the graph.
- Answers questions based on knowledge graph relationships.

### 3. Hybrid RAG

- Combines FAISS vector retrieval and Neo4j graph retrieval.
- Uses both document context and graph relationships.
- Generates answers using the combined retrieved information.

### 4. Streamlit User Interface

- Spotify-inspired dark theme.
- Dropdown to select retrieval mode.
- Frequently asked questions.
- Interactive chatbot.
- Chat history display.
- Clear Chat option.

### 5. FastAPI Backend

- Handles requests from the Streamlit frontend.
- Processes questions using the selected retrieval mode.
- Connects to the RAG components.
- Returns generated answers to the frontend.

## Project Structure

```text
Spotify_Hybrid_RAG/
|
|-- backend/
|   |-- main.py
|
|-- frontend/
|   |-- app.py
|
|-- data/
|   |-- spotify_web_app_architecture.pdf
|
|-- Dockerfile
|-- docker-compose.yml
|-- nginx.conf
|-- requirements.txt
|-- .dockerignore
|-- .gitignore
|-- README.md
```

Additional runtime files and folders include:

- `.env` – Environment variables and credentials.
- `faiss_index/` – Locally stored FAISS vector index.
- `graph_cache/` – Graph-related cache data.

Sensitive credentials and generated runtime data should not be committed to GitHub.

## Local Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/Mouni-0909/Spotify_Hybrid_RAG.git
cd Spotify_Hybrid_RAG
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```bash
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory.

Configure the OpenAI API key and Neo4j connection credentials required by the backend.

Do not upload the `.env` file to GitHub.

### Step 5: Run the FastAPI Backend

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Step 6: Run the Streamlit Frontend

Open another terminal and run:

```bash
streamlit run frontend/app.py
```

The Streamlit application will open in the browser.

The frontend must be configured to communicate with the running FastAPI backend.

## Docker Deployment

The application is containerized using Docker and Docker Compose.

Three services are used:

1. **Backend** – FastAPI application.
2. **Frontend** – Streamlit application.
3. **Nginx** – Reverse proxy.

### Build and Start Containers

```bash
docker compose up -d --build
```

### Check Container Status

```bash
docker compose ps
```

### View Container Logs

```bash
docker compose logs
```

### Stop Containers

```bash
docker compose down
```

The application uses Docker Compose to manage the services.

## Cloud Deployment

The application is deployed on a Hostinger VPS running Ubuntu.

Deployment configuration:

| Component | Configuration |
|---|---|
| Hosting | Hostinger VPS |
| Operating System | Ubuntu |
| Containerization | Docker Compose |
| Backend | FastAPI |
| Frontend | Streamlit |
| Reverse Proxy | Nginx |
| HTTPS Routing | Traefik |
| SSL Certificate | Let's Encrypt |
| Domain | spotify.mounika-ai.sbs |

Traefik routes HTTPS requests to the Spotify Nginx container, which forwards traffic to the Streamlit frontend.

The application is accessible at:

https://spotify.mounika-ai.sbs

## API Endpoint

The FastAPI backend provides an `/ask` endpoint.

**Method:** POST

**Endpoint:**

```text
/ask
```

Example request:

```json
{
  "question": "What database stores user information?",
  "mode": "Hybrid RAG"
}
```

Example response:

```json
{
  "answer": "PostgreSQL stores user information."
}
```

Supported retrieval modes:

- `Vector RAG`
- `Graph RAG`
- `Hybrid RAG`

## Testing and Validation

The application was tested locally and after deployment.

### Test Question

**What database stores user information?**

### Vector RAG Response

```text
PostgreSQL stores user information, including users,
profiles, subscriptions, playlists, and follows.
```

### Graph RAG Response

```text
postgresql STORES users
```

### Hybrid RAG Response

```text
PostgreSQL stores user information.
```

### Deployment Verification

| Test | Result |
|---|---|
| FastAPI Backend | Passed |
| Streamlit Frontend | Passed |
| FAISS Vector Retrieval | Passed |
| Neo4j Graph Retrieval | Passed |
| Hybrid RAG | Passed |
| Docker Containers | Running |
| Custom Domain | Working |
| HTTPS | Working |
| Live Browser Testing | Passed |

All three retrieval modes were successfully tested through the deployed application.

## Challenges and Learning

During this project, I learned how to:

- Implement different RAG retrieval approaches.
- Work with FAISS and Neo4j.
- Integrate a FastAPI backend with Streamlit.
- Manage application credentials using environment variables.
- Build and run Docker containers.
- Deploy a multi-container application on a VPS.
- Configure Nginx and Traefik.
- Connect a custom domain and enable HTTPS.
- Test and troubleshoot an AI application in a cloud environment.

## Future Improvements

- Improve Graph RAG responses using more natural-language generation.
- Expand the knowledge graph with additional relationships.
- Add more architecture documentation.
- Display retrieved sources along with answers.
- Improve error handling and application monitoring.
- Add additional evaluation tests for RAG response quality.

## Conclusion

This project demonstrates the development and deployment of a Hybrid RAG AI Assistant using both vector search and knowledge graph retrieval.

It provides practical experience in Generative AI, LangChain, FAISS, Neo4j, FastAPI, Streamlit, Docker, and cloud deployment.

The application has been successfully deployed on a Hostinger VPS and is accessible through a custom HTTPS domain.

**Live Application:** https://spotify.mounika-ai.sbs

**GitHub:** https://github.com/Mouni-0909/Spotify_Hybrid_RAG
