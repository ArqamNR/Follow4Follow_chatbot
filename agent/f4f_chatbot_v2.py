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
from agent.manager_f4f_v2 import bot_crud_agent_prompt, reporting_crud_agent_prompt,f4f_manager_prompt, datahouse_agent_prompt, device_crud_agent_prompt,server_crud_agent_prompt,proxy_crud_agent_prompt,scrape_task_crud_agent_prompt,audience_crud_agent_prompt
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


import os
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
class Chatbot:
    def __init__(self):
        self.ngrok = 'http://208.109.247.201:8080/'
        self.rag_tool = None
        self.completion_tool = None
        self.vectorstore = None
        self.bot_creation_task_body_tool = None
        self.bot_creation_api_tool = None
        self.bot_update_api_tool = None
        self.bot_report_task_body_tool = None
        self.bots_logged_in_api_tool=None
        self.bot_delete_tool = None
        self.device_creation_task_body_tool=None
        self.device_delete_tool = None
        self.filtered_reporting_for_bot_tool=None
        self.server_delete_tool = None
        self.audience_delete_tool = None
        self.scrape_task_delete_tool = None
        self.bot_names_api_tool=None
        self.scrape_task_names_api_tool=None
        self.device_names_api_tool=None
        self.server_names_api_tool=None
        self.proxy_urls_api_tool=None
        self.proxy_creation_task_body_tool=None
        self.audience_names_api_tool=None
        self.bot_update_api_tool=None
        self.bot_update_info_api_tool=None
        self.server_creation_task_body_tool=None
        self.server_creation_api_tool=None
        self.server_choices_tool=None
        self.total_servers_tool=None
        self.server_details_api_tool=None
        self.server_update_info_api_tool=None
        self.server_delete_bulk_tool=None
        self.device_creation_api_tool=None
        self.device_details_api_tool=None
        self.device_update_info_api_tool=None
        self.device_delete_bulk_tool=None
        self.scrape_task_creation_task_body_tool=None
        self.scrape_task_creation_api_tool=None
        self.scrape_task_details_api_tool=None
        self.scrape_task_ids_api_tool=None
        self.total_scrape_tasks_api_tool=None
        self.pause_scrape_tasks_api_tool=None
        self.resume_scrape_tasks_api_tool=None
        self.delete_scrape_tasks_api_tool=None
        self.bots_of_scrape_task_api_tool=None
        self.bot_details_for_scrape_task_api_tool=None
        self.reporting_crud_tool=None
        self.reporting_for_scrape_task_tool=None
        self.reporting_summary_for_scrape_task_tool=None
        self.reporting_for_bot_tool=None
        self.reporting_summary_for_bots_tool=None
        self.datahouse_ops_tool=None
        self.data_house_payload_tool=None
        self.data_house_api_calling_tool=None
        self.agent_bots = None
        self.llm = None
        self.total_devices_tool=None
        self.bots_agent_executor = None
        self.manager_agent_executor = None
        self.bots_crud_tool = None
        self.devices_crud_tool=None
        self.server_crud_tool=None
        self.scrape_tasks_crud_tool=None
        self.proxy_crud_tool=None
        self.audience_crud_tool=None
        self.datahouse_crud_tool=None
        self.report_crud_tool=None
        self.total_bots_tool=None
        self.bots_crud_agent_executor=None
        self.devices_crud_agent_executor=None
        self.server_crud_agent_executor=None
        self.scrape_task_crud_agent_executor=None
        self.proxies_crud_agent_executor=None
        self.datahouse_crud_agent_executor=None
        self.reports_crud_agent_executor=None
        self.audience_crud_agent_executor=None
        self.audience_creation_cleaning_task_body_tool=None
        self.audience_creation_data_enrichment_task_body_tool=None
        self.total_audiences_tool=None
        self.audience_details_api_tool=None
        self.audiences_names_tool=None
        self.audience_delete_tool=None
        self.bots_tokens=0
        self.manager_tokens=0
        self.devices_tokens=0
        self.shared_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.shared_memory_bot = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.shared_memory_datahouse = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.shared_memory_device = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.shared_memory_server = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.shared_memory_proxy = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.shared_memory_scrape_task = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.shared_memory_audience = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.shared_memory_reporting = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
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
            os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", GEMINI_API_KEY)

        from langchain_google_genai import ChatGoogleGenerativeAI

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        print("LLM initialized (RAG skipped).")

        self.initialize_rag_tool()
        self.initialize_bot_creation()
        self.initialize_central_for_bot_creation()
        self.initialize_central_for_bot_names()
        self.initialize_central_for_bot_update()
        self.initialize_central_for_bot_details()
        self.initialize_bot_delete()
        self.initialize_central_for_bot_update_info()
        self.initialize_central_for_total_bots()
        self.initialize_central_for_bots_logged_in()
        self.invoke_bots_crud()
        self.invoke_datahouse_agent()
        self.initialize_data_house_payload_tool()
        self.initialize_device_creation()
        self.initialize_central_for_device_creation()
        self.initialize_central_for_total_devices()
        self.initialize_central_for_device_details()
        self.initialize_central_for_device_names()
        self.initialize_device_delete()
        self.initialize_central_for_device_update_info()
        self.initialize_device_delete_bulk()
        self.invoke_devices_crud()   
        self.invoke_servers_crud()
        self.initialize_central_for_server_names()
        self.initialize_server_creation() 
        self.initialize_central_for_server_creation()
        self.initialize_central_for_server_choices()
        self.initialize_central_for_total_servers()
        self.initialize_central_for_server_details()
        self.initialize_central_for_server_update_info()
        self.initialize_server_delete()
        self.initialize_server_delete_bulk()
        self.initialize_proxy_creation()
        self.initialize_scrape_task_creation()
        self.invoke_scrape_tasks_crud()
        self.initialize_central_for_scrape_task_creation()
        self.initialize_central_for_scrape_task_details()
        self.initialize_central_for_scrape_task_names()
        self.initialize_central_for_total_scrape_tasks()
        self.initialize_central_for_pausing_scrape_tasks()
        self.initialize_central_for_resuming_scrape_tasks()
        self.initialize_central_for_deleting_scrape_tasks()
        self.initialize_central_for_bots_of_scrape_task()
        self.initialize_central_for_bot_details_for_scrape_task()
        self.invoke_audience_crud()
        self.initialize_central_for_scrape_task_ids()
        self.initialize_audience_creation_using_cleaning()
        self.initialize_audience_creation_using_data_enrichment()
        self.initialize_central_for_total_audiences()
        self.initialize_central_for_audience_details()
        self.initialize_central_for_audience_names()
        self.initialize_audience_delete()
        self.invoke_reporting_crud()
        self.initialize_reporting_for_scrape_task()
        self.initialize_reporting_summary_for_scrape_task()
        self.initialize_reporting_for_bots()
        self.initialize_reporting_summary_for_bots()
        self.initialize_reporting_for_devices()
        self.initialize_filtered_reporting_for_bots()
    def initialize_bot_creation(self):
        """Initializes the Bot Creation.""" 
        self.bot_creation_task_body_tool = Tool(
            name="Task_Body_Creation_bots",
            func=self.task_body_creation_for_new_bot,
            description="Creates the task body for bot creation tasks."
        )
    def task_body_creation_for_new_bot(self, query): 
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.5, # Set your desired temperature here
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
            
        return json_string
    def initialize_central_for_bot_creation(self):
        """Initializes the Central for Bot Creation.""" 
        self.bot_creation_api_tool = Tool(
            name="Bot_Creation",
            func=self.central_api_call_for_bot_creation,
            description="Creates the bot on central using the respective updated payload."
        )
    def central_api_call_for_bot_creation(self, query):
        headers = {'Content-Type': 'application/json', 'username':'jeni','password':'jeni'}
        import json
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = query.replace('```',"")
        query = json.loads(query)
        print(type(query))
        response=requests.post(data=json.dumps(query),url=f'{self.ngrok}sessionbot/api/resource/create/',headers=headers,auth=auth)
        print(response)
        if response.status_code == 200:
            json_str = response.text
            parsed_data = json.loads(json_str)

            # Extract the 'data' list
            data_list = parsed_data['data']
            return data_list
        else:
            return f"ResponseError: {response.status_code} - {response.text}"   
    def initialize_central_for_bots_logged_in(self):
        """Initializes the Central for Bots Logged in.""" 
        self.bots_logged_in_api_tool = Tool(
            name="Bots_Logged_in",
            func=self.central_api_call_for_bots_logged_in,
            description="Checks which bots are logged in on central."
        )
    def central_api_call_for_bots_logged_in(self, query):
        headers = {'Content-Type': 'application/json', 'username':'jeni','password':'jeni'}
        import json
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/profile/',headers=headers,auth=auth)
        print(response)
        data = response.text
        data = json.loads(data)
        bots = data.get('results')
        logged_in_status_true = []
        logged_in_status_false = []

        for bot in bots:
            status = bot.get('logged_in')
            name = bot.get('display_name')
            # print(status)
            if status == True:
                logged_in_status_true.append(name)
            if status == False:
                logged_in_status_false.append(name)

        if response.status_code == 200:
            return len(logged_in_status_true)
        else:
            return "Not a positive response was received from Central"
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
        response=requests.post(data=json.dumps(query),url=f'{self.ngrok}sessionbot/api/resource/profile/',headers=headers)
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
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/profile/',headers=headers, auth=auth)
        # print(response.text)
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
    def initialize_central_for_total_bots(self):
        """Initializes the Central for getting the total number of bots.""" 
        self.total_bots_tool = Tool(
            name="Total_bots",
            func=self.central_api_call_for_total_bots,
            description="Gets the total number of the bots from central using API call."
        )
    def central_api_call_for_total_bots(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'{self.ngrok}/sessionbot/api/resource/profile/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        profiles = data.get('count')
        return profiles
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
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/profile/',headers=headers, auth=auth)

        data = response.text
        data = json.loads(data)
        profiles = data.get('results')
        profiles = profiles
        print(f"Query: {query} and its type: {type(query)}")
        query = query.replace("\n","").replace("```","")
        names = []
        # print(profiles)
        for profile in profiles:
            name = profile.get('display_name')
            if name == query:
                print(name)
                res=profile
                return res
        else:
            return f"Bot: {query} is not present in the available bots."
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
        query = query.replace("```","").replace("\n","")
        query = json.loads(query)
        bot_id = query.get('id')
        query.pop('id')
        
        response = requests.patch(data=json.dumps(query), url=f"{self.ngrok}sessionbot/api/resource/profile/{bot_id}/", headers=headers, auth=auth)
        if response.status_code == 200:
            return "The bot's information has been updated successfully."
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    
    def initialize_bot_delete(self):
        """Initializes the Bot Delete Process.""" 
        self.bot_delete_tool = Tool(
            name="Bot_Delete",
            func=self.task_body_creation_for_bot_delete,
            description="Takes the name of the bot and deletes the bot from central"
        )
    def task_body_creation_for_bot_delete(self, query): 
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url=f'{self.ngrok}sessionbot/api/resource/profile/',headers=headers,auth=auth)
        data = resp.text
        data = json.loads(data)
        profiles = data.get('results')
        query = query.replace("\n","").replace("```","")
        found = False
        profiles_ = [profile.get('display_name') for profile in profiles]
        print(profiles_)
        print(f"Query: {query} and type: {type(query)}")
        if query in profiles_:
            for profile in profiles:
                name = profile.get('display_name')
                id = profile.get('id')
                print(name)
                if name == query:
                    print(f"Bot :{name}, ID: {id}")
                    _resp=requests.delete(url=f'{self.ngrok}sessionbot/api/resource/profile/{id}/',headers=headers, auth =auth)
                    print(_resp.text)
                    found = True
                    return f"The bot {query} has been deleted successfully."
        else:
            return f"The bot {query} is not in the list of available bots."
    def initialize_bot_delete_bulk(self):
        """Initializes the Bot Delete Bulk Process.""" 
        self.bot_delete_bulk_tool = Tool(
            name="Bot_Delete_Bulk",
            func=self.task_body_creation_for_bot_delete_bulk,
            description="Takes the names of the bots and delete the bots from central"
        )
    def task_body_creation_for_bot_delete_bulk(self, query): 
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url=f'{self.ngrok}sessionbot/api/resource/profile/',headers=headers)
        data = resp.text
        data = json.loads(data)
        profiles = data.get('results')
        bots_to_delete = query.split(', ')
        print(f"Query: {query} and type: {type(query)}")

        for profile in profiles:
            name = profile.get('display_name')
            id = profile.get('id')
            if name in bots_to_delete:
                print(f"Bot :{name}, ID: {id}")
                _resp=requests.delete(url=f'{self.ngrok}sessionbot/api/resource/profile/{id}/',headers=headers, auth =auth)
                print(_resp.text)
        return _resp.text
    
    def initialize_device_creation(self):
        """Initializes the Device Creation.""" 
        self.device_creation_task_body_tool = Tool(
            name="Task_Body_Creation_devices",
            func=self.task_body_creation_for_new_device,
            description="Creates the task body for Device creation tasks."
        )
    def task_body_creation_for_new_device(self, query): 
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.5,
    )
        #simple LLM:
        query = query.replace("```","").replace("\n","")
        print(f"\nAgent Query for Body Creation for New bot: {query}")
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=config,
            contents=f"""You have to precisely extract value of device name, serial number, server, os, brand and model from the {query} and"
            "after that you need to fill the folowing task body with those values precisely:"
            "Task body Example:"
            "{{
            "name": "from query",
            "serial_number": "from query",
            "connected_to_server": "from query",
            "info": {{
                "os": "from query",
                "brand": "from query",
                "model": "from query"
            }}          
        }}
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
            
        return json_string
    def initialize_central_for_device_creation(self):
        """Initializes the Central for Device Creation.""" 
        self.device_creation_api_tool = Tool(
            name="Device_Creation",
            func=self.central_api_call_for_device_creation,
            description="Creates the device on central using the respective payload."
        )
    def central_api_call_for_device_creation(self, query):
        headers = {'Content-Type': 'application/json', 'username':'jeni','password':'jeni'}
        import json
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = query.replace("```","").replace("\n","")
        query = json.loads(query)
        server_to_connect = query.get('connected_to_server')
        servers=requests.get(data=json.dumps(query),url=f'{self.ngrok}sessionbot/api/resource/server/',headers=headers,auth=auth,timeout=30)
        data = servers.text
        data = json.loads(data)
        servers = data.get('results')
        for server in servers:
            name = server.get('name')
            if server_to_connect == name:
                server_to_connect = server.get('id')
        query['connected_to_server'] = server_to_connect
        print(f"Updated Query: {query}")
        print(type(query))
        response=requests.post(data=json.dumps(query),url=f'{self.ngrok}sessionbot/api/devices/create/',headers=headers,auth=auth,timeout=30)
        print(response)
        if response.status_code == 200:
            return response.text
        else:
            return f"ResponseError: {response.status_code} - {response.text}"  
    def initialize_central_for_total_devices(self):
        """Initializes the Central for getting the total number of devices.""" 
        self.total_devices_tool = Tool(
            name="Total_devices",
            func=self.central_api_call_for_total_devices,
            description="Gets the total number of the devices from central using API call."
        )
    def central_api_call_for_total_devices(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/device/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        devices = data.get('count')
        return devices
    def initialize_central_for_device_details(self):
        """Initializes the Central for Device Details.""" 
        self.device_details_api_tool = Tool(
            name="Device_Details",
            func=self.central_api_call_for_device_details,
            description="Gets the details of the device from central using API call."
        )
    def central_api_call_for_device_details(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/device/',headers=headers, auth=auth,timeout=30)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        devices = data.get('results')
        
        names = []
        query = query.replace("\n","")
        query=query.replace("```","")
        print(f"Query for device details: {query} and its type: {type(query)}")
        for device in devices:
            name = device.get('name')
            if name == query:
                print(name)
                res=device
                return res
        else:
            return f"Device named {query} is not in the available devices."
    def initialize_central_for_device_update_info(self):
        """Initializes the Central for Device Info Update.""" 
        self.device_update_info_api_tool = Tool(
            name="Device_Update",
            func=self.central_api_call_for_device_update_info,
            description="Updates the details of the device from central using API call."
        )
    def central_api_call_for_device_update_info(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = query.replace("```","").replace("\n","")
        query = json.loads(query)
        device_id = query.get('id')
        query.pop('id')
        
        response = requests.patch(data=json.dumps(query), url=f"{self.ngrok}sessionbot/api/resource/device/{device_id}/", headers=headers, auth=auth,timeout=30)
        print(response)
        if response.status_code == 200:
            return response.text
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
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/device/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        devices = data.get('results')
        names = []
        
        for device in devices:
            name = device.get('name')
            names.append(name)
        if response.status_code == 200:
            return names
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_device_delete(self):
        """Initializes the Device Delete Process.""" 
        self.device_delete_tool = Tool(
            name="Device_Delete",
            func=self.central_api_call_for_device_delete,
            description="Takes the name of the device and deletes the device from central"
        )
    def central_api_call_for_device_delete(self, query): 
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url=f'{self.ngrok}sessionbot/api/resource/device/',headers=headers,timeout=30)
        data = resp.text
        data = json.loads(data)
        devices = data.get('results')
        query = query.replace("\n","")
        query = query.replace("```","")
        devices_ = [device.get('name') for device in devices]
        print(f"Query: {query} and type: {type(query)}")
        if query in devices_:
            for device in devices:
                name = device.get('name')
                serial_number = device.get('serial_number')
                if name == query:
                    print(f"Device Name :{name}, Serial Number: {serial_number}")
                    _resp=requests.delete(url=f'{self.ngrok}sessionbot/api/devices/delete/{serial_number}/',headers=headers, auth=auth, timeout=30)
                    print(_resp.text)
                    return _resp.text
        else:
            return "This device is not in the list of available devices."
    
    def initialize_device_delete_bulk(self):
        """Initializes the Device Delete Bulk Process.""" 
        self.device_delete_bulk_tool = Tool(
            name="Device_Delete_Bulk",
            func=self.task_body_creation_for_device_delete_bulk,
            description="Takes the names of the devices and delete the bots from central"
        )
    def task_body_creation_for_device_delete_bulk(self, query): 
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url='{self.ngrok}sessionbot/api/resource/device/',headers=headers,timeout=30,auth=auth)
        data = resp.text
        data = json.loads(data)
        devices = data.get('results')
        query = query.replace("\n","")
        query = query.replace("```","")
        devices_to_delete = query.split(', ')
        print(devices_to_delete)
        print(f"Query: {query} and type: {type(query)}")
        
        for device in devices:
            name = device.get('name')
            print(name)
            serial_number = device.get('serial_number')
            if name in devices_to_delete:
                print(f"Device :{name}, Serial Number: {serial_number}")
                _resp=requests.delete(url=f'{self.ngrok}sessionbot/api/devices/delete/{serial_number}/',headers=headers, auth =auth,timeout=30)
                print(_resp.text)
        return _resp.text

    def initialize_server_creation(self):
        """Initializes the Server Creation.""" 
        self.server_creation_task_body_tool = Tool(
            name="Task_Body_Creation_servers",
            func=self.task_body_creation_for_new_server,
            description="Creates the task body for Server creation tasks."
        )
    def task_body_creation_for_new_server(self, query): 
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.5, 
)
        #simple LLM:
        query = query.replace("```","").replace("\n","")
        print(f"\nAgent Query for Body Creation for New Server: {query}")
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=config,
            contents=f"""You have to precisely extract value of server name, public ip, maximum parallel tasks allowed and instance type from the {query} and"
            "after that you need to fill the folowing task body with those values precisely:"
            "Task body Example:"
            "{{
            
                "name": "from query",
                "public_ip": "from query",
                "maximum_parallel_tasks_allowed": from query,
                "instance_type": "from query"
        }}
        Each value should be extracted as it is from the {query}
        Once, you have filled this task body correctly, return it as your Final Answer as a valid JSON.
        """ 
        )
        json_output = response.text
        match = re.search(r"```json(.*)", json_output, re.DOTALL)
        if match:
            final_json_string = (match.group(1)).replace("```","")
        print(f"Completed task body: {final_json_string}")
        json_obj = json.loads(final_json_string)
        json_string = json.dumps(json_obj)
        
        return json_string
    def initialize_central_for_server_creation(self):
        """Initializes the Central for Server Creation.""" 
        self.server_creation_api_tool = Tool(
            name="Server_Creation",
            func=self.central_api_call_for_server_creation,
            description="Creates the server on central using the respective payload."
        )
    def central_api_call_for_server_creation(self, query):
        headers = {'Content-Type': 'application/json', 'username':'jeni','password':'jeni'}
        import json
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = query.replace("```","").replace("\n","")
        query = json.loads(query)
        print(type(query))
        
        response=requests.post(data=json.dumps(query),url=f'{self.ngrok}sessionbot/api/resource/server/',headers=headers,auth=auth,timeout=30)
        print(response)
        if response.status_code == 200 or response.status_code == 201:
            json_str = response.text
            return response.text
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_central_for_server_choices(self):
        """Initializes the Central for getting the choices for instance type of servers.""" 
        self.server_choices_tool = Tool(
            name="Server_Choices",
            func=self.central_api_call_for_server_choices,
            description="Gets the total number of the servers from central using API call."
        )
    def central_api_call_for_server_choices(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/server/choices/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        print(data)
        data = json.loads(data)
        choices = data.get('instance_type_choices')
        choices = choices.keys()
        return choices
    def initialize_central_for_total_servers(self):
        """Initializes the Central for getting the total number of servers.""" 
        self.total_servers_tool = Tool(
            name="Total_servers",
            func=self.central_api_call_for_total_servers,
            description="Gets the total number of the servers from central using API call."
        )
    def central_api_call_for_total_servers(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/server/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        servers = data.get('count')
        return servers
    def initialize_central_for_server_names(self):
        """Initializes the Central for server Names.""" 
        self.server_names_api_tool = Tool(
            name="Server_Names",
            func=self.central_api_call_for_server_names,
            description="Gets the names of the servers from central using API call."
        )
    def central_api_call_for_server_names(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/server/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        servers = data.get('results')
        names = []
        
        for server in servers:
            name = server.get('name')
            names.append(name)
        if response.status_code == 200:
            return names
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_central_for_server_details(self):
        """Initializes the Central for Server Details.""" 
        self.server_details_api_tool = Tool(
            name="Server_Details",
            func=self.central_api_call_for_server_details,
            description="Gets the details of the server from central using API call."
        )
    def central_api_call_for_server_details(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/server/',headers=headers, auth=auth,timeout=30)
        
        data = response.text
        data = json.loads(data)
        servers = data.get('results')
        
        names = []
        query = query.replace("```","")
        query = query.replace("\n","")
        for server in servers:
            name = server.get('name')
            print(name)
            server_id = server.get('id')
            if name == query:
                print(name)
                res=server
                return res
        else:
            return f"Server: {query} is not in the list of available servers."
    def initialize_central_for_server_update_info(self):
        """Initializes the Central for Server Info Update.""" 
        self.server_update_info_api_tool = Tool(
            name="Server_Update",
            func=self.central_api_call_for_server_update_info,
            description="Updates the details of the server from central using API call."
        )
    def central_api_call_for_server_update_info(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = query.replace("```","").replace("\n","")
        query = json.loads(query)
        server_id = query.get('id')
        query.pop('id')
        
        response = requests.patch(data=json.dumps(query), url=f"{self.ngrok}sessionbot/api/resource/server/{server_id}/", headers=headers, auth=auth)
        if response.status_code == 200:
            return response.text
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_server_delete(self):
        """Initializes the Server Delete Process.""" 
        self.server_delete_tool = Tool(
            name="Server_Delete",
            func=self.central_api_call_for_server_delete,
            description="Takes the name of the server and deletes the server from central"
        )
    def central_api_call_for_server_delete(self, query): 
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url=f'{self.ngrok}sessionbot/api/resource/server/',headers=headers,auth=auth,timeout=30)
        data = resp.text
        data = json.loads(data)
        servers = data.get('results')
        query = query.replace("\n","")
        query = query.replace("```","")
        print(f"Query: {query} and type: {type(query)}")
        servers_ = [server.get('name') for server in servers]
        print(servers_)
        if query in servers_:
            for server in servers:
                name = server.get('name')
                id = server.get('id')
                if name == query:
                    print(f"Server Name :{name}, Server ID: {id}")
                    _resp=requests.delete(url=f'{self.ngrok}sessionbot/api/resource/server/{id}/',headers=headers, auth=auth,timeout=30)
                    print(_resp)
                    if _resp.status_code == 204:
                        return f"The server named {name} has been deleted successfully."
        else:
            return "This server is not in the list of available servers"        
    def initialize_server_delete_bulk(self):
        """Initializes the Server Delete Bulk Process.""" 
        self.server_delete_bulk_tool = Tool(
            name="Server_Delete_Bulk",
            func=self.task_body_creation_for_server_delete_bulk,
            description="Takes the names of the servers and delete the servers from central"
        )
    def task_body_creation_for_server_delete_bulk(self, query): 
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url=f'{self.ngrok}sessionbot/api/resource/server/',headers=headers,auth=auth, timeout=30)
        data = resp.text
        query = query.replace("```","")
        query = query.replace("\n","")
        data = json.loads(data)
        servers = data.get('results')
        servers_ = [server.get('name') for server in servers]
        print(servers_)
        servers_to_delete = query.split(', ')
        check = ''
        for server in servers_to_delete:
            if server not in servers_:
                check = f'Server {server} is not present in the list of servers'
                servers_to_delete.remove(server)
            else:
                check = ''
        print(f"Servers to delete: {servers_to_delete}")
        print(f"Query: {query} and type: {type(query)}")
        for server in servers:
            name = server.get('name')
            print(name)
            id = server.get('id')
            if name in servers_to_delete:
                print(f"Device :{name}, ID: {id}")
                
                _resp=requests.delete(url=f'{self.ngrok}sessionbot/api/resource/server/{id}/',headers=headers, auth=auth,timeout=30)
                
                print(_resp.message,_resp.status)
        return _resp,check 

    def initialize_proxy_creation(self):
        """Initializes the Proxy Creation.""" 
        self.proxy_creation_task_body_tool = Tool(
            name="Task_Body_Creation_proxies",
            func=self.task_body_creation_for_new_proxy,
            description="Creates the task body for Proxy creation tasks."
        )
    def task_body_creation_for_new_proxy(self, query): 
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.5, # Set your desired temperature here
    # other parameters like top_p, top_k, max_output_tokens can also be set here
)
        #simple LLM:
        print(f"\nAgent Query for Body Creation for New Proxy: {query}")
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=config,
            contents=f"""You have to precisely extract value of spreadsheet URL from the {query} and"
            "after that you need to fill the folowing task body with those values precisely:"
            "Task body Example:"
            "{{
            "spreadsheet_url": "from query",
            "resource_type": "proxies",
            "request_id": "str(uuid.uuid1())"           
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
            
        return json_string

    def initialize_scrape_task_creation(self):
        """Initializes the Scrape Task Creation.""" 
        self.scrape_task_creation_task_body_tool = Tool(
            name="Task_Body_Creation_scrape_tasks",
            func=self.task_body_creation_for_new_scrape_task,
            description="Creates the task body for Scrape Tasks creation tasks."
        )
    def task_body_creation_for_new_scrape_task(self, query): 
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.5, 
)
        #simple LLM:
        print(f"\nAgent Query for Body Creation for New Scrape Task: {query}")
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=config,
            contents=f"""You have to precisely extract value of service, name, scrape type, scrape value, os, storage, childbot ids, max threads, max requests per day, start scraping and server id from the {query} and"
            "after that you need to fill the folowing task body with those values precisely:"
            "Task body Example:"
            "{{
                "method": "create",
                "data": [
                    {{
                    "service": "from query",                     
                    "name": "from query",                        
                    "scrape_type": "from query",                 
                    "scrape_value": "from query",                
                    "os": "from query",                          
                    "storage": "from query",                     
                    "childbot_ids": [from query,from query],               
                    "max_threads": "from query",              
                    "max_requests_per_day": "from query",    
                    "start_scraping": from query,          
                    "server_id": "from query"                   
                    }}
                ]
        }}
        Each value should be extracted as it is from the {query}
        Once, you have filled this task body correctly, return it as your Final Answer as a valid JSON.
        """ 
        )
        json_output = response.text
        match = re.search(r"```json(.*)", json_output, re.DOTALL)
        if match:
            final_json_string = (match.group(1)).replace("```","")
        print(f"Completed task body: {final_json_string}")
        json_obj = json.loads(final_json_string)
        json_string = json.dumps(json_obj)
        
        return json_string
    def initialize_central_for_scrape_task_creation(self):
        """Initializes the Central for Scrape Task Creation.""" 
        self.scrape_task_creation_api_tool = Tool(
            name="Scrape_Task_Creation_API_Calling",
            func=self.central_api_call_for_scrape_task_creation,
            description="Creates the Scrape Task on Central by using the user-provided updated payload in the query"
        )
    def central_api_call_for_scrape_task_creation(self, query):
        headers = {'Content-Type': 'application/json'}
        import json
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = json.loads(query)
        print(type(query))
        response=requests.post(data=json.dumps(query),url='{self.ngrok}sessionbot/api/scrapetask/',headers=headers, auth=auth, timeout=30)
        print(response)
        if response.status_code == 200:
            return response.text
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_central_for_scrape_task_details(self):
        """Initializes the Central for Scrape Task Details.""" 
        self.scrape_task_details_api_tool = Tool(
            name="Scrape_Task_Details",
            func=self.central_api_call_for_scrape_task_details,
            description="Gets the details of the scrape task from central using API call."
        )
    def central_api_call_for_scrape_task_details(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://78e0ff41aa61.ngrok-free.app/sessionbot/api/resource/scrapetask/',headers=headers, auth=auth,timeout=30)

        data = response.text
        data = json.loads(data)
        scrape_tasks = data.get('results')
        
        names = []
        query = query.replace("```","")
        query = query.replace("\n","")
        print(f"Query: {query} and its type: {type(query)}")
        for scrape_task in scrape_tasks:
            name = scrape_task.get('name')
            print(name)
            
            if name == query:
                print(name)
                res = scrape_task
                return res
                # _resp = requests.get(url = f'{self.ngrok}sessionbot/api/scrapetask/{scrape_task_id}/', headers=headers, auth=auth,timeout=30)
        # if _resp.status_code == 200:
            # return _resp.text
        else:
            return f"Scrape Task: {query} is not in the list of scrape tasks."
    def initialize_central_for_bots_of_scrape_task(self):
        """Initializes the Central for getting the bots used by a Scrape Task.""" 
        self.bots_of_scrape_task_api_tool = Tool(
            name="Get_bots_of_Scrape_Task",
            func=self.central_api_call_for_bots_of_scrape_task,
            description="Gets the bots that are used by a scrape task from central using API call."
        )
    def central_api_call_for_bots_of_scrape_task(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/scrapetask/',headers=headers, auth=auth,timeout=30)

        data = response.text
        data = json.loads(data)
        scrape_tasks = data.get('results')
        scrape_tasks_ = [st.get('name') for st in scrape_tasks]
        bot_names = []
        query = query.replace("```","")
        query = query.replace("\n","")
        if query in scrape_tasks_:
            for scrape_task in scrape_tasks:
                name = scrape_task.get('name')
                print(name)
                scrape_task_id = scrape_task.get('id')
                if name == query:
                    pl = {
                        "method":"get",
                        "data":{
                            "ids":[str(scrape_task_id)]
                        }
                    }
                    pl = json.dumps(pl)
                    print(pl)
                    _resp = requests.post(data=pl, url = f'{self.ngrok}sessionbot/api/scrapetask/', headers=headers, auth=auth,timeout=30)
                    data = _resp.text
                    data = json.loads(data)
                    print(data)
                    for st in data:
                        print(st)
                        st_ = st.get(str(scrape_task_id))
                        childbots = st_.get('childbot_ids')
                        print(childbots)
                
            for bot in childbots:
                bot_name = bot[1]
                bot_names.append(bot_name)
            return bot_names
        else:
            return "There's no scrape task with this name."
    def initialize_central_for_bot_details_for_scrape_task(self):
        """Initializes the Central for getting bot IDs of bots that will be used for scraping.""" 
        self.bot_details_for_scrape_task_api_tool = Tool(
            name="Bot_Details_for_Scrape_Task",
            func=self.central_api_call_for_bot_details_for_scrape_task,
            description="Gets the bot IDs of the bots that the user wants to use for scraping from central using API call."
        )
    def central_api_call_for_bot_details_for_scrape_task(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/profile/',headers=headers, auth=auth, timeout=30)

        data = response.text
        data = json.loads(data)
        bots = data.get('results')
        print(bots)
        bot_ids=[]
        for bot in bots:
            bot_ids.append(bot.get('id'))
            print(bot.get('display_name'), bot.get('id'))
        print(bot_ids)

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
        response=requests.get(url=f'https://78e0ff41aa61.ngrok-free.app/sessionbot/api/resource/scrapetask/',headers=headers, auth=auth,timeout=30)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        scrape_tasks = data.get('results')
        names = []
        for scrape_task in scrape_tasks:
            name = scrape_task.get('name')
            names.append(name)
        if response.status_code == 200:
            return names
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_central_for_total_scrape_tasks(self):
        """Initializes the Central for Total Scrape Tasks.""" 
        self.total_scrape_tasks_api_tool = Tool(
            name="Total_Scrape_Tasks",
            func=self.central_api_call_for_total_scrape_tasks,
            description="Gets the total number of the scrape tasks from central using API call."
        )
    def central_api_call_for_total_scrape_tasks(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/scrapetask/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        scrape_tasks = data.get('count')
        print(f"Query: {query} and type: {type(query)}")
        
        return scrape_tasks
    def initialize_central_for_pausing_scrape_tasks(self):
        """Initializes the Central for Pausing Scrape Tasks.""" 
        self.pause_scrape_tasks_api_tool = Tool(
            name="Pausing_Scrape_Tasks",
            func=self.central_api_call_for_pausing_scrape_tasks,
            description="Pauses the desired scrape task/s from central using API call."
        )
    def central_api_call_for_pausing_scrape_tasks(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.5,)
        query=query.replace("```","")
        query=query.replace("\n","")
        print(query)
        res = requests.get(url=f'{self.ngrok}sessionbot/api/resource/scrapetask/',headers=headers, auth=auth,timeout=30)
        data = res.text
        data = json.loads(data)
        scrape_tasks = data.get('results')
        scrape_tasks_ = [st.get('name') for st in scrape_tasks]
        print(scrape_tasks_)
        scrape_tasks_to_pause = query.split(',')
        check = ''
        ids = []
        ids_to_pause=[]
        for scrape_task in scrape_tasks_to_pause:
            if scrape_task not in scrape_tasks_:
                check = f'Scrape Task: {scrape_task} is not present in the list of Scrape Tasks.'
                scrape_tasks_to_pause.remove(scrape_task)
            else:
                check = ''
        print(f"Scrape Tasks to pause: {scrape_tasks_to_pause}")
        for scrape_task in scrape_tasks:
            name = scrape_task.get('name')
            id = scrape_task.get('id')
            if name in scrape_tasks_to_pause:
                ids.append(id)
        print(f"IDs: {ids}")

        for scrape_task in scrape_tasks:
            name = scrape_task.get('name')
            id = scrape_task.get('id')
            print(name)

            if name in scrape_tasks_to_pause and id in ids:
                print(id)
                ids_to_pause.append(id)
        if ids_to_pause != []:
            client = genai.Client()
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                config=config,
                contents=f"""You have to precisely extract value of scrape task/s id/s from the id/s: {ids_to_pause} and"
                "after that you need to fill the folowing task body with those values precisely:"
                "Task body Example:"
                "{{
                    "method": "change_state",
                    "data": {{
                        "action": "pause",       // pass the actual action here
                        "ids": ["from id/s", "from id/s"]}}
                    
            }}
            Once, you have filled this task body correctly, return it as your Final Answer as a valid JSON.
            """ 
            )
            json_output = response.text
            print(f"Output from LLM: {json_output} and its data type: {type(json_output)}")
            match = re.search(r"```json(.*)", json_output, re.DOTALL)
            if match:
                final_json_string = (match.group(1)).replace("```","")
            print(f"Completed task body: {final_json_string}")
        
            json_obj = json.loads(final_json_string)
            json_string = json.dumps(json_obj)
            print(f"Payload: {json_string} and its type: {type(json_string)}")
            response=requests.post(data=json_string,url=f'{self.ngrok}sessionbot/api/scrapetask/',headers=headers, auth=auth,timeout=30)
            data = response.text
            data = json.loads(data)
            success_message = data.get('message')
            return success_message, check
        else:
            return "You need to enter valid scrape task name/s in order to pause."    
    def initialize_central_for_resuming_scrape_tasks(self):
        """Initializes the Central for Resuming Scrape Tasks.""" 
        self.resume_scrape_tasks_api_tool = Tool(
            name="Resuming_Scrape_Tasks",
            func=self.central_api_call_for_resuming_scrape_tasks,
            description="Resumes the desired scrape task/s from central using API call."
        )
    def central_api_call_for_resuming_scrape_tasks(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.5,)
        query=query.replace("```","")
        query=query.replace("\n","")
        print(query)
        res = requests.get(url=f'{self.ngrok}sessionbot/api/resource/scrapetask/',headers=headers, auth=auth,timeout=30)
        data = res.text
        data = json.loads(data)
        scrape_tasks = data.get('results')
        scrape_tasks_ = [st.get('name') for st in scrape_tasks]
        print(scrape_tasks_)
        scrape_tasks_to_resume = query.split(',')
        check = ''
        ids = []
        ids_to_resume=[]
        for scrape_task in scrape_tasks_to_resume:
            if scrape_task not in scrape_tasks_:
                check = f'Scrape Task: {scrape_task} is not present in the list of Scrape Tasks.'
                scrape_tasks_to_resume.remove(scrape_task)
            else:
                check = ''
        print(f"Scrape Tasks to resume: {scrape_tasks_to_resume}")
        for scrape_task in scrape_tasks:
            name = scrape_task.get('name')
            id = scrape_task.get('id')
            if name in scrape_tasks_to_resume:
                ids.append(id)
        print(f"IDs: {ids}")

        for scrape_task in scrape_tasks:
            name = scrape_task.get('name')
            id = scrape_task.get('id')
            if name in scrape_tasks_to_resume and id in ids:
                print(id)
                ids_to_resume.append(id)
        print(ids_to_resume)
        if ids_to_resume != []:
            client = genai.Client()
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                config=config,
                contents=f"""You have to precisely extract value of scrape task/s id/s from the id/s: {ids_to_resume} and"
                "after that you need to fill the folowing task body with those values precisely:"
                "Task body Example:"
                "{{
                    "method": "change_state",
                    "data": {{
                        "action": "resume",       // pass the actual action here
                        "ids": ["from ids to resume", "from ids to resume"]}}
                    
            }}
            Once, you have filled this task body correctly, return it as your Final Answer as a valid JSON.
            """ 
            )
            json_output = response.text
            print(f"Output from LLM: {json_output} and its data type: {type(json_output)}")
            match = re.search(r"```json(.*)", json_output, re.DOTALL)
            if match:
                final_json_string = (match.group(1)).replace("```","")
            print(f"Completed task body: {final_json_string}")
            json_obj = json.loads(final_json_string)
            json_string = json.dumps(json_obj)
            print(f"Payload: {json_string} and its type: {type(json_string)}")
            response=requests.post(data=json_string,url=f'{self.ngrok}sessionbot/api/scrapetask/',headers=headers, auth=auth,timeout=30)
            data = response.text
            data = json.loads(data)
            success_message = data.get('message')
            return success_message, check
        else:
            return "You need to enter valid scrape task name/s in order to resume."
    def initialize_central_for_deleting_scrape_tasks(self):
        """Initializes the Central for Deleting Scrape Tasks.""" 
        self.delete_scrape_tasks_api_tool = Tool(
            name="Scrape_Task_Delete",
            func=self.central_api_call_for_deleting_scrape_tasks,
            description="Deletes the desired scrape task/s from central using API call."
        )
    def central_api_call_for_deleting_scrape_tasks(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.5,)
        query=query.replace("```","")
        query=query.replace("\n","")
        print(query)
        res = requests.get(url=f'{self.ngrok}sessionbot/api/resource/scrapetask/',headers=headers, auth=auth,timeout=30)
        data = res.text
        data = json.loads(data)
        scrape_tasks = data.get('results')
        scrape_tasks_ = [st.get('name') for st in scrape_tasks]
        print(scrape_tasks_)
        scrape_tasks_to_delete = query.split(',')
        check = ''
        ids = []
        ids_to_delete=[]
        for scrape_task in scrape_tasks_to_delete:
            if scrape_task not in scrape_tasks_:
                check = f'Scrape Task: {scrape_task} is not present in the list of Scrape Tasks.'
                scrape_tasks_to_delete.remove(scrape_task)
            else:
                check = ''
        print(f"Scrape Tasks to delete: {scrape_tasks_to_delete}")
        for scrape_task in scrape_tasks:
            name = scrape_task.get('name')
            id = scrape_task.get('id')
            if name in scrape_tasks_to_delete:
                ids.append(id)
        print(f"IDs: {ids}")

        for scrape_task in scrape_tasks:
            name = scrape_task.get('name')
            id = scrape_task.get('id')
            if name in scrape_tasks_to_delete and id in ids:
                print(id)
                ids_to_delete.append(id)
        print(ids_to_delete)
        if ids_to_delete != []:
            client = genai.Client()
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                config=config,
                contents=f"""You have to precisely extract value of scrape task/s id/s from the id/s: {ids_to_delete} and"
                "after that you need to fill the folowing task body with those values precisely:"
                "Task body Example:"
                "{{
                    "method": "delete",
                    "data": {{
                        "ids": ["from ids to delete"]
                    }}

                    
            }}
            Once, you have filled this task body correctly, return it as your Final Answer as a valid JSON.
            """ 
            )
            json_output = response.text
            print(f"Output from LLM: {json_output} and its data type: {type(json_output)}")
            match = re.search(r"```json(.*)", json_output, re.DOTALL)
            if match:
                final_json_string = (match.group(1)).replace("```","")
            print(f"Completed task body: {final_json_string}")
        
            json_obj = json.loads(final_json_string)
            json_string = json.dumps(json_obj)
            print(f"Payload: {json_string} and its type: {type(json_string)}")
            response=requests.post(data=json_string,url=f'{self.ngrok}sessionbot/api/scrapetask/',headers=headers, auth=auth,timeout=30)
            print(f"Status code for delete: {response.status_code}")
            print(f"Response text for delete: {response.text}")
            data = json.loads(response.text)
            status = data.get('status')
            if status=='success':
                return "The scrape task/s has/have been deleted successfully", check
        else:
            return "You need to enter valid scrape task name/s."
    
    def initialize_central_for_scrape_task_ids(self):
        """Initializes the Central for Scrape Task Names IDs.""" 
        self.scrape_task_ids_api_tool = Tool(
            name="Scrape_Task_IDs",
            func=self.central_api_call_for_scrape_task_ids,
            description="Gets the ids of the scrape tasks from central using API call."
        )
    def central_api_call_for_scrape_task_ids(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://78e0ff41aa61.ngrok-free.app/sessionbot/api/resource/scrapetask/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        query = query.replace("```","").replace("\n","")
        scrape_task_names = query.strip(", ")
        scrape_tasks = data.get('results')
        scrape_tasks_ = [st.get('name') for st in scrape_tasks]

        ids = []
        for scrape_task in scrape_tasks:
            name = scrape_task.get('name')
            id = scrape_task.get('id')
            if name in scrape_task_names:
                ids.append(id)
        if response.status_code == 200:
            return ids
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    def initialize_audience_creation_using_cleaning(self):
        """Initializes the Audience Creation with workflow step as Cleaning.""" 
        self.audience_creation_cleaning_task_body_tool = Tool(
            name="Cleaning_Step_for_Audience_Creation",
            func=self.task_body_creation_for_audience_creation_cleaning,
            description="Creates the task body for Audience Creation task with workflow step as Cleaning."
        )
    def task_body_creation_for_audience_creation_cleaning(self, query): 
        query = query.replace("```","").replace("\n","")
        print(f"Query: {query}")
        data = json.loads(query)
        print(f"Complete Query as Json: {data}")
        scrape_tasks = data.get('scrape_task_names')
        print(scrape_tasks)
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/scrapetask/',headers=headers, auth=auth,timeout=30)
        ids = []
        data = response.text
        data = json.loads(data)
        scrape_tasks_ = data.get('results')
        for st in scrape_tasks_:
            name = st.get('name')
            id = st.get('id')
            if name in scrape_tasks:
                ids.append(id)
        print(f"Scrape Task IDs: {ids}")
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.5, 
)
        #simple LLM:
        print(f"\nAgent Query for Body Creation for Audience Creation using Cleaning step: {query}")
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=config,
            contents=f"""You have to precisely extract value of audience name and openai api key from the {query} and scrape task ids from {ids} and"
            "after that you need to fill the folowing task body with those values precisely:"
            "These are the fields with their respective types, operators, etc. that you need to remember:"
            {{
                "name": {{
                    "type": "str",
                    "control": "text",
                    "label": "Name",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "followers_count": {{
                    "type": "integer",
                    "control": "number",
                    "label": "Followers Count",
                    "operators": ["range","eq", "neq", "gt", "gte", "lt", "lte", "is_empty", "is_not_empty"]
                }},
                "followings_count": {{
                    "type": "integer",
                    "control": "number",
                    "label": "Followings Count",
                    "operators": ["range","eq", "neq", "gt", "gte", "lt", "lte", "is_empty", "is_not_empty"]
                }},
                "post_count": {{
                    "type": "integer",
                    "control": "number",
                    "label": "Post Count",
                    "operators": ["range","eq", "neq", "gt", "gte", "lt", "lte", "is_empty", "is_not_empty"]
                }},
                "is_private": {{
                    "type": "boolean",
                    "control": "checkbox",
                    "label": "Is Private",
                    "operators": ["eq", "neq"]
                }},
                "bio": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Bio",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "gender": {{
                "type": "str",
                "control": "select",
                "label": "Gender",
                "options": [
                    {{ "value": "male", "label": "Male" }},
                    {{ "value": "female", "label": "Female" }},
                    {{ "value": "transgender", "label": "Transgender" }},
                    {{ "value": "None", "label": "Unknown" }}
                ],
                "operators": ["eq", "neq", "is_one_of", "is_empty", "is_not_empty"]
                }},
                "country": {{
                    "type": "str",
                    "control": "text",
                    "label": "Country",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_one_of", "is_empty", "is_not_empty"]
                }},
                "city": {{
                    "type": "str",
                    "control": "text",
                    "label": "City",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_one_of", "is_empty", "is_not_empty"]
                }},
                "interests": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Interests",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "profile_analysis": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Profile Analysis",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "keywords": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Keywords",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "phone_number": {{
                    "type": "str",
                    "control": "text",
                    "label": "Phone Number",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "email": {{
                    "type": "str",
                    "control": "text",
                    "label": "Email",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "external_accounts": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "External Accounts",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "age": {{
                    "type": "str",
                    "control": "text",
                    "label": "Age",
                    "operators": ["range","eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "category_name": {{
                    "type": "str",
                    "control": "text",
                    "label": "Category Name",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "possible_buying_interests": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Possible Buying Interests",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "interest_and_lifestyle_patterns": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Lifestyle Patterns",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "possible_buying_intent": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Buying Intent",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "financial_and_economic_status": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Financial and Economic Status",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "religion": {{
                    "type": "str",
                    "control": "select",
                    "label": "Religion",
                    "options" : ["Islam", "Christianity", "Hinduism", "Buddhism", "Judaism", "Sikhism", "Baháʼí Faith", "Jainism", "Shinto", "Taoism", "Zoroastrianism", "Atheism", "Agnosticism", "Other"],
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "account_type": {{
                    "type": "str",
                    "control": "select",
                    "label": "Account Type",
                    "options": [
                                {{ "value": "personal", "label": "Personal" }},
                                {{ "value": "business", "label": "Business" }},
                                {{ "value": "creator", "label": "Creator" }},
                                {{ "value": "other", "label": "Other" }}],
                    "operators": ["eq", "neq", "is_one_of", "is_empty", "is_not_empty"]
                }},
                "continent": {{
                    "type": "str",
                    "control": "select",
                    "label": "Continent",
                    "options": [
                                {{ "value": "asia", "label": "Asia" }},
                                {{"value": "usa", "label": "USA"}},
                                {{ "value": "europe", "label": "Europe" }},
                                {{ "value": "africa", "label": "Africa" }},
                                {{ "value": "oceania", "label": "Oceania" }},
                                {{ "value": "south america", "label": "South America" }},
                                {{ "value": "north america", "label": "North America" }}
                                ],
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_one_of", "is_empty", "is_not_empty"]
                }}
                }}
            "Let's take a look at a task body example for a user request that you can get from {query}. If the user request is to have the profiles whose age is greater than 15 and less than 50 and their gender is male, then the task body will look like the following:"
            "{{
                "method":"create",
                "generalConfig": {{
                    "settings": {{
                    "name": "audience name from query {query}",
                    "service": "instagram",
                    "scrapeTasks": ["scrape task ID from {ids}"],
                    "ai_service": "openai",
                    "api_key": "API key from query {query}",
                    "storage": {{
                        "save_to_googlesheet": false,
                        "google_sheet_url": ""
                    }}
                    }}
                }},
                "steps": [
                    {{
                    "step": 1,
                    "type": "cleaning",
                    "data": {{
                        "fields_to_compare": [
                        
                        {{ "key": "gender", "value": ["M"], "operator": "eq" }},
                        {{ "key": "age", "value": {{ "min": from query, "max": from query }}, "operator": "range" }},
                        ]
                    }}
                    }}
                    ]
                }}
        Each value in the fields in task body should be corresponding to the fields in the fields shown to you earlier. If the query {query} has gender male, the task body should have "M" in the value for gender field.
        Once, you have filled this task body correctly, return it as your Final Answer as a valid JSON.
        """ 
        )
        json_output = response.text
        match = re.search(r"```json(.*)", json_output, re.DOTALL)
        if match:
            final_json_string = (match.group(1)).replace("```","")
        print(f"Completed task body: {final_json_string}")
        json_obj = json.loads(final_json_string)
        scrape_task_ids = json_obj.get('generalConfig').get('settings').get('scrapeTasks')
        print(scrape_task_ids)
        json_string = json.dumps(json_obj)
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        res = requests.post(data=json_string,url=f'{self.ngrok}sessionbot/api/audience/',headers=headers, auth=auth,timeout=30)
        print(res.text)
        if res.text:
            return res.text
        else:
            return "Could not create audience"
    def initialize_audience_creation_using_data_enrichment(self):
        """Initializes the Audience Creation with workflow step as Data Enrichment.""" 
        self.audience_creation_data_enrichment_task_body_tool = Tool(
            name="Data_Enrichment_Step_for_Audience_Creation",
            func=self.task_body_creation_for_audience_creation_data_enrichment,
            description="Creates the task body for Audience Creation task with workflow step as Data Enrichment."
        )
    def task_body_creation_for_audience_creation_data_enrichment(self, query): 
        query = query.replace("```","").replace("\n","")
        start_index = query.find('{')
        end_index = query.rfind('}') + 1
        dict_string = query[start_index:end_index]
        json_string = json.dumps(dict_string)
        print("\nThe JSON string is:")
        print(json_string)
        print(f"Query: {json_string} and its type: {type(json_string)}")
        data = json.loads(json_string)
        print(f"Complete Query as Json: {data}")
        scrape_tasks = data.get('scrape_task_names')
        print(scrape_tasks)
        enrichment_type = data.get('enrichment_types')
        print(enrichment_type)
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/scrapetask/',headers=headers, auth=auth,timeout=30)
        ids = []
        data = response.text
        data = json.loads(data)
        scrape_tasks_ = data.get('results')
        for st in scrape_tasks_:
            name = st.get('name')
            id = st.get('id')
            if name in scrape_tasks:
                ids.append(id)
        print(f"Scrape Task IDs: {ids}")
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.5, 
)
        #simple LLM:
        print(f"\nAgent Query for Body Creation for Audience Creation using Cleaning step: {json_string}")
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=config,
            contents=f"""You have to precisely extract value of audience name and openai api key from the {json_string}, scrape task ids from {ids}, enrichment type from enrichment type: {enrichment_type} and"
            "after that you need to fill the folowing task body with those values precisely:"
            "These are the fields with their respective types, operators, etc. that you need to remember:"
            
            "Let's take a look at a task body example for a user request that you can get from {json_string}. If the user request is to have the profiles whose age is greater than 15 and less than 50 and their gender is male, then the task body will look like the following:"
            "{{
                "method":"create",
                "generalConfig": {{
                    "settings": {{
                    "name": "audience name from query {json_string}",
                    "service": "instagram",
                    "scrapeTasks": ["scrape task ID from {ids}"],
                    "ai_service": "openai",
                    "api_key": "API key from query {json_string}",
                    "storage": {{
                        "save_to_googlesheet": false,
                        "google_sheet_url": ""
                    }}
                    }}
                }},
                "steps": [
                    {{
                    "step": 1,
                    "type": "enrichments",
                    "data": {{
                        "enrichment_types:"from enrichment type: {enrichment_type}"
                    }}
                    }}
                    ]
                }}
        Once, you have filled this task body correctly, return it as your Final Answer as a valid JSON.
        """ 
        )
        json_output = response.text
        match = re.search(r"```json(.*)", json_output, re.DOTALL)
        if match:
            final_json_string = (match.group(1)).replace("```","")
        print(f"Completed task body: {final_json_string}")
        json_obj = json.loads(final_json_string)
        scrape_task_ids = json_obj.get('generalConfig').get('settings').get('scrapeTasks')
        print(scrape_task_ids)
        json_string = json.dumps(json_obj)
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        res = requests.post(data=json_string,url=f'{self.ngrok}sessionbot/api/audience/',headers=headers, auth=auth,timeout=30)
        print(res.text)
        if res.status_code==200:
            return res.text
        else:
            return "Could not create audience"
    def initialize_central_for_total_audiences(self):
        """Initializes the Central for getting the total number of audiences.""" 
        self.total_audiences_tool = Tool(
            name="Total_Audiences",
            func=self.central_api_call_for_total_audiences,
            description="Gets the total number of the audiences from central using API call."
        )
    def central_api_call_for_total_audiences(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://78e0ff41aa61.ngrok-free.app/sessionbot/api/resource/audience/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        audiences = data.get('count')
        return audiences
    def initialize_central_for_audience_names(self):
        """Initializes the Central for getting the names of audiences.""" 
        self.audiences_names_tool = Tool(
            name="Audience_Names",
            func=self.central_api_call_for_audience_names,
            description="Gets the names of the audiences from central using API call."
        )
    def central_api_call_for_audience_names(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://78e0ff41aa61.ngrok-free.app/sessionbot/api/resource/audience/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        audiences = data.get('results')
        names= []
        for audience in audiences:
            name = audience.get('name')
            names.append(name)
        return names
    def initialize_central_for_audience_details(self):
        """Initializes the Central for Audience Details.""" 
        self.audience_details_api_tool = Tool(
            name="Audience_Details",
            func=self.central_api_call_for_audience_details,
            description="Gets the details of the audience from central using API call."
        )
    def central_api_call_for_audience_details(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = query.replace("```","").replace("\n","")
        response=requests.get(url=f'{self.ngrok}sessionbot/api/resource/audience/',headers=headers, auth=auth)
        data = response.text
        data=json.loads(data)
        audiences = data.get('results')
        print(f"Query: {query} and its type: {type(query)}")
        for audience in audiences:
            name = audience.get('name')
            id = audience.get('id')
            print(id)
            if name == query:
                print(name)
                resp = audience
            

                return resp
        else:
            return f"Audience {query} not found in audiences"
    def initialize_audience_delete(self):
        """Initializes the Audience Delete Process.""" 
        self.audience_delete_tool = Tool(
            name="Audience_Delete",
            func=self.central_api_call_for_audience_delete,
            description="Takes the name of the audience and deletes the audience from central"
        )
    def central_api_call_for_audience_delete(self, query): 
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url=f'{self.ngrok}sessionbot/api/resource/audience/',headers=headers,auth=auth,timeout=30)
        data = resp.text
        data = json.loads(data)
        audiences = data.get('results')
        query = query.replace("\n","")
        query = query.replace("```","")
        print(f"Query: {query} and type: {type(query)}")
        audiences_ = [audience.get('name') for audience in audiences]
        print(audiences_)
        if query in audiences_:
            for audience in audiences:
                name = audience.get('name')
                id = audience.get('id')
                if name == query:
                    print(f"Audience Name :{name}, Audience ID: {id}")
                    _resp=requests.delete(url=f'{self.ngrok}sessionbot/api/resource/audience/{id}/',headers=headers, auth=auth,timeout=30)
                if _resp.status_code == 204:
                    return f"Audience named as: {query} has been successfully deleted."
        else:
            return f"Audience named as {query} is not in the list of available audiences"
    
    def initialize_reporting_for_scrape_task(self):
        """Initializes the Scrape task Reporting Process.""" 
        self.reporting_for_scrape_task_tool = Tool(
            name="Scrape_Task_Reporting",
            func=self.central_api_call_for_reporting_for_scrape_task,
            description="Takes the names of the scrape tasks and generates a report from central"
        )
    def central_api_call_for_reporting_for_scrape_task(self, query): 
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = query.replace("\n","")
        query = query.replace("```","")
        print(f"Query: {query} and type: {type(query)}")
        scrape_tasks_to_report = query.split(', ')
        resp=requests.get(url=f'{self.ngrok}sessionbot/api/resource/scrapetask/',headers=headers,auth=auth,timeout=120)
        data = resp.text
        data = json.loads(data)
        scrape_tasks = data.get('results')
        scrape_tasks_ = [st.get('name') for st in scrape_tasks]
        print(scrape_tasks_)
        ids = []
        for st in scrape_tasks:
            name = st.get('name')
            if name in scrape_tasks_to_report:
                print(st.get('name'))
                print(st.get('id'))
                ids.append(st.get('id'))
        
        print(ids)
        pl = {
            "object_type": "scrape_task",
            "chart_type": "bar",
            "selected_objects": ids
            }
        res = requests.post(data=json.dumps(pl), url=f"{self.ngrok}sessionbot/api/resource/reporting/", headers=headers, auth=auth, timeout=30)
        print(res.text)
        data = res.text
        data = json.loads(data)
        filename = "scrape_task_report.json"

        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        return res.text
    def initialize_reporting_for_bots(self):
        """Initializes the Bot Reporting Process.""" 
        self.reporting_for_bot_tool = Tool(
            name="Bots_Reporting",
            func=self.central_api_call_for_reporting_for_bot,
            description="Takes the names of the bots and generates a report from central"
        )
    def central_api_call_for_reporting_for_bot(self, query): 
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = query.replace("\n","")
        query = query.replace("```","")
        print(f"Query: {query} and type: {type(query)}")
        bots_to_report = query.split(', ')
        resp=requests.get(url=f'{self.ngrok}sessionbot/api/resource/profile/',headers=headers,auth=auth,timeout=30)
        data = resp.text
        data = json.loads(data)
        bots = data.get('results')
        bots_ = [bot.get('display_name') for bot in bots]
        print(bots_)
        ids = []
        for bot in bots:
            name = bot.get('display_name')
            if name in bots_to_report:
                print(bot.get('display_name'))
                print(bot.get('id'))
                ids.append(bot.get('id'))
        
        print(ids)
        pl = {
            "object_type": "bots",
            "chart_type": "bar",
            "selected_objects": ids,
            "bot_type":"browser_profile"
            }
        res = requests.post(data=json.dumps(pl), url=f"{self.ngrok}sessionbot/api/resource/reporting/", headers=headers, auth=auth, timeout=30)
        print(res.text)
        data = res.text
        data = json.loads(data)
        filename = "bot_report.json"

        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        return res.text
    def initialize_filtered_reporting_for_bots(self):
        """Initializes the Filtered Bot Reporting Process.""" 
        self.filtered_reporting_for_bot_tool = Tool(
            name="Bots_Reporting_Filtered",
            func=self.central_api_call_for_filtered_reporting_for_bot,
            description="Generates reports for the bots based on the conditions mentioned in the user query."
        )
    def central_api_call_for_filtered_reporting_for_bot(self, query): 
        query = query.replace("```","").replace("\n","")
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url=f'{self.ngrok}sessionbot/api/resource/profile/',headers=headers,auth=auth,timeout=30)
        data = resp.text
        data = json.loads(data)
        bots = data.get('results')
        bots_ = [bot.get('display_name') for bot in bots]
        print(len(bots_))
        ids = []
        for bot in bots:
            name = bot.get('display_name')
            ids.append(bot.get('id'))
        pl = {
            "object_type": "bots",
            "chart_type": "bar",
            "selected_objects": ids,
            "bot_type":"browser_profile"
            }
        res = requests.post(data=json.dumps(pl), url=f"{self.ngrok}sessionbot/api/resource/reporting/", headers=headers, auth=auth, timeout=200)
        print(res)
        data = res.text
        data = json.loads(data)
        summaries = data.get('Summaries')
        print(len(summaries))
        reports_with_incorrect_password = []
        bots_with_incorrect_passwords = []
        reports_with_proxy_issues = []
        bots_with_proxy_issues = []
        reports_with_challenge_page_identified = []
        bots_with_challenge_page_identified = []
        reports_with_all_login_issues = []
        bots_with_login_issues = []
        for report in summaries:
            if report.get('Critical Events'):
                if query == 'incorrect_password':
                    if 'incorrect_password' in report.get('Critical Events') or 'username_or_password_not_found' in report.get('Critical Events'):
                        reports_with_incorrect_password.append(report)
                        bots_with_incorrect_passwords.append(report.get('Bot Name'))
                elif query == 'proxy_issue':
                    if 'proxy_issue' in report.get('Critical Events'):
                        reports_with_proxy_issues.append(report)
                        bots_with_proxy_issues.append(report.get('Bot Name'))
                elif query == 'ChallengePage_identified':
                    if 'ChallengePage_identified' in report.get('Critical Events'):
                        reports_with_challenge_page_identified.append(report)
                        bots_with_challenge_page_identified.append(report.get('Bot Name'))
                elif query == 'all':
                    if 'ChallengePage_identified' in report.get('Critical Events') or 'incorrect_password' in report.get('Critical Events') or 'username_or_password_not_found' in report.get('Critical Events') or 'proxy_issue' in report.get('Critical Events'):
                        reports_with_all_login_issues.append(report)
                        bots_with_login_issues.append(report.get('Bot Name'))
        if query == 'incorrect_password':
            return bots_with_incorrect_passwords, len(bots_with_incorrect_passwords)
        elif query == 'proxy_issue':
            return bots_with_proxy_issues, len(bots_with_proxy_issues)
        elif query == 'ChallengePage_identified':
            return bots_with_challenge_page_identified, len(bots_with_challenge_page_identified)
        elif query == 'all':
            return bots_with_login_issues, len(bots_with_login_issues)
        # filename = "bot_report.json"
        # with open(filename, 'w') as json_file:
        #     json.dump(data, json_file, indent=4)
        # return bots_with_incorrect_passwords
    def initialize_reporting_for_devices(self):
        """Initializes the Devices Reporting Process.""" 
        self.reporting_for_devices_tool = Tool(
            name="Devices_Reporting",
            func=self.central_api_call_for_reporting_for_devices,
            description="Takes the names of the devices and generates a report from central"
        )
    def central_api_call_for_reporting_for_devices(self, query): 
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = query.replace("\n","")
        query = query.replace("```","")
        print(f"Query: {query} and type: {type(query)}")
        devices_to_report = query.split(', ')
        resp=requests.get(url=f'{self.ngrok}sessionbot/api/resource/device/',headers=headers,auth=auth,timeout=30)
        data = resp.text
        data = json.loads(data)
        devices = data.get('results')
        devices_ = [device.get('name') for device in devices]
        print(devices_)
        ids = []
        for device in devices:
            name = device.get('name')
            if name in devices_to_report:
                print(device.get('display_name'))
                print(device.get('id'))
                ids.append(device.get('id'))
        
        print(ids)
        pl = {
            "object_type": "bots",
            "chart_type": "bar",
            "selected_objects": ids,
            "bot_type":"device"
            }
        res = requests.post(data=json.dumps(pl), url=f"{self.ngrok}sessionbot/api/resource/reporting/", headers=headers, auth=auth, timeout=30)
        print(res.text)
        data = res.text
        data = json.loads(data)
        filename = "bot_report.json"

        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        return f"Report for Devices {devices_to_report} has been generated. You can download it. Do you want me to summarize the report for you?"
    def initialize_reporting_summary_for_scrape_task(self):
        """Initializes the Scrape task Reporting Summary Process.""" 
        self.reporting_summary_for_scrape_task_tool = Tool(
            name="Scrape_Task_Reporting_Summary",
            func=self.central_api_call_for_reporting_summary_for_scrape_task,
            description="Summarizes the Scrape Task report"
        )
    def central_api_call_for_reporting_summary_for_scrape_task(self, query): 
        file_path = 'scrape_task_report.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
        print(data)
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=config,
            contents=f"""You are an expert at summarizing reports which are in json format. Here is 
            a report {data} in JSON format. You just need to provide a summary in simple words of the whole report.
        """ 
        )
        print(response.text)
        json_output = response.text
        print(f"Output from LLM: {json_output}")
        return json_output
    def initialize_reporting_summary_for_bots(self):
        """Initializes the Bots Reporting Summary Process.""" 
        self.reporting_summary_for_bots_tool = Tool(
            name="Bots_Reporting_Summary",
            func=self.central_api_call_for_reporting_summary_for_bots,
            description="Summarizes the Bots report"
        )
    def central_api_call_for_reporting_summary_for_bots(self, query): 
        file_path = 'bot_report.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
        print(data)
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=config,
            contents=f"""You are an expert at summarizing reports which are in json format. Here is 
            a report {data} in JSON format. You just need to provide a summary in simple words of the whole report.
        """ 
        )
        print(response.text)
        json_output = response.text
        print(f"Output from LLM: {json_output}")
        return json_output
    def initialize_data_house_payload_tool(self):
        """Initializes the Data House Payload tool."""
        self.data_house_payload_tool= Tool(
            name="DH_Payload",
            func=self.data_house_func,
            description="Useful for when you need to create a payload for Data House."
        )
    def data_house_func(self, query):
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.6, # Set your desired temperature here
    # other parameters like top_p, top_k, max_output_tokens can also be set here
)
        #simple LLM:
        print(f"\nManager Query for Data House Payload Tool: {query}")
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=config,
            contents=f"""You are excellent at getting the names of the fields and values for the fields and after that converting those into a JSON payload. 
You will get a {query} which will include what the user wants to do and you need to create a payload understanding the {query}.
If the service name is not mentioned as instagram, twitter, facebook, etc. keep service as "instagram" by default. The "gender" field can have "male", "female" or None as values.
{{
                "name": {{
                    "type": "str",
                    "control": "text",
                    "label": "Name",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "followers_count": {{
                    "type": "integer",
                    "control": "number",
                    "label": "Followers Count",
                    "operators": ["range","eq", "neq", "gt", "gte", "lt", "lte", "is_empty", "is_not_empty"]
                }},
                "followings_count": {{
                    "type": "integer",
                    "control": "number",
                    "label": "Followings Count",
                    "operators": ["range","eq", "neq", "gt", "gte", "lt", "lte", "is_empty", "is_not_empty"]
                }},
                "post_count": {{
                    "type": "integer",
                    "control": "number",
                    "label": "Post Count",
                    "operators": ["range","eq", "neq", "gt", "gte", "lt", "lte", "is_empty", "is_not_empty"]
                }},
                "is_private": {{
                    "type": "boolean",
                    "control": "checkbox",
                    "label": "Is Private",
                    "operators": ["eq", "neq"]
                }},
                "bio": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Bio",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "gender": {{
                "type": "str",
                "control": "select",
                "label": "Gender",
                "options": [
                    {{ "value": "male", "label": "Male" }},
                    {{ "value": "female", "label": "Female" }},
                    {{ "value": "transgender", "label": "Transgender" }},
                    {{ "value": "None", "label": "Unknown" }}
                ],
                "operators": ["eq", "neq", "is_one_of", "is_empty", "is_not_empty"]
                }},
                "country": {{
                    "type": "str",
                    "control": "text",
                    "label": "Country",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_one_of", "is_empty", "is_not_empty"]
                }},
                "city": {{
                    "type": "str",
                    "control": "text",
                    "label": "City",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_one_of", "is_empty", "is_not_empty"]
                }},
                "interests": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Interests",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "profile_analysis": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Profile Analysis",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "keywords": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Keywords",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "phone_number": {{
                    "type": "str",
                    "control": "text",
                    "label": "Phone Number",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "email": {{
                    "type": "str",
                    "control": "text",
                    "label": "Email",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "external_accounts": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "External Accounts",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "age": {{
                    "type": "str",
                    "control": "text",
                    "label": "Age",
                    "operators": ["range","eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "category_name": {{
                    "type": "str",
                    "control": "text",
                    "label": "Category Name",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "possible_buying_interests": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Possible Buying Interests",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "interest_and_lifestyle_patterns": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Lifestyle Patterns",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "possible_buying_intent": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Buying Intent",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "financial_and_economic_status": {{
                    "type": "str",
                    "control": "textarea",
                    "label": "Financial and Economic Status",
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "religion": {{
                    "type": "str",
                    "control": "select",
                    "label": "Religion",
                    "options" : ["Islam", "Christianity", "Hinduism", "Buddhism", "Judaism", "Sikhism", "Baháʼí Faith", "Jainism", "Shinto", "Taoism", "Zoroastrianism", "Atheism", "Agnosticism", "Other"],
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_empty", "is_not_empty"]
                }},
                "account_type": {{
                    "type": "str",
                    "control": "select",
                    "label": "Account Type",
                    "options": [
                                {{ "value": "personal", "label": "Personal" }},
                                {{ "value": "business", "label": "Business" }},
                                {{ "value": "creator", "label": "Creator" }},
                                {{ "value": "other", "label": "Other" }}],
                    "operators": ["eq", "neq", "is_one_of", "is_empty", "is_not_empty"]
                }},
                "continent": {{
                    "type": "str",
                    "control": "select",
                    "label": "Continent",
                    "options": [
                                {{ "value": "asia", "label": "Asia" }},
                                {{"value": "usa", "label": "USA"}},
                                {{ "value": "europe", "label": "Europe" }},
                                {{ "value": "africa", "label": "Africa" }},
                                {{ "value": "oceania", "label": "Oceania" }},
                                {{ "value": "south america", "label": "South America" }},
                                {{ "value": "north america", "label": "North America" }}
                                ],
                    "operators": ["eq", "neq", "contains", "starts with", "ends with", "does not contain", "is_one_of", "is_empty", "is_not_empty"]
                }}
                }}
If the query {query} says followers greater than 100 then, the field in the payload will be represented like: "followers_count.gt":100.
After getting those values and fields, you need to create a payload for Data House like the following example:
        For example, if the query says, "Get me the social media profiles whose gender is male and whose age is less than 25", then the payload should be like the following:
        {{
             {{
                "filters": {{
                    "and_conditions":[{{
                        "service": "from query",
                        "respective_field.operator": "from query"}},
{{
                        "service": "from query",
                        "respective_field.operator": "from query"}}
                                }}]  
  }},
                "size": 5,
                "object_type": "profile"
}}            
        If the gender is specified as null, gender should be mentioned in the task body as **"gender.eq":null**.
        The "size" field is by default 5. If the query specifically has the number of profiles to get, then change the value for field "size" accordingly.
        Once, you have filled this payload precisely, return the payload only and do not include any extra text.
        """
        )
        json_output = response.text
        match = re.search(r"```json(.*)", json_output, re.DOTALL)
        # print(match)
        if match:
            final_json_string = (match.group(1)).replace("```","")
        print(f"Completed Data House Payload: {final_json_string}")
        json_obj = json.loads(final_json_string)
        json_string = json.dumps(json_obj,indent=None)
        datahouse_url = "http://208.109.241.136/datahouse/api/provide/" 
        headers = {'Content-Type': 'application/json'}
        
        try:
            print(f"Query from bot for DH API: {final_json_string} and its type: {type(final_json_string)}")
            query = json.loads(final_json_string)
            response = requests.post(datahouse_url, headers=headers, data=json.dumps(query))
            data = response.text
            data = json.loads(data)
            print(data.get('data'))
            import pandas as pd
            df = pd.DataFrame(data)
            
            print(df)
            filename = 'data'
            df.to_csv(f"{filename}.csv")
            if response.status_code == 200:
                return data.get('data')
            else:
                return f"ResponseError: {response.status_code} - {response.text}"
        except json.JSONDecodeError:
            return "ResponseError: Invalid JSON input provided."
        return final_json_string
    def initialiaze_DH_API_tool(self):
        """Initializes the Data House API tool."""
        self.data_house_api_calling_tool = Tool(
            name="DH_API_Calling",
            func=self.data_house_api_calling_func,
            description="Useful for when you need to make an API call to Data House."
        )
    def data_house_api_calling_func(self, query: str) -> str:
        """
        An Agent to make an API call to retrieve the data from Data House.
        """
        """
    #     Simulates making a POST request to an API endpoint.
    #     Input should be a JSON string representing the payload.
    #     """
        datahouse_url = "http://http://208.109.241.136/datahouse/api/provide/" 
        headers = {'Content-Type': 'application/json'}
        
        try:
            print(f"Query from bot for DH API: {query} and its type: {type(query)}")
            query = json.loads(query)
            response = requests.post(datahouse_url, headers=headers, data=json.dumps(query))
            data = response.text
            data = json.loads(data)
            print(data)
            if response.status_code == 200:
                return response.text
            else:
                return f"ResponseError: {response.status_code} - {response.text}"
        except json.JSONDecodeError:
            return "ResponseError: Invalid JSON input provided."
        except requests.exceptions.RequestException as e:
            return f"ResponseError: Request failed - {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
    def create_datahouse_agent(self):
        """
        Creates and initializes the Datahouse Agent.
        This agent orchestrates the user query handling and efficient tool calling with respect to the user query.
        """
        datahouse_agent_tools = [self.data_house_payload_tool]
        
        datahouse_agent_runnable = create_react_agent(self.llm, datahouse_agent_tools, datahouse_agent_prompt)
        self.datahouse_agent_executor = AgentExecutor(
            agent=datahouse_agent_runnable,
            tools=datahouse_agent_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=self.shared_memory_datahouse
        )
    def invoke_datahouse_agent(self):
        """Initializes the Datahouse agent.""" 
        self.datahouse_ops_tool = Tool(
            name="DH_Ops",
            func=self.datahouse_data_fetching,
            description="Understands the user query and call respective tool from available tools accordingly."
        )
    def datahouse_data_fetching(self, query: str) -> str:
        """
        An agent to handle all the queries related to Datahouse (Datahouse data fetching for social media profiles).
        """
        print(f"\n---Manager calling Datahouse Agent with query: {query}---")
        response = self.datahouse_agent_executor.invoke({"input": query})
            
        save_memory(serialize_messages(self.datahouse_agent_executor.memory.chat_memory.messages), 'agent/datahouse_memory.json')
        return response['output']
    def create_bots_crud_agent(self):
        """
        Creates and initializes the Bots CRUD Agent.
        This agent performs all the necessary actions required for CRUD operations for bots.
        """
        
        bot_crud_tools = [self.bot_creation_api_tool,self.bots_logged_in_api_tool,self.bot_creation_task_body_tool,self.bot_names_api_tool, self.total_bots_tool, self.bot_details_api_tool, self.bot_delete_tool, self.bot_update_api_tool, self.bot_update_info_api_tool,self.filtered_reporting_for_bot_tool]
        bots_crud_agent_runnable = create_react_agent(self.llm, bot_crud_tools, bot_crud_agent_prompt)
        self.bots_crud_agent_executor = AgentExecutor(
            agent=bots_crud_agent_runnable,
            tools=bot_crud_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=self.shared_memory_bot
        )
    def invoke_bots_crud(self):
        """Initializes the Bot CRUD agent.""" 
        self.bots_crud_tool = Tool(
            name="Bots_CRUD",
            func=self.bot_crud_func,
            description="Understands the user query and call respective tool from available tools accordingly."
        )
    def bot_crud_func(self, query: str) -> str:
        """
        An agent to handle all the queries related to Bots (CRUD operations for Bots).
        """
        print(f"\n---Manager calling Bots CRUD Agent with query: {query}---")
        
        response = self.bots_crud_agent_executor.invoke({"input": query})
            
        save_memory(serialize_messages(self.bots_crud_agent_executor.memory.chat_memory.messages),'agent/bots_memory.json')
        return response['output']
    def create_devices_crud_agent(self):
        """
        Creates and initializes the Devices CRUD Agent.
        This agent performs all the necessary actions required for CRUD operations for devices.
        """
        device_crud_tools = [self.device_creation_api_tool,self.device_creation_task_body_tool, self.total_devices_tool, self.device_details_api_tool, self.device_names_api_tool, self.device_delete_tool, self.device_update_info_api_tool,self.server_names_api_tool,self.device_delete_bulk_tool]
        device_crud_agent_runnable = create_react_agent(self.llm, device_crud_tools, device_crud_agent_prompt)
        self.devices_crud_agent_executor = AgentExecutor(
            agent=device_crud_agent_runnable,
            tools=device_crud_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=self.shared_memory_device
        )
    def invoke_devices_crud(self):
        """Initializes the Devices CRUD agent.""" 
        self.devices_crud_tool = Tool(
            name="Devices_CRUD",
            func=self.device_crud_func,
            description="Understands the user query related to devices and call respective tool from available tools accordingly."
        )
    def device_crud_func(self, query: str) -> str:
        """
        An agent to handle all the queries related to Devices (CRUD operations for Devices).
        """
        print(f"\n---Manager calling Devices CRUD Agent with query: {query}---")
    
            # Invoke the agent with a query that requires a tool call
        response = self.devices_crud_agent_executor.invoke({"input": query})
        
        save_memory(serialize_messages(self.devices_crud_agent_executor.memory.chat_memory.messages),'agent/devices_memory.json')
        return response['output']
    def create_servers_crud_agent(self):
        """
        Creates and initializes the Servers CRUD Agent.
        This agent performs all the necessary actions required for CRUD operations for servers.
        """
        server_crud_tools = [self.server_creation_task_body_tool,self.server_creation_api_tool,self.server_choices_tool,self.total_servers_tool,self.server_names_api_tool,self.server_details_api_tool,self.server_update_info_api_tool,self.server_delete_tool,self.server_delete_bulk_tool]
        server_crud_agent_runnable = create_react_agent(self.llm, server_crud_tools, server_crud_agent_prompt)
        self.server_crud_agent_executor = AgentExecutor(
            agent=server_crud_agent_runnable,
            tools=server_crud_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=self.shared_memory_server
        )
    def invoke_servers_crud(self):
        """Initializes the Servers CRUD agent.""" 
        self.servers_crud_tool = Tool(
            name="Servers_CRUD",
            func=self.server_crud_func,
            description="Understands the user query related to servers and call respective tool from available tools accordingly."
        )
    def server_crud_func(self, query: str) -> str:
        """
        An agent to handle all the queries related to Servers (CRUD operations for Servers).
        """
        print(f"\n---Manager calling Servers CRUD Agent with query: {query}---")
    
            # Invoke the agent with a query that requires a tool call
        response = self.server_crud_agent_executor.invoke({"input": query})
        
        save_memory(serialize_messages(self.server_crud_agent_executor.memory.chat_memory.messages),'agent/servers_memory.json')
        return response['output']
    def create_scrapetasks_crud_agent(self):
        """
        Creates and initializes the Scrape Tasks CRUD Agent.
        This agent performs all the necessary actions required for CRUD operations for scrape tasks.
        """
        scrape_task_crud_tools = [self.scrape_task_creation_task_body_tool,self.scrape_task_creation_api_tool,self.scrape_task_details_api_tool,self.scrape_task_names_api_tool, self.pause_scrape_tasks_api_tool, self.resume_scrape_tasks_api_tool,self.delete_scrape_tasks_api_tool,self.bots_of_scrape_task_api_tool,self.bot_names_api_tool,self.bot_details_for_scrape_task_api_tool]
        scrape_task_crud_agent_runnable = create_react_agent(self.llm, scrape_task_crud_tools, scrape_task_crud_agent_prompt)
        self.scrape_task_crud_agent_executor = AgentExecutor(
            agent=scrape_task_crud_agent_runnable,
            tools=scrape_task_crud_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=self.shared_memory_scrape_task
        )
    def invoke_scrape_tasks_crud(self):
        """Initializes the Scrape Tasks CRUD agent.""" 
        self.scrape_tasks_crud_tool = Tool(
            name="Scrape_Tasks_CRUD",
            func=self.scrape_task_crud_func,
            description="Understands the user query related to scrape tasks and call respective tool from available tools accordingly."
        )
    def scrape_task_crud_func(self, query: str) -> str:
        """
        An agent to handle all the queries related to Scrpae Tasks (CRUD operations for Scrape Tasks).
        """
        print(f"\n---Manager calling Scrape Tasks CRUD Agent with query: {query}---")
    
            # Invoke the agent with a query that requires a tool call
        response = self.scrape_task_crud_agent_executor.invoke({"input": query})
        
        save_memory(serialize_messages(self.scrape_task_crud_agent_executor.memory.chat_memory.messages),'agent/scrape_tasks_memory.json')
        return response['output']
    def create_audience_crud_agent(self):
        """
        Creates and initializes the Audiences CRUD Agent.
        This agent performs all the necessary actions required for CRUD operations for scrape tasks.
        """
        audience_crud_tools = [self.scrape_task_names_api_tool,self.scrape_task_ids_api_tool,self.audience_creation_cleaning_task_body_tool,self.total_audiences_tool,self.audience_details_api_tool, self.audiences_names_tool,self.audience_delete_tool,self.audience_creation_data_enrichment_task_body_tool]
        audience_crud_agent_runnable = create_react_agent(self.llm, audience_crud_tools, audience_crud_agent_prompt)
        self.audience_crud_agent_executor = AgentExecutor(
            agent=audience_crud_agent_runnable,
            tools=audience_crud_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=self.shared_memory_audience
        )
    def invoke_audience_crud(self):
        """Initializes the audience CRUD agent.""" 
        self.audience_crud_tool = Tool(
            name="Audiences_CRUD",
            func=self.audience_crud_func,
            description="Understands the user query related to audiences and call respective tool from available tools accordingly."
        )
    def audience_crud_func(self, query: str) -> str:
        """
        An agent to handle all the queries related to Audiences (CRUD operations for Audiences).
        """
        print(f"\n---Manager calling Audiences CRUD Agent with query: {query}---")
    
            # Invoke the agent with a query that requires a tool call
        response = self.audience_crud_agent_executor.invoke({"input": query})
        
        save_memory(serialize_messages(self.audience_crud_agent_executor.memory.chat_memory.messages),'agent/audiences_memory.json')
        return response['output']
    def create_reporting_crud_agent(self):
        """ 
        Creates and initializes the Reporting CRUD Agent.
        This agent performs all the necessary actions required for CRUD operations for reporting.
        """
        reporting_crud_tools = [self.reporting_for_scrape_task_tool,self.reporting_summary_for_scrape_task_tool,self.reporting_for_bot_tool,self.reporting_summary_for_bots_tool,self.reporting_for_devices_tool,self.filtered_reporting_for_bot_tool]
        reporting_crud_agent_runnable = create_react_agent(self.llm, reporting_crud_tools, reporting_crud_agent_prompt)
        self.reporting_crud_agent_executor = AgentExecutor(
            agent=reporting_crud_agent_runnable,
            tools=reporting_crud_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=self.shared_memory_reporting
        )
    def invoke_reporting_crud(self):
        """Initializes the reporting CRUD agent.""" 
        self.reporting_crud_tool = Tool(
            name="Reportings_CRUD",
            func=self.reporting_crud_func,
            description="Understands the user query related to reporting and call respective tool from available tools accordingly."
        )
    def reporting_crud_func(self, query: str) -> str:
        """
        An agent to handle all the queries related to Reporting (CRUD operations for Reporting).
        """
        print(f"\n---Manager calling Reporting CRUD Agent with query: {query}---")
    
            # Invoke the agent with a query that requires a tool call
        response = self.reporting_crud_agent_executor.invoke({"input": query})
        
        save_memory(serialize_messages(self.reporting_crud_agent_executor.memory.chat_memory.messages),'agent/reportings_memory.json')
        return response['output']
    def create_manager_agent(self):
        """
        Creates and initializes the Manager Agent.
        This agent orchestrates the user query handling and efficient tool calling with respect to the user query.
        """
        manager_tools = [self.bots_crud_tool,self.datahouse_ops_tool, self.devices_crud_tool,self.servers_crud_tool,self.scrape_tasks_crud_tool,self.audience_crud_tool,self.reporting_crud_tool]
        
        manager_agent_runnable = create_react_agent(self.llm, manager_tools, f4f_manager_prompt)
        self.manager_agent_executor = AgentExecutor(
            agent=manager_agent_runnable,
            tools=manager_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=self.shared_memory
        )

    def initialize(self):
        """Initializes all components: LLM, RAG, and all agents."""
        self.initialize_llm_and_rag()
        if not self.llm or not self.rag_tool:
            print("Initialization failed: LLM or RAG tool not set up.")
            return False
        self.create_bots_crud_agent()
        self.create_datahouse_agent()
        self.create_devices_crud_agent()
        self.create_servers_crud_agent()
        self.create_scrapetasks_crud_agent()
        self.create_audience_crud_agent()
        self.create_reporting_crud_agent()
        self.create_manager_agent()

        self.is_initialized = True
        return True

    def chat_with_agent(self, user_input: str) -> Dict[str, Any]:
        """
        Takes the user query and forwards it to Bots_CRUD tool as it is.
        """
        print(f"-----Query for Manager Agent: {user_input}-----")
        from langchain.callbacks import get_openai_callback
        with get_openai_callback() as cb:
            # Invoke the agent with a query that requires a tool call
            response = self.manager_agent_executor.invoke({"input": user_input})
            self.manager_tokens = cb.total_tokens
            self.manager_input_tokens = cb.prompt_tokens
            self.manager_output_tokens = cb.completion_tokens
            # # Print the token usage from the callback object
            print("\n--- Callback Token Usage for Manager Agent---")
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
    
        
        save_memory(serialize_messages(self.manager_agent_executor.memory.chat_memory.messages), 'agent/manager_memory.json')

        return response['output']

