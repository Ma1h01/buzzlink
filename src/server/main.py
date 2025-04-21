from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import getpass
from IPython.display import Image, display
from datetime import datetime
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LangChain imports
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

# Qdrant imports
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, models

# LangGraph imports
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request/response models
class Profile(BaseModel):
    id: str
    name: str
    profile_pic: Optional[str]
    headline: Optional[str]
    summary: Optional[str]
    linkedin_url: Optional[str]

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    profiles: List[Profile]

# Load environment variables
load_dotenv()

# LangChain API Key
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


# OpenAI model, requires API key
llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18", temperature=0)
# Ensure the response is in JSON format
llm = llm.bind(response_format={"type": "json_object"}) 

embeddings = OllamaEmbeddings(model="nomic-embed-text")


REUSE_COLLECTION = True

# Initialize Qdrant client with environment variables
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

collection_name = "user_profile_collection_with_ollama"

collections = qdrant_client.get_collections()
if collection_name not in [collection.name for collection in collections.collections]:
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=768, 
            distance=Distance.COSINE 
        )
    )
    print(f"Collection '{collection_name}' created successfully!")

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name=collection_name,
    embedding=embeddings
)

DATA_PATH = "../data/raw-profile-data/profile_data.json"

def _get_with_condition(dictionary, key, condition_values=[None, ""], default="Unknown"):
    value = dictionary.get(key, default)
    return default if value in condition_values else value

def preprocess_alumni_profile(data_path):
    """
    Create one document for each alumnus JSON profile, and return a list of documents.
    These documents are then stored in a vector store for later retrieval.
    These documents contain a summary of the alumnus's work experiences and education history with their names, LinkedIn URLs and profile pictures as metadata.
    """
    with open(data_path, 'r') as f:
        alumni_profiles = json.load(f)
        documents = []
        for alumnus in alumni_profiles:
            companies = set()
            id, name, about, headline, location, profile_pic, experiences, educations = _get_with_condition(alumnus, 'id'), _get_with_condition(alumnus, "name"), _get_with_condition(alumnus, "about"), _get_with_condition(alumnus,"headline"), _get_with_condition(alumnus,"location"), _get_with_condition(alumnus,"profile_pic"), _get_with_condition(alumnus,"experiences"), _get_with_condition(alumnus,"educations")
            intro_line = f"{name} is a {headline} at {location}. {name} self-describes as {about}."
            exp_lines, edu_lines = [f"{name}'s work experiences are as follows:"], [f"{name}'s education history is as follows:"]
            for idx, exp in enumerate(experiences):
                title, company, work_type, location, start, end, description = _get_with_condition(exp, "title"), _get_with_condition(exp, "company"), _get_with_condition(exp, "work_type"), _get_with_condition(exp, "location"), _get_with_condition(exp, "start_date"), _get_with_condition(exp, "end_date"), _get_with_condition(exp, "description")
                exp_lines.append(f"{idx+1}. Role: {title}\nCompany: {company}\nWork Type: {work_type}\nLocation: {location}\nDuration: {start} to {end}\nDescription: {description}")
                companies.add(company)
            for idx, edu in enumerate(educations):
                school, degree, major, start, end, description = _get_with_condition(edu, "school"), _get_with_condition(edu, "degree"), _get_with_condition(edu, "major"), _get_with_condition(edu, "start_date"), _get_with_condition(edu, "end_date"), _get_with_condition(edu, "description")
                edu_lines.append(f"{idx+1}. School: {school}\nDegree: {degree}\nMajor: {major}\nDuration: {start} to {end}\nDescription: {description}")

            alumnus_profile_summary = f"{intro_line}\n\n" + "\n".join(exp_lines) + "\n\n" + "\n".join(edu_lines)
            doc = Document(page_content=alumnus_profile_summary, metadata={"id": id, "name": name, "profile_pic": profile_pic, "companies": list(companies)})
            documents.append(doc)
        return documents
    
def preprocess_alumni_profile_with_manual_split(data_path):
    """
    Create one or more documents for each alumnus JSON profile based on the split, and return a list of documents.
    These documents are then stored in a vector store for later retrieval.
    These documents contain a summary of the alumnus's work experiences and education history with their names, LinkedIn URLs and profile pictures as metadata.
    Each profile should have the following splits:
    
    summary: {page_content: <headline+location+bio>, metadata:{id, pic, name, location, role, company, work_type, work_duration, school, degree, major, school_duration}}
    each work exp: {page_content: <title+company+work_type+start_date+end_date+location+description>, metadata:{id, pic, name, location, role, company, work_type, work_duration, school, degree, major, school_duration}}
    each edu hist: {page_content: <school+degree+major+start_date+end_date+description>, metadata:{id, pic, name, role, location, company, work_type, work_duration, school, degree, major, school_duration}}
    """
    with open(data_path, 'r') as f:
        alumni_profiles = json.load(f)
        documents = []
        for alumnus in alumni_profiles:
            # summary
            id, name, about, headline, location, profile_pic, experiences, educations = _get_with_condition(alumnus, 'id'), _get_with_condition(alumnus, "name"), _get_with_condition(alumnus, "about"), _get_with_condition(alumnus,"headline"), _get_with_condition(alumnus,"location"), _get_with_condition(alumnus,"profile_pic"), _get_with_condition(alumnus,"experiences"), _get_with_condition(alumnus,"educations")
            summary_line = f"{name} is a {headline} at {location}. {name} self-describes as {about}"
            summary_doc = Document(page_content=summary_line, metadata={"id":id, "name":name, "profile_pic":profile_pic, "location":location, "role":None, "company":None, "work_type":None, "work_duration":None, "school":None, "degree":None, "major":None, "school_duration":None})

            # work exps
            work_docs = []
            for exp in experiences:
                title, company, work_type, work_location, start, end, description = _get_with_condition(exp, "title"), _get_with_condition(exp, "company"), _get_with_condition(exp, "work_type"), _get_with_condition(exp, "location"), _get_with_condition(exp, "start_date"), _get_with_condition(exp, "end_date"), _get_with_condition(exp, "description")
                exp_line = f"Name: {name}\nRole: {title}\nCompany: {company}\nWork Type: {work_type}\nLocation: {work_location}\nDuration: {start} to {end}\nDescription: {description}"
                work_docs.append(Document(page_content=exp_line, metadata={"id":id, "name":name, "profile_pic":profile_pic, "location":work_location, "role":title, "company":company, "work_type":work_type, "work_duration":f"{start} to {end}", "school":None, "degree":None, "major":None, "school_duration":None}))

            # edu hist
            edu_docs = []                
            for edu in educations:
                school, degree, major, start, end, description = _get_with_condition(edu, "school"), _get_with_condition(edu, "degree"), _get_with_condition(edu, "major"), _get_with_condition(edu, "start_date"), _get_with_condition(edu, "end_date"), _get_with_condition(edu, "description")
                edu_line = f"School: {school}\nDegree: {degree}\nMajor: {major}\nDuration: {start} to {end}\nDescription: {description}"
                edu_docs.append(Document(page_content=edu_line, metadata={"id":id, "name":name, "profile_pic":profile_pic, "location":None, "role":None, "company":None, "work_type":None, "work_duration":None, "school":school, "degree":degree, "major":major, "school_duration":f"{start} to {end}"}))

            documents.extend([summary_doc] + work_docs + edu_docs)
        return documents

if not REUSE_COLLECTION:
    docs = preprocess_alumni_profile_with_manual_split(DATA_PATH)
    print(docs[0])
    print(docs[1])
    vector_store.add_documents(documents=docs)



graph_builder = StateGraph(MessagesState)


def extract_search_parameters(query: str):
    """Use LLM to extract search parameters from a user query."""
    
    system_message = """
    You are an intelligent assistant that extracts useful parameters from user queries into a JSON object.
    Your task is to identify any people names, companies, titles, locations, and duration time mentioned in the user query, and return a JSON object with the extracted information.
    You MUST return an empty array [] as values if you can not find any information for the parameters.
    
    Return your response in the following format:
    {{names: [...], companies: [...], titles: [...], locations: [...], duration: [...], skills: [...]}}

    For the duration parameter, if it is present tense, add 'Present' to the parameter.
    <start_date to end_date> pair should ONLY take one entry in the duration parameter.
    You MUST also expand any short forms of months into the full month name.
    
    Example:
    Query: "Who works at Google as a Data Analyst with AWS experience?"
    Response:
    {{names: [], companies: ["Google"], titles: ["Data Analyst"], locations: [], duration: [], skills: ["AWS"]}}
    
    Query: "Yihao Mai's experience at IBM"
    Response:
    {{names: ["Yihao Mai"], companies: ["IBM"], titles: [], locations: [], duration: [], skills: []}}
    
    Query: "Who worked at Amazon as a Software Engineer intern in May 2025"
    Response:
    {{names: [], companies: ["Amazon"], titles: ["Software Engineer"], locations: [], duration: ["May 2025"]}}
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "Extract search parameters from the following query: {query}")
    ])
    
    response = llm.invoke(prompt.format_messages(query=query))
    
    content = json.loads(response.content)
    print(f"Parsed search parameters: {content}")
    return content



@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    
    # Extract parameters from the query
    params = extract_search_parameters(query)
    
    retrieved_docs = vector_store.similarity_search(query, k=15)

    serialized = []
    for idx, doc in enumerate(retrieved_docs):
        page_content, metadata = doc.page_content, doc.metadata
        id, name, pic, location, role, company, work_type, work_duration, school, degree, major, school_duration = metadata['id'], metadata['name'], metadata['profile_pic'], metadata['location'], metadata['role'], metadata['company'], metadata['work_type'], metadata['work_duration'], metadata['school'], metadata['degree'], metadata['major'], metadata['school_duration']    
        content = f"{idx+1}. Content: {page_content}\nId: {id}\nName: {name}\nProfile Pic: {pic}"
        serialized.append(content)
        serialized.append("\n\n")
    
    serialized = "".join(serialized)
    
    if not retrieved_docs:
        return "No matching alumni profiles found.", []
    
    return serialized, retrieved_docs


CURR_MONTH_YEAR = datetime.now().strftime("%B %Y")
def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""

    # Rewrite the user query into one of the following canonical forms based on its intended temporal context.
    system_message = SystemMessage(
    "You are a specialized assistant for Georgia Tech students seeking information about GT alumni. "
    "Your task is to transform the user query into a canonical question or statement about a person's experience, "
    "including any combination of the following elements, preserving the user's intended tense (past, present, or future):"
    "\n\n- Name: <name>"
    "\n- Position Title: <position_title>"
    "\n- Company: <company>"
    "\n- Location: <location>"
    "\n- Skills: <skills>"
    "\n- Time Period: <time_period> (e.g. 'from Jan 2018 to Dec 2020,' 'from January 2020 to Present,' 'in May 2023,' etc.)"
    "\n\nIf the user mentions words like 'previously,' treat it as past tense (worked). "
    "If they mention 'currently,' 'now', 'present', treat it as present tense (presently works). "
    "If they mention 'will' or 'plans to,' treat it as future tense (will work)."
    "\n\nChoose from the following canonical forms. Use only those placeholders the user actually provides; omit any placeholders they do not mention. "
    "Combine them as needed to reflect the user's request:"
    "\n\n1) Who worked / presently works / will work as <position_title>?"
    "\n2) Who worked / presently works / will work at <company>?"
    "\n3) Who worked / presently works / will work in <location>?"
    "\n4) Who worked / presently works / will work with <skills>?"
    "\n5) Who worked / presently works / will work as <position_title> with <skills>?"
    "\n6) Who worked / presently works / will work at <company> with <skills>?"
    "\n7) Who worked / presently works / will work in <location> with <skills>?"
    "\n8) Who worked / presently works / will work as <position_title> at <company>?"
    "\n9) Who worked / presently works / will work as <position_title> in <location>?"
    "\n10) Who worked / presently works / will work at <company> in <location>?"
    "\n11) Who worked / presently works / will work as <position_title> at <company> in <location>?"
    "\n12) Who worked / presently works / will work as <position_title> at <company> with <skills>?"
    "\n13) Who worked / presently works / will work as <position_title> in <location> with <skills>?"
    "\n14) Who worked / presently works / will work at <company> in <location> with <skills>?"
    "\n\n15) Who worked / presently works / will work as <position_title> during <time_period>?"
    "\n16) Who worked / presently works / will work at <company> during <time_period>?"
    "\n17) Who worked / presently works / will work in <location> during <time_period>?"
    "\n18) Who worked / presently works / will work with <skills> during <time_period>?"
    "\n19) Who worked / presently works / will work as <position_title> at <company> during <time_period>?"
    "\n20) Who worked / presently works / will work as <position_title> in <location> during <time_period>?"
    "\n21) Who worked / presently works / will work at <company> in <location> during <time_period>?"
    "\n22) Who worked / presently works / will work with <skills> at <company> in <location> during <time_period>?"
    "\n23) Who worked / presently works / will work as <position_title> with <skills> during <time_period>?"
    "\n24) Who worked / presently works / will work as <position_title> at <company> with <skills> during <time_period>?"
    "\n25) Who worked / presently works / will work as <position_title> in <location> with <skills> during <time_period>?"
    "\n26) Who worked / presently works / will work as <position_title> at <company> in <location> with <skills> during <time_period>?"
    "\n\n27) <name>'s experience as a <position_title>?"
    "\n28) <name>'s experience as a <position_title> at <company>?"
    "\n29) <name>'s experience as a <position_title> in <location>?"
    "\n30) <name>'s experience at <company> in <location>?"
    "\n31) <name>'s experience with <skills>?"
    "\n32) <name>'s experience as a <position_title> with <skills>?"
    "\n33) <name>'s experience at <company> with <skills>?"
    "\n34) <name>'s experience in <location> with <skills>?"
    "\n\n35) <name>'s experience as a <position_title> at <company> in <location> with <skills>?"
    "\n36) <name>'s experience as a <position_title> during <time_period>?"
    "\n37) <name>'s experience at <company> during <time_period>?"
    "\n38) <name>'s experience in <location> during <time_period>?"
    "\n39) <name>'s experience with <skills> during <time_period>?"
    "\n40) <name>'s experience as a <position_title> at <company> in <location> with <skills> during <time_period>?"
    "\n\nAs soon as you successfully match the user's query to one of these forms, rewrite it in that form and then use the retrieve tool to find alumni information. "
    "If the user's query already meet one of these forms, you STILL need to use the retrieve tool to find alumni information."
    "Otherwise, do not rewrite it and do not call the retrieve tool."
)

    messages = [system_message] + state["messages"]
    llm_with_tools = llm.bind_tools([retrieve]) # Only tells the model there's an available tool to use. The model will decide whether to use it depending on the input message
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# Step 2: Execute the retrieval.
tools = ToolNode([retrieve])


# Step 3: Generate a response using the retrieved content.
def generate(state: MessagesState):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    

    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    
    # Create a static system message for instructing behavior.
    system_message = SystemMessage(
        "You are an assistant for helping Georgia Tech college students find information about Georgia Tech alumni. "
        "You are given a question and a list of retrieved documents about Georgia Tech alumni. "
        "ONLY use the facts from the provided DOCUMENT to answer the question. "
        "Do not incorporate any external or pre-existing knowledge. "
        "If the DOCUMENT does not contain sufficient information to answer the question, return []."
    )
    
    human_message_content = f"""
        INSTRUCTIONS:
        • Answer the QUESTION using ONLY the facts provided in the DOCUMENT.
        • Do not include any information not present in the DOCUMENT.
        • You MUST scan through the entire DOCUMENT list and use all documents that can be helpful to answer the QUESTION.
        • If the DOCUMENT does not contain the facts needed to answer the question, return an empty list [].
        • You MUST return your answer in a list of JSON objects, and each object contains: 
            1. name: the alumnus's name, 
            2. id: the alumnus's id, 
            3. pic: the alumnus's profile picture URL
            4. summary: summary of alumnus experience using the information from the DOCUMENT.
        • Treat any duration whose end date is the literal word "Present"/"Unknown" as ongoing on TODAY.
        • If a question asks about current / present / now, USE ONLY documents whose end‑date == "Present" or "Unknown".
        • If a question asks "as of <year>" or "after <month year>", include only docs active on that date:
            A document {{start, end}} is active on DATE if start ≤ DATE ≤ end (or end == "Present" or "Unknown").
        
        DOCUMENT:
        {docs_content}

        QUESTION:
        {conversation_messages[-1].content}
        """

    human_message = HumanMessage(human_message_content)

    prompt = [system_message, human_message]
 
    # Run
    response = llm.invoke(prompt)


    return {"messages": [response]}


graph_builder.add_node(query_or_respond)
graph_builder.add_node(tools)
graph_builder.add_node(generate)

graph_builder.set_entry_point("query_or_respond")
graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition,
    {END: END, "tools": "tools"},
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

graph = graph_builder.compile()

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 1) Build the payload:
        user_msgs = [
            {"role": "system", "content": "You are a helpful assistant that helps users find Georgia Tech alumni based on their query."},
            {"role": "user",   "content": request.message}
        ]

        # 2) Invoke the graph:
        invocation = graph.invoke({"messages": user_msgs})
        final_messages = invocation["messages"]

        # 3) Pull out the assistant’s reply:
        response_content = final_messages[-1].content

        # 4) Initialize profiles list (avoids UnboundLocalError):
        profiles: List[Profile] = []

        # 5) Extract any tool messages (your retrieve calls) to build Profile objects:
        for msg in final_messages:
            if msg.type == "tool" and isinstance(msg.content, tuple):
                # msg.content is (serialized_string, docs_list)
                _, docs = msg.content
                for doc in docs:
                    md = doc.metadata
                    profiles.append(Profile(
                        id=md.get("id", ""),
                        name=md.get("name", ""),
                        profile_pic=md.get("profile_pic"),
                        headline=md.get("role"),
                        summary=doc.page_content,
                        # assume linkedin_url is the id if it looks like a URL
                        linkedin_url=md.get("id") if md.get("id", "").startswith("http") else None
                    ))

        # 6) Return safely even if no tool messages were found:
        return ChatResponse(response=response_content, profiles=profiles)

    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
