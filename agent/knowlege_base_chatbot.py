import json, requests
from langchain.agents import AgentExecutor, Tool, create_react_agent
from typing import List, Dict, Any
import os, re, ast
import django
from langchain_core.documents import Document
import pymupdf
from follow4follow import settings
# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)
django.setup()
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
from google import genai
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
from agent.knowledge_base_prompt import knowledge_base_prompt
api_key = os.getenv("GOOGLE_API_KEY")
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
            description="Useful for when you need to fetch details regarding a specific user query from the Knowledge Base. Try to get the relevant information by understanding the user query."
        )

    def initialize_llm_and_rag(self):
        """Initializes the LLM and RAG system (vectorstore and embeddings)."""
        import os, re, pymupdf, asyncio
        if "GOOGLE_API_KEY" not in os.environ:
            os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", GEMINI_API_KEY)
        from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
        from langchain_community.vectorstores import FAISS
        from langchain.schema import Document
        
        # Step 1: Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            
        )
        def extract_pdf_text(path):
            doc = pymupdf.open(path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text

        def extract_qa_pairs(text):
            # Regular expression to match Q: ... A: ...
            pattern = r"Q[:\-–]?\s*(.*?)\nA[:\-–]?\s*(.*?)(?=\nQ[:\-–]?|\Z)"
            matches = re.findall(pattern, text, re.DOTALL)

            docs = []
            for question, answer in matches:
                docs.append({
                    "question": question.strip(),
                    "answer": answer.strip()
                })
            return docs

        def process_pdfs_in_directory(pdf_dir):
            all_docs = []
            for filename in os.listdir(pdf_dir):
                if filename.lower().endswith(".pdf"):
                    pdf_path = os.path.join(pdf_dir, filename)
                    raw_text = extract_pdf_text(pdf_path)
                    clean_text = raw_text.replace("uestion:", "Question:").replace("nswer:", "Answer:")
                    docs = extract_qa_pairs(clean_text)
                    lc_docs = [
                        Document(
                            page_content=f"Q: {item['question']}\nA: {item['answer']}",
                            metadata={"question": item['question'], "source": filename}
                        )
                        for item in docs
                    ]
                    all_docs.extend(lc_docs)
            return all_docs

        # Step 3: Build docs from PDFs
        docs = process_pdfs_in_directory('agent/Knowledge base docs')
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())
        
        from langchain_huggingface import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        FAISS_INDEX_PATH = "faiss_index_knowledge_base_chatbot"
        if os.path.exists(FAISS_INDEX_PATH):
            print(f"Loading FAISS index from {FAISS_INDEX_PATH}...")
            self.vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        else:
            print("Creating new FAISS index...")
            if docs:
                self.vectorstore = FAISS.from_documents(documents=docs, embedding=embeddings)
                self.vectorstore.save_local(FAISS_INDEX_PATH)
                print(f"FAISS index saved to {FAISS_INDEX_PATH}")
            else:
                print("Cannot create FAISS index: no documentS available.")
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
        Takes the user query and forwards it to RAG_Query tool as it is.
        """
        print(f"-----Query for Knowledge Base Agent: {user_input}-----")
        from langchain.callbacks import get_openai_callback
        with get_openai_callback() as cb:
            
            response = self.knowledge_base_agent_executor.invoke({"input": user_input})
            self.knowledge_base_total_tokens = cb.total_tokens
            self.knowledge_base_input_tokens = cb.prompt_tokens
            self.knowledge_base_output_tokens = cb.completion_tokens
            
            print("\n--- Callback Token Usage for Knowledge Base Agent---")
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
    
        
        save_memory(serialize_messages(self.knowledge_base_agent_executor.memory.chat_memory.messages), 'knowldge_base_memory.json')
        response = response['output']
        response = response.replace("```markdown","").replace("```","")
        return response

