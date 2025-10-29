import json, requests
from langchain.agents import AgentExecutor, Tool, create_react_agent
from typing import List, Dict, Any
import os, re, ast
import django
from follow4follow import settings
# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)
django.setup()
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings # Keeping this import as it was in original but using GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, AIMessage
from google import genai
from dotenv import load_dotenv
load_dotenv()
from knowledge_base_prompt import knowledge_base_prompt

# --- Memory Management Functions ---
def load_memory(file_path):
    """Loads chat history from a JSON file."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        content = f.read().strip()
        if not content:
            return []
        return json.loads(content)

def reset_memory(file_path):
    """Resets (deletes) the memory file."""
    if os.path.exists(file_path):
        os.remove(file_path)

def save_memory(memory_buffer, file_path):
    """Saves chat history to a JSON file."""
    try:
        with open(file_path, "w") as f:
            json.dump(memory_buffer, f)
    except Exception as e:
        print(f'Error occured while saving to memory: {e}')
def reconstruct_memory(memory_data):
    """Reconstructs ConversationBufferMemory from a list of dicts."""
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    messages = []
    for msg_dict in memory_data:
        if msg_dict.get('type') == 'human':
            messages.append(HumanMessage(content=msg_dict['content']))
        elif msg_dict.get('type') == 'ai':
            messages.append(AIMessage(content=msg_dict['content']))
    memory.chat_memory.messages = messages
    return memory

def serialize_messages(messages):
    """Serializes LangChain message objects to dicts for saving."""
    serialized = []
    for msg in messages:
        if hasattr(msg, "model_dump"):
            serialized.append(msg.model_dump())
        elif isinstance(msg, dict):
            serialized.append(msg)
        else:
            raise TypeError(f"Unsupported message type: {type(msg)}")
    return serialized
def serialize_task_body(msg):
    """Serializes LangChain message objects to dicts for saving."""
    serialized = []
    if hasattr(msg, "model_dump"):
        serialized.append(msg.model_dump())
    elif isinstance(msg, dict):
        serialized.append(msg)
    else:
        raise TypeError(f"Unsupported message type: {type(msg)}")
    return serialized



class KnowlegdeBase:
    def __init__(self):
    
        self.rag_tool = None
        self.vectorstore = None
        self.is_initialized = False
        self.knowledge_base_total_tokens=0
        self.knowledge_base_input_tokens=0
        self.knowledge_base_output_tokens=0
        self.memory_for_agent = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    def rag_query_tool_func(self, query: str) -> str:
        """
        A RAG tool to fetch details from the database based on the user's input.
        Input should be a question or query related to the knowledge base.
        """
        if self.vectorstore:
            try:
                retrieved_docs = self.vectorstore.similarity_search(query,k=5)
                if not retrieved_docs:
                    return "No relevant information found in the knowledge base."
                combined_content = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
                return combined_content
            except Exception as e:
                return f"Error using RAG tool: {e}"
        else:
            return "RAG system is not initialized. Cannot fetch information."

    def initialize_rag_tool(self):
        """Initializes the RAG_Query tool."""
        self.rag_tool = Tool(
            name="RAG_Query",
            func=self.rag_query_tool_func,
            description="Useful for when you need to fetch details regarding a specific user query from the Knowledge Base."
        )

    def initialize_llm_and_rag(self):
        """Initializes the LLM and RAG system (vectorstore and embeddings)."""

        if "GOOGLE_API_KEY" not in os.environ:
            os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

        from langchain_google_genai import ChatGoogleGenerativeAI

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        print("Setting up RAG system...")
        try:
            # Adjust the directory path if 'Services_Schemas' is not directly accessible
            loader = DirectoryLoader(r'Knowledge base docs', glob="**/*.pdf", loader_cls=PyPDFLoader, use_multithreading=True, show_progress=True)
            docs = loader.load()
            if not docs:
                print("Warning: No documents loaded from 'Knowledge base docs'. Make sure the directory and PDFs exist.")
        except Exception as e:
            print(f"Error loading documents: {e}. Please ensure 'Knowledge base docs/' directory with PDFs exists and is accessible.")
            docs = []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        
        splits = text_splitter.split_documents(docs)
        print(f"Number of document chunks: {len(splits)}")
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        FAISS_INDEX_PATH = "faiss_index_knowledgebase_chatbot"
        if os.path.exists(FAISS_INDEX_PATH):
            print(f"Loading FAISS index from {FAISS_INDEX_PATH}...")
            self.vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        else:
            print("Creating new FAISS index...")
            if splits:
                self.vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
                self.vectorstore.save_local(FAISS_INDEX_PATH)
                print(f"FAISS index saved to {FAISS_INDEX_PATH}")
            else:
                print("Cannot create FAISS index: no document splits available.")
                self.vectorstore = None

        self.initialize_rag_tool()
        

    def create_knowledge_base_agent(self):
        """
        Creates and initializes the Manager Agent.
        This agent orchestrates the user query handling and efficient tool calling with respect to the user query.
        """
        knowledge_base_tools = [self.rag_tool]
        
        knowledge_base_agent_runnable = create_react_agent(self.llm, knowledge_base_tools, knowledge_base_prompt)
        self.knowledge_base_agent_executor = AgentExecutor(
            agent=knowledge_base_agent_runnable,
            tools=knowledge_base_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=self.memory_for_agent
        )

    def initialize(self):
        """Initializes all components: LLM, RAG, and all agents."""
        self.initialize_llm_and_rag()
        if not self.llm or not self.rag_tool:
            print("Initialization failed: LLM or RAG tool not set up.")
            return False
        
        self.create_knowledge_base_agent()

        self.is_initialized = True
        return True

    def chat_with_agent(self, user_input: str) -> Dict[str, Any]:
        """
        Takes the user query and forwards it to Bots_CRUD tool as it is.
        """
        print(f"-----Query for Knowledge Base Agent: {user_input}-----")
        from langchain.callbacks import get_openai_callback
        with get_openai_callback() as cb:
            # Invoke the agent with a query that requires a tool call
            response = self.knowledge_base_agent_executor.invoke({"input": user_input})
            self.manager_tokens = cb.total_tokens
            self.manager_input_tokens = cb.prompt_tokens
            self.manager_output_tokens = cb.completion_tokens
            # # Print the token usage from the callback object
            print("\n--- Callback Token Usage for Manager Agent---")
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
    
        
        save_memory(serialize_messages(self.knowledge_base_agent_executor.memory.chat_memory.messages), 'knowldge_base_memory.json')

        return response['output']

