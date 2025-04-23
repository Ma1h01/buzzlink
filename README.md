# BuzzLink
BuzzLink is a conversational search application designed to help Georgia Tech students discover alumni profiles by field, company, or location. It leverages FastAPI for its backend, LangChain and LangGraph for conversational AI and retrieval, Qdrant as a vector database, and a React-based frontend for an intuitive chat interface.

## Features
- **Natural Language Search**: Ask questions like "Find alumni in software engineering" or "Show GT graduates at Google".
- **Profile Retrieval**: Returns relevant alumni profiles with names, headlines, summaries, and profile images.
- **Extensible Architecture**: Easily adapt to other datasets or vector stores.

## Environment Variables
Create a `.env` file in `backend/` with the following:

```env
OPENAI_API_KEY
LANGSMITH_API_KEY
QDRANT_URL
QDRANT_API_KEY
NOMIC_API_KEY
```  

Create a `.env` file in `frontend/` with the following:

```env
VITE_BACKEND_API_URL
VITE_LOCAL_BACKEND_API_URL
```

## Backend Setup and Run
1. Navigate to the server directory:
   ```sh
   cd backend
   ```
2. Install Python dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Start the FastAPI server:
   ```sh
   python main.py
   ```

## Frontend Setup and Run
1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```
2. Install JavaScript dependencies:
   ```sh
   npm install
   ```
3. Launch the development server:
   ```sh
   npm run dev
   ```
* If you want to access the deployed backend, change line `28` in `src/api/chat.ts` to the deployed backend URL: `VITE_BACKEND_API_URL`.

## Usage
- Open your browser to the frontend URL.
- Enter queries in the chat box, such as:
  - "Find alumni who worked at Amazon."
  - "Show me GT graduates in May 2024."
- The response panel will display a summary of results and clickable profile cards.
