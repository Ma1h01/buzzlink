from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from typing import List, Optional
from langchain.docstore.document import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.messages import SystemMessage, HumanMessage
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv
from data_processor import preprocess_alumni_profile_with_manual_split

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React dev server
        "http://localhost:8080",  # Additional frontend port
        "http://127.0.0.1:8080"   # Alternative localhost notation
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Authorization", "X-Requested-With"],
    expose_headers=["Content-Type"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Initialize models and vector store
try:
    llm = ChatOpenAI(
        model="gpt-4o-mini-2024-07-18",
        temperature=0
    )
    llm = llm.bind(response_format={
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "A brief summary of the search results"
                },
                "highlights": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key points or findings from the search"
                },
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "relevance": {"type": "string"}
                        }
                    },
                    "description": "List of recommended profiles with relevance explanations"
                }
            },
            "required": ["summary", "highlights", "recommendations"]
        }
    })
except Exception as e:
    print(f"Error initializing ChatOpenAI: {str(e)}")
    raise

try:
    embeddings = OpenAIEmbeddings()
except Exception as e:
    print(f"Error initializing OpenAIEmbeddings: {str(e)}")
    raise

# Initialize Qdrant client
try:
    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
except Exception as e:
    print(f"Error connecting to Qdrant: {str(e)}")
    raise

collection_name = "user_profile_collection_with_splitting"

# Check if collection exists, if not create it and populate with data
try:
    collections = qdrant_client.get_collections()
    if collection_name not in [collection.name for collection in collections.collections]:
        # Create collection with proper configuration for OpenAI embeddings
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1536,  # OpenAI embeddings dimension
                distance=Distance.COSINE
            )
        )
        print(f"Collection '{collection_name}' created successfully!")
        
        # Initialize vector store
        vector_store = QdrantVectorStore(
            client=qdrant_client,
            collection_name=collection_name,
            embedding=embeddings
        )
        
        # Preprocess and add documents
        data_path = os.path.join(os.path.dirname(__file__), "../../data/raw-profile-data/profile_data.json")
        if not os.path.exists(data_path):
            print(f"Warning: Data file not found at {data_path}")
        else:
            documents = preprocess_alumni_profile_with_manual_split(data_path)
            vector_store.add_documents(documents)
            print(f"Added {len(documents)} documents to the vector store")
    else:
        # Collection exists, just initialize the vector store
        vector_store = QdrantVectorStore(
            client=qdrant_client,
            collection_name=collection_name,
            embedding=embeddings
        )
except Exception as e:
    print(f"Error setting up vector store: {str(e)}")
    raise

# Define request/response models
class ChatRequest(BaseModel):
    message: str

class Profile(BaseModel):
    id: str
    name: str
    profile_pic: Optional[str]
    headline: Optional[str]
    summary: Optional[str]
    linkedin_url: Optional[str]

class ChatResponse(BaseModel):
    response: str
    profiles: List[Profile]

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Search for relevant profiles
        docs = vector_store.similarity_search(request.message, k=5)
        
        if not docs:
            return ChatResponse(
                response=json.dumps({
                    "summary": "No matching profiles found.",
                    "highlights": ["No results found for your query."],
                    "recommendations": []
                }),
                profiles=[]
            )
        
        # Extract unique profiles
        profiles = []
        seen_ids = set()
        
        for doc in docs:
            profile_id = doc.metadata.get("id")
            if profile_id and profile_id not in seen_ids:
                seen_ids.add(profile_id)
                profiles.append(Profile(
                    id=profile_id,
                    name=doc.metadata.get("name", "Unknown"),
                    profile_pic=doc.metadata.get("profile_pic"),
                    headline=doc.metadata.get("role"),
                    summary=doc.page_content,
                    linkedin_url=doc.metadata.get("linkedin_url")
                ))
        
        # Generate response text
        system_prompt = """You are a helpful assistant that helps users find Georgia Tech alumni based on their query.
        Given the search results, analyze them and provide a structured response with the following:
        1. A concise summary of the overall findings
        2. Key highlights or patterns you've noticed
        3. Specific recommendations for each relevant profile, explaining why they match the query
        
        Keep your responses focused and relevant to the user's query."""
        
        human_prompt = f"""User query: {request.message}
        
        Search results:
        {json.dumps([{
            "content": doc.page_content,
            "metadata": {
                k: v for k, v in doc.metadata.items()
                if k in ["name", "role", "company", "work_type", "school", "degree", "major"]
            }
        } for doc in docs], indent=2)}"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            response = llm.invoke(messages)
            return ChatResponse(
                response=response.content,
                profiles=profiles
            )
        except Exception as e:
            print(f"Error from LLM: {str(e)}")
            # Return a graceful error response
            return ChatResponse(
                response=json.dumps({
                    "summary": "Sorry, I encountered an error while processing your request.",
                    "highlights": ["Error processing the query"],
                    "recommendations": []
                }),
                profiles=profiles
            )
            
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "An error occurred while processing your request", "error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 