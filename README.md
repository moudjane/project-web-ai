# Project Web AI

A full-stack AI chat application with Vue.js frontend and Python backend.

## Prerequisites

- Node.js (for frontend)
- Docker & Docker Compose (for backend)
- Mistral AI API key
- Firebase API key (for frontend)

## Setup

### Backend

1. Navigate to the backend folder:
   ```bash
   cd back
   ```

2. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and add your Mistral API key:
   ```
   MISTRAL_API_KEY=your-actual-key-here
   DB_CONNECTION_STRING=postgresql+psycopg://langchain:langchain@db:5432/langchain
   ```

4. Launch the backend with Docker:
   ```bash
   docker compose up
   ```

### Frontend

1. Navigate to the frontend folder:
   ```bash
   cd front
   ```

2. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and add your API keys:
   ```
   VITE_MISTRAL_API_KEY=your-actual-mistral-key-here
   VITE_FIREBASE_API_KEY=your-actual-firebase-key-here
   ```

4. Install dependencies:
   ```bash
   npm install
   ```

5. Launch the frontend development server:
   ```bash
   npm run dev
   ```
   
   Or alternatively:
   ```bash
   npm run start
   ```

## Access

Once both services are running, open your browser and navigate to the URL displayed by the frontend development server (typically `http://localhost:5173`).
