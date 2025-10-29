import json, requests
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain_core.prompts import PromptTemplate
from typing import List, Dict, Any
import os, re, ast
import os
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
import asyncio
from google import genai
from agent.manager_prompt_for_f4f import f4f_manager_prompt
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
# os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "AIzaSyDoomH3hk4QL42ss9nsq3I50OOB0km3RJg")


# --- Memory Management Functions ---
def load_memory(file_path='memory_agent_f4f.json'):
    """Loads chat history from a JSON file."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        content = f.read().strip()
        if not content:
            return []
        return json.loads(content)

def reset_memory(file_path="memory_agent_f4f.json"):
    """Resets (deletes) the memory file."""
    if os.path.exists(file_path):
        os.remove(file_path)

def save_memory(memory_buffer):
    """Saves chat history to a JSON file."""
    try:
        with open("memory_agent_f4f.json", "w") as f:
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

# Reset memory at the start of the application for a fresh run
reset_memory()
global_memory = reconstruct_memory(load_memory()) # Global memory instance for agents

class AgentPersona:
    def __init__(self):
        self.rag_tool = None
        # self.api_post_tool = None
        self.completion_tool = None
        self.vectorstore = None
        self.bot_creation_task_body_tool = None
        self.bot_creation_api_tool = None
        self.bot_update_api_tool = None
        self.bot_report_task_body_tool = None
        self.bot_delete_tool = None
        self.device_delete_tool = None
        self.server_delete_tool = None
        self.audience_delete_tool = None
        self.scrape_task_delete_tool = None
        self.bot_names_api_tool=None
        self.scrape_task_names_api_tool=None
        self.device_names_api_tool=None
        self.server_names_api_tool=None
        self.proxy_urls_api_tool=None
        self.audience_names_api_tool=None
        self.bot_update_api_tool=None
        self.bot_update_info_api_tool=None
        self.server_creation_api_tool=None
        self.device_creation_api_tool=None
        self.agent_bots = None
        self.llm = None
        self.bots_agent_executor = None
        self.manager_agent_executor = None

        
        self.is_initialized = False

    def rag_query_tool_func(self, query: str) -> str:
        """
        A RAG tool to fetch details from the database based on the user's input.
        Input should be a question or query related to the knowledge base.
        """
        if self.vectorstore:
            try:
                # Perform similarity search to get relevant documents
                retrieved_docs = self.vectorstore.similarity_search(query,k=5)

                if not retrieved_docs:
                    return "No relevant information found in the knowledge base."

                # Concatenate the page_content of the retrieved documents
                # You can customize this formatting as needed
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
            description="Useful for when you need to fetch specific details or answer questions "
                        "from the knowledge base/database."
        )

    

    def initialize_llm_and_rag(self):
        """Initializes the LLM and RAG system (vectorstore and embeddings)."""

        if "GOOGLE_API_KEY" not in os.environ:
            print("Warning: GOOGLE_API_KEY environment variable not set. LLM might not function.")
            os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", GEMINI_API_KEY)

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
            loader = DirectoryLoader(
                r'agent/Follow4Follow docs',
                glob="**/*.pdf",
                loader_cls=PyPDFLoader,
                use_multithreading=True,
                show_progress=True
            )
            docs = loader.load()
            if not docs:
                print("Warning: No documents loaded from 'Follow4Follow docs/'.")
        except Exception as e:
            print(f"Error loading documents: {e}")
            docs = []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

        splits = text_splitter.split_documents(docs)
        print(f"Number of document chunks: {len(splits)}")

        # ✅ Wrap async embedding instantiation
        embeddings = asyncio.run(self._init_embeddings())

        FAISS_INDEX_PATH = "agent/faiss_index_follow4follow_chatbot"
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

        # Call the other initializers
        self.initialize_rag_tool()
        self.initialize_bot_creation()
        self.initialize_central_for_bot_creation()
        self.initialize_central_for_bot_names()
        self.initialize_central_for_bot_update()
        self.initialize_central_for_bot_details()
        self.initialize_bot_delete()
        self.initialize_device_delete()
        self.initialize_audience_delete()
        self.initialize_scrape_task_delete()
        self.initialize_server_delete()
        self.initialize_central_for_scrape_task_names()
        self.initialize_central_for_device_names()
        self.initialize_central_for_server_names()
        self.initialize_central_for_proxy_urls()
        self.initialize_central_for_audience_names()
        self.initialize_central_for_bot_update_info()
        self.initialize_central_for_server_creation()
        self.initialize_central_for_device_creation()


# ✅ Define the async method
    async def _init_embeddings(self):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        
    def initialize_bot_creation(self):
        """Initializes the Bot Creation.""" 
        self.bot_creation_task_body_tool = Tool(
            name="Bot_Creation",
            func=self.task_body_creation_for_new_bot,
            description="Creates the task body for bot creation tasks."
        )
    def task_body_creation_for_new_bot(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.3, # Set your desired temperature here
    # other parameters like top_p, top_k, max_output_tokens can also be set here
)
        #simple LLM:
        print(f"\nAgent Query for Body Creation for New bot: {query}")
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=config,
            contents=f"""You have to precisely extract value of spreadsheet URL from the {query} and"
            "after that you need to fill the folowing task body with those values precisely:"
            "Task body Example:"
            "{{
            "resource_type":"profiles",
            "spreadsheet_url":"from query",
            "request_id":"str(uuid.uuid1())"            
        }}
        The request_id should be unique ID which you should generate yourself using uuid module.
        Once, you have filled this task body correctly, return it as your Final Answer as a valid JSON.
        """
            
        )
        json_output = response.text
        match = re.search(r"```json(.*)", json_output, re.DOTALL)
        # print(match)
        if match:
            final_json_string = (match.group(1)).replace("```","")
        print(f"Completed task body: {final_json_string}")
        json_obj = json.loads(final_json_string)
        # print(f" and its type: {type(json_obj)}")
        json_string = json.dumps(json_obj)

# 2. Create a HumanMessage instance with the JSON string as content
        human_message_with_json = HumanMessage(content=json_string)
        # print(human_message_with_json)
        # save_memory(serialize_messages(self.super_manager_agent_executor.memory.chat_memory.messages))
        global_memory.chat_memory.add_message(human_message_with_json)    
        return json_string
    def initialize_central_for_bot_creation(self):
        """Initializes the Central for Bot Creation.""" 
        self.bot_creation_api_tool = Tool(
            name="Bot_Creation_API_Calling",
            func=self.central_api_call_for_bot_creation,
            description="Creates the task body for bot creation tasks."
        )
    def central_api_call_for_bot_creation(self, query):
        headers = {'Content-Type': 'application/json', 'username':'jeni','password':'jeni'}
        import json
        query = json.loads(query)
        print(type(query))
        response=requests.post(data=json.dumps(query),url='https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/create/',headers=headers)
        print(response)
        if response.status_code == 200:
            return response.text
        else:
            return f"ResponseError: {response.status_code} - {response.text}"    
    def initialize_central_for_server_creation(self):
        """Initializes the Central for Server Creation.""" 
        self.server_creation_api_tool = Tool(
            name="Server_Creation_API_Calling",
            func=self.central_api_call_for_server_creation,
            description="Creates the Server on Central by using the user-provided updated payload in the query"
        )
    def central_api_call_for_server_creation(self, query):
        headers = {'Content-Type': 'application/json'}
        import json
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = json.loads(query)
        print(type(query))
        response=requests.post(data=json.dumps(query),url='https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/server/',headers=headers, auth=auth)
        print(response)
        if response.status_code == 200:
            return response.text
        else:
            return f"ResponseError: {response.status_code} - {response.text}" 
    def initialize_central_for_device_creation(self):
        """Initializes the Central for Device Creation.""" 
        self.device_creation_api_tool = Tool(
            name="Device_Creation_API_Calling",
            func=self.central_api_call_for_device_creation,
            description="Creates the Device on Central"
        )
    def central_api_call_for_device_creation(self, query):
        headers = {'Content-Type': 'application/json', 'username':'jeni','password':'jeni'}
        import json
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = json.loads(query)
        print(type(query))
        response=requests.post(data=json.dumps(query),url='https://3108a95be43e.ngrok-free.app/sessionbot/api/devices/create/',headers=headers, auth=auth)
        print(response)
        if response.status_code == 200:
            return response.text
        else:
            return f"ResponseError: {response.status_code} - {response.text}" 
    def initialize_central_for_bot_update(self):
        """Initializes the Central for Bot Update.""" 
        self.bot_update_api_tool = Tool(
            name="Bot_Update_API_Calling",
            func=self.central_api_call_for_bot_update,
            description="Updates the bot on central using API call."
        )
    def central_api_call_for_bot_update(self, query):
        headers = {'Content-Type': 'application/json'}
        import json
        query = json.loads(query)
        print(type(query))
        profile_number = 30
        response=requests.post(data=json.dumps(query),url=f'https://37deebac6d8e.ngrok-free.app/sessionbot/api/resource/profile/',headers=headers)
        print(response)
        if response.status_code == 200:
            return response.text
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_central_for_bot_names(self):
        """Initializes the Central for Bot Names.""" 
        self.bot_names_api_tool = Tool(
            name="Bot_Names",
            func=self.central_api_call_for_bot_names,
            description="Gets the name of the bots from central using API call."
        )
    def central_api_call_for_bot_names(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/profile/',headers=headers, auth=auth)
        print(response.text)
        data = response.text
        data = json.loads(data)
        profiles = data.get('results')
        names = []
        
        for profile in profiles:
            name = profile.get('display_name')
            names.append(name)
        if response.status_code == 200:
            return names
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_central_for_bot_details(self):
        """Initializes the Central for Bot Details.""" 
        self.bot_details_api_tool = Tool(
            name="Bot_Details",
            func=self.central_api_call_for_bot_details,
            description="Gets the details of the bot from central using API call."
        )
    def central_api_call_for_bot_details(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/profile/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        profiles = data.get('results')
        names = []
        
        for profile in profiles:
            name = profile.get('display_name')
            print(name)
            id = profile.get('id')
            if name == query:
                _resp = requests.get(url = f'https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/profile/{id}/', headers=headers, auth=auth)
                # print(_resp.text)
        if response.status_code == 200:
            return _resp.text
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_central_for_bot_update_info(self):
        """Initializes the Central for Bot Info Update.""" 
        self.bot_update_info_api_tool = Tool(
            name="Bot_Update",
            func=self.central_api_call_for_bot_update_info,
            description="Updates the details of the bot from central using API call."
        )
    def central_api_call_for_bot_update_info(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = json.loads(query)
        bot_id = query.get('id')
        query.pop('id')
        
        response = requests.patch(data=json.dumps(query), url=f"https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/profile/{bot_id}/", headers=headers, auth=auth)
        if response.status_code == 200:
            return response
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_central_for_scrape_task_names(self):
        """Initializes the Central for Scrape Task Names.""" 
        self.scrape_task_names_api_tool = Tool(
            name="Scrape_Task_Names",
            func=self.central_api_call_for_scrape_task_names,
            description="Gets the name of the scrape tasks from central using API call."
        )
    def central_api_call_for_scrape_task_names(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://37deebac6d8e.ngrok-free.app/sessionbot/api/resource/scrapetask/',headers=headers, auth=auth)
        print(response.text)
        data = response.text
        data = json.loads(data)
        scrape_tasks = data.get('results')
        names = []
        print(f"Query: {query} and type: {type(query)}")
        for scrape_task in scrape_tasks:
            name = scrape_task.get('name')
            names.append(name)
        if response.status_code == 200:
            return names
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_central_for_device_names(self):
        """Initializes the Central for Device Names.""" 
        self.device_names_api_tool = Tool(
            name="Device_Names",
            func=self.central_api_call_for_device_names,
            description="Gets the name of the devices from central using API call."
        )
    def central_api_call_for_device_names(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://37deebac6d8e.ngrok-free.app/sessionbot/api/resource/device/',headers=headers, auth=auth)
        print(response.text)
        data = response.text
        data = json.loads(data)
        devices = data.get('results')
        names = []
        print(f"Query: {query} and type: {type(query)}")
        for device in devices:
            name = device.get('name')
            names.append(name)
        if response.status_code == 200:
            return names
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_central_for_server_names(self):
        """Initializes the Central for Server Names.""" 
        self.server_names_api_tool = Tool(
            name="Server_Names",
            func=self.central_api_call_for_server_names,
            description="Gets the name of the servers from central using API call."
        )
    def central_api_call_for_server_names(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://37deebac6d8e.ngrok-free.app/sessionbot/api/resource/server/',headers=headers, auth=auth)
        print(response.text)
        data = response.text
        data = json.loads(data)
        servers = data.get('results')
        names = []
        print(f"Query: {query} and type: {type(query)}")
        for server in servers:
            name = server.get('name')
            names.append(name)
        if response.status_code == 200:
            return names
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_central_for_proxy_urls(self):
        """Initializes the Central for Proxy URLs.""" 
        self.proxy_urls_api_tool = Tool(
            name="Proxy_URLs",
            func=self.central_api_call_for_proxy_urls,
            description="Gets the proxy urls from central using API call."
        )
    def central_api_call_for_proxy_urls(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://37deebac6d8e.ngrok-free.app/sessionbot/api/resource/proxy/',headers=headers, auth=auth)
        print(response.text)
        data = response.text
        data = json.loads(data)
        proxies = data.get('results')
        names = []
        print(f"Query: {query} and type: {type(query)}")
        for proxy in proxies:
            name = proxy.get('name')
            names.append(name)
        if response.status_code == 200:
            return names
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_central_for_audience_names(self):
        """Initializes the Central for Audience Names.""" 
        self.audience_names_api_tool = Tool(
            name="Audience_Names",
            func=self.central_api_call_for_audience_names,
            description="Gets the audience names from central using API call."
        )
    def central_api_call_for_audience_names(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://37deebac6d8e.ngrok-free.app/sessionbot/api/resource/audience/',headers=headers, auth=auth)
        print(response.text)
        data = response.text
        data = json.loads(data)
        audiences = data.get('results')
        names = []
        print(f"Query: {query} and type: {type(query)}")
        for audience in audiences:
            name = audience.get('name')
            names.append(name)
        if response.status_code == 200:
            return names
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_central_for_device_update(self):
        """Initializes the Central for Device Update.""" 
        self.device_update_api_tool = Tool(
            name="Device_Update_API_Calling",
            func=self.central_api_call_for_device_update,
            description="Updates the device on central using API call."
        )
    def central_api_call_for_device_update(self, query):
        headers = {'Content-Type': 'application/json'}
        import json
        query = json.loads(query)
        print(type(query))
        response=requests.post(data=json.dumps(query),url=f'https://37deebac6d8e.ngrok-free.app/sessionbot/api/resource/device/',headers=headers)
        print(response)
        if response.status_code == 200:
            return response.text
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_bot_delete(self):
        """Initializes the Bot Delete Process.""" 
        self.bot_delete_tool = Tool(
            name="Bot_Delete",
            func=self.task_body_creation_for_bot_delete,
            description="Takes the name of the bot and deletes the bot from central"
        )
    def task_body_creation_for_bot_delete(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url='https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/profile/',headers=headers)
        data = resp.text
        data = json.loads(data)
        profiles = data.get('results')
        
        print(f"Query: {query} and type: {type(query)}")
        for profile in profiles:
            name = profile.get('display_name')
            id = profile.get('id')
            if name == query:
                print(f"Bot :{name}, ID: {id}")
                _resp=requests.delete(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/profile/{id}/',headers=headers, auth =auth)
                print(_resp.text)
        return _resp.text
    def initialize_scrape_task_delete(self):
        """Initializes the Scrape Task Delete Process.""" 
        self.scrape_task_delete_tool = Tool(
            name="Scrape_Task_Delete",
            func=self.central_api_call_for_scrape_task_delete,
            description="Takes the name of the scrape task and deletes the scrape task from central"
        )
    def central_api_call_for_scrape_task_delete(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url='https://215c63613292.ngrok-free.app/sessionbot/api/resource/scrapetask/',headers=headers)
        data = resp.text
        data = json.loads(data)
        scrape_tasks = data.get('results')
        
        print(f"Query: {query} and type: {type(query)}")
        for scrape_task in scrape_tasks:
            name = scrape_task.get('name')
            id = scrape_task.get('id')
            if name == query:
                print(f"Scrape Task Name :{name}, ID: {id}")
                _resp=requests.delete(url=f'https://215c63613292.ngrok-free.app/sessionbot/api/resource/scrapetask/{id}/',headers=headers, auth =auth)
                print(_resp.text)
        return _resp.text
    def initialize_device_delete(self):
        """Initializes the Device Delete Process.""" 
        self.device_delete_tool = Tool(
            name="Device_Delete",
            func=self.central_api_call_for_device_delete,
            description="Takes the name of the device and deletes the device from central"
        )
    def central_api_call_for_device_delete(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url='https://215c63613292.ngrok-free.app/sessionbot/api/resource/device/',headers=headers)
        data = resp.text
        data = json.loads(data)
        devices = data.get('results')
        
        print(f"Query: {query} and type: {type(query)}")
        for device in devices:
            name = device.get('name')
            id = device.get('id')
            if name == query:
                print(f"Device Name :{name}, ID: {id}")
                _resp=requests.delete(url=f'https://215c63613292.ngrok-free.app/sessionbot/api/resource/device/{id}/',headers=headers, auth =auth)
                print(_resp.text)
        return _resp.text
    def initialize_server_delete(self):
        """Initializes the Server Delete Process.""" 
        self.server_delete_tool = Tool(
            name="Server_Delete",
            func=self.central_api_call_for_server_delete,
            description="Takes the name of the server and deletes the server from central"
        )
    def central_api_call_for_server_delete(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url='https://215c63613292.ngrok-free.app/sessionbot/api/resource/server/',headers=headers)
        data = resp.text
        data = json.loads(data)
        servers = data.get('results')
        
        print(f"Query: {query} and type: {type(query)}")
        for server in servers:
            name = server.get('name')
            id = server.get('id')
            if name == query:
                print(f"Device Name :{name}, ID: {id}")
                _resp=requests.delete(url=f'https://215c63613292.ngrok-free.app/sessionbot/api/resource/server/{id}/',headers=headers, auth =auth)
                print(_resp.text)
        return _resp.text
    def initialize_audience_delete(self):
        """Initializes the Audience Delete Process.""" 
        self.audience_delete_tool = Tool(
            name="Audience_Delete",
            func=self.central_api_call_for_audience_delete,
            description="Takes the name of the audience and deletes the audience from central"
        )
    def central_api_call_for_audience_delete(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url='https://215c63613292.ngrok-free.app/sessionbot/api/resource/audience/',headers=headers)
        data = resp.text
        data = json.loads(data)
        audiences = data.get('results')
        
        print(f"Query: {query} and type: {type(query)}")
        for audience in audiences:
            name = audience.get('name')
            id = audience.get('id')
            if name == query:
                print(f"Device Name :{name}, ID: {id}")
                _resp=requests.delete(url=f'https://215c63613292.ngrok-free.app/sessionbot/api/resource/audience/{id}/',headers=headers, auth =auth)
                print(_resp.text)
        return _resp.text
    def initialize_bot_reporting(self):
        """Initializes the Bot Report Generation.""" 
        self.bot_report_task_body_tool = Tool(
            name="Bot_Reporting",
            func=self.task_body_creation_for_bot_report,
            description="Creates the task body for bot report generation."
        )
    def task_body_creation_for_bot_report(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.3, # Set your desired temperature here
    # other parameters like top_p, top_k, max_output_tokens can also be set here
)
        #simple LLM:
        print(f"\nAgent Query for Body Creation for Bot Report Generation: {query}")
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=config,
            contents=f"""You have to precisely extract value of profile number from the {query} and"
            "after that you need to fill the folowing task body with those values precisely:"
            "Task body Example:"
            "{{
            "object_type":"bots",
            "chart_type":"bar",
            "bot_type":"browser_profile",
            "selected_objects":["profile number from query"],
                   
        }}
        If the profile number is just a single entity for example, 30, then "selected_objects":["30"] and if the profile number has multiple entities for example, 30,40 then "selected_objects":["30","40"]    
        Once, you have filled this task body correctly, return it as your Final Answer as a valid JSON.
        """
            
        )
        json_output = response.text
        match = re.search(r"```json(.*)", json_output, re.DOTALL)
        # print(match)
        if match:
            final_json_string = (match.group(1)).replace("```","")
        print(f"Completed task body for Report Generation : {final_json_string}")
        json_obj = json.loads(final_json_string)
        # print(f" and its type: {type(json_obj)}")
        json_string = json.dumps(json_obj)
    
    
    def create_manager_agent(self):
        """
        Creates and initializes the Persona Agent.
        This agent orchestrates the Task Creation Agent and Task Completion Agent
        for filling 'awaiting' fields.
        """
        manager_tools = [self.device_names_api_tool,self.device_creation_api_tool,self.bot_details_api_tool,self.server_creation_api_tool,self.bot_update_info_api_tool, self.audience_names_api_tool,self.proxy_urls_api_tool,self.server_names_api_tool,self.bot_creation_task_body_tool, self.bot_creation_api_tool, self.bot_update_api_tool, self.bot_delete_tool, self.rag_tool, self.bot_names_api_tool, self.scrape_task_names_api_tool]

        manager_agent_runnable = create_react_agent(self.llm, manager_tools, f4f_manager_prompt)
        self.manager_agent_executor = AgentExecutor(
            agent=manager_agent_runnable,
            tools=manager_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=global_memory # Share the global memory
        )

    def initialize(self):
        """Initializes all components: LLM, RAG, and all agents."""
        self.initialize_llm_and_rag()
        if not self.llm or not self.rag_tool:
            print("Initialization failed: LLM or RAG tool not set up.")
            return False
        self.create_manager_agent()
        

        self.is_initialized = True
        return True

    def chat_with_agent(self, user_input: str) -> Dict[str, Any]:
        """
        Manages the conversational flow with the user, orchestrating the Persona Agent. 
        Handles the assigning process of persona and demographics for the social media profiles.
        """
        from langchain.callbacks import get_openai_callback
        with get_openai_callback() as cb:
    # Invoke the agent with a query that requires a tool call
            response = self.manager_agent_executor.invoke({"input": user_input})
            
            # Print the token usage from the callback object
            print("\n--- Callback Token Usage ---")
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
        # response = self.manager_agent_executor.invoke({"input": user_input})
                # Access the response_metadata
        
        # Step 1: Print all intermediate tool steps
            intermediate_steps = response.get("intermediate_steps", [])
            for i, (action, observation) in enumerate(intermediate_steps):
                try:
                    observation_json = HumanMessage(content=observation.strip())
                    global_memory.chat_memory.add_message(observation_json)
                except Exception as e:
                    pass
            # print(response)
            print(f"Assistant: {response['output']}")
            save_memory(serialize_messages(self.manager_agent_executor.memory.chat_memory.messages))

        return response['output']

