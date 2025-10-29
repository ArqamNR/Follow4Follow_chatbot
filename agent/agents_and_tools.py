def create_devices_crud_agent(self):
        """
        Creates and initializes the Bots CRUD Agent.
        This agent performs all the necessary actions required for CRUD operations for bots.
        """
        device_crud_tools = [self.device_creation_api_tool,self.device_creation_task_body_tool,self.device_names_api_tool, self.total_devices_tool, self.device_details_api_tool, self.device_delete_tool, self.device_update_api_tool, self.device_update_info_api_tool, self.device_delete_bulk_tool]
        device_crud_agent_runnable = create_react_agent(self.llm, device_crud_tools, device_crud_agent_prompt)
        self.devices_crud_agent_executor = AgentExecutor(
            agent=device_crud_agent_runnable,
            tools=device_crud_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=devices_memory 
        )
    def invoke_devices_crud(self):
        """Initializes the Devices CRUD agent.""" 
        self.device_crud_tool = Tool(
            name="Devices_CRUD",
            func=self.device_crud_func,
            description="Understands the user query related to devices and call respective tool from available tools accordingly."
        )
    def device_crud_func(self, query: str) -> str:
        """
        An agent to handle all the queries related to Devices (CRUD operations for Devices).
        """
        print(f"\n---Manager calling Devices CRUD Agent with query: {query}---")
        from langchain.callbacks import get_openai_callback
        with get_openai_callback() as cb:
    # Invoke the agent with a query that requires a tool call
            response = self.devices_crud_agent_executor.invoke({"input": query})
            
            # Print the token usage from the callback object
            print("\n--- Callback Token Usage for Devices Agent---")
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
            
            save_memory(serialize_messages(self.devices_crud_agent_executor.memory.chat_memory.messages),'devices_memory.json')
        return response['output']
    def create_servers_crud_agent(self):
        """
        Creates and initializes the Servers CRUD Agent.
        This agent performs all the necessary actions required for CRUD operations for servers.
        """
        server_crud_tools = [self.server_creation_api_tool,self.server_creation_task_body_tool,self.server_names_api_tool,self.server_names_api_tool, self.total_servers_tool, self.server_details_api_tool, self.server_delete_tool, self.server_update_info_api_tool, self.server_delete_bulk_tool]
        server_crud_agent_runnable = create_react_agent(self.llm, server_crud_tools, server_crud_agent_prompt)
        self.servers_crud_agent_executor = AgentExecutor(
            agent=server_crud_agent_runnable,
            tools=server_crud_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=servers_memory
        )
    def invoke_servers_crud(self):
        """Initializes the Servers CRUD agent.""" 
        self.server_crud_tool = Tool(
            name="Servers_CRUD",
            func=self.server_crud_func,
            description="Understands the user query related to servers and call respective tool from available tools accordingly."
        )
    def server_crud_func(self, query: str) -> str:
        """
        An agent to handle all the queries related to Servers (CRUD operations for Servers).
        """
        print(f"\n---Manager calling Servers CRUD Agent with query: {query}---")
        from langchain.callbacks import get_openai_callback
        with get_openai_callback() as cb:
    # Invoke the agent with a query that requires a tool call
            response = self.servers_crud_agent_executor.invoke({"input": query})
            
            # Print the token usage from the callback object
            print("\n--- Callback Token Usage for Servers Agent---")
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
            
            save_memory(serialize_messages(self.servers_crud_agent_executor.memory.chat_memory.messages),'servers_memory.json')
        return response['output']
    def create_proxies_crud_agent(self):
        """
        Creates and initializes the Proxies CRUD Agent.
        This agent performs all the necessary actions required for CRUD operations for proxies.
        """
        proxies_crud_tools = [self.bot_creation_api_tool,self.bot_creation_task_body_tool,self.device_names_api_tool,self.bot_names_api_tool, self.total_bots_tool, self.bot_details_api_tool, self.bot_delete_tool, self.bot_update_api_tool, self.bot_update_info_api_tool]
        proxies_crud_agent_runnable = create_react_agent(self.llm, proxies_crud_tools, proxy_crud_agent_prompt)
        self.proxies_crud_agent_executor = AgentExecutor(
            agent=proxies_crud_agent_runnable,
            tools=proxies_crud_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=proxies_memory
        )
    def invoke_proxies_crud(self):
        """Initializes the Proxies CRUD agent.""" 
        self.proxy_crud_tool = Tool(
            name="Proxies_CRUD",
            func=self.proxy_crud_func,
            description="Understands the user query related to proxies and call respective tool from available tools accordingly."
        )
    def proxy_crud_func(self, query: str) -> str:
        """
        An agent to handle all the queries related to Proxies (CRUD operations for Proxies).
        """
        print(f"\n---Manager calling Proxies CRUD Agent with query: {query}---")
        from langchain.callbacks import get_openai_callback
        with get_openai_callback() as cb:
    # Invoke the agent with a query that requires a tool call
            response = self.proxies_crud_agent_executor.invoke({"input": query})
            
            # Print the token usage from the callback object
            print("\n--- Callback Token Usage for Proxies Agent---")
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
            
            save_memory(serialize_messages(self.proxies_crud_agent_executor.memory.chat_memory.messages),'proxies_memory.json')
        return response['output']
    # def create_audiences_crud_agent(self):
    #     """
    #     Creates and initializes the Audiences CRUD Agent.
    #     This agent performs all the necessary actions required for CRUD operations for audiences.
    #     """
    #     audience_crud_tools = [self.audience_creation_task_body_tool,self.audience_names_api_tool,self.audience_names_api_tool, self.total_audiences_tool, self.audience_details_api_tool, self.audience_delete_tool, self.audience_update_info_api_tool, self.audience_delete_bulk_tool]
    #     audience_crud_agent_runnable = create_react_agent(self.llm, audience_crud_tools, audience_crud_agent_prompt)
    #     self.audience_crud_agent_executor = AgentExecutor(
    #         agent=audience_crud_agent_runnable,
    #         tools=audience_crud_tools,
    #         return_intermediate_steps=True,
    #         verbose=True,
    #         handle_parsing_errors=True,
    #         memory=audiences_memory
    #     )
    def invoke_audiences_crud(self):
        """Initializes the Audiences CRUD agent.""" 
        self.audience_crud_tool = Tool(
            name="Audiences_CRUD",
            func=self.audience_crud_func,
            description="Understands the user query related to audience and call respective tool from available tools accordingly."
        )
    def audience_crud_func(self, query: str) -> str:
        """
        An agent to handle all the queries related to Audiences (CRUD operations for Audiences).
        """
        print(f"\n---Manager calling Audiences CRUD Agent with query: {query}---")
        from langchain.callbacks import get_openai_callback
        with get_openai_callback() as cb:
    # Invoke the agent with a query that requires a tool call
            response = self.audience_crud_agent_executor.invoke({"input": query})
            
            # Print the token usage from the callback object
            print("\n--- Callback Token Usage for Audience Agent---")
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
            
            save_memory(serialize_messages(self.audience_crud_agent_executor.memory.chat_memory.messages),'audiences_memory.json')
        return response['output']
    def create_scrape_tasks_crud_agent(self):
        """
        Creates and initializes the Scrape Tasks CRUD Agent.
        This agent performs all the necessary actions required for CRUD operations for scrape tasks.
        """
        scrape_task_crud_tools = [self.bot_creation_api_tool,self.bot_creation_task_body_tool,self.device_names_api_tool,self.bot_names_api_tool, self.total_bots_tool, self.bot_details_api_tool, self.bot_delete_tool, self.bot_update_api_tool, self.bot_update_info_api_tool]
        scrape_task_crud_agent_runnable = create_react_agent(self.llm, scrape_task_crud_tools, scrape_task_crud_agent_prompt)
        self.scrape_task_crud_agent_executor = AgentExecutor(
            agent=scrape_task_crud_agent_runnable,
            tools=scrape_task_crud_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=scrape_tasks_memory
        )
    def invoke_scrape_tasks_crud(self):
        """Initializes the Scrape Tasks CRUD agent.""" 
        self.scrape_tasks_crud_tool = Tool(
            name="Scrape_Tasks_CRUD",
            func=self.scrape_tasks_crud_func,
            description="Understands the user query related to scrape tasks and call respective tool from available tools accordingly."
        )
    def scrape_tasks_crud_func(self, query: str) -> str:
        """
        An agent to handle all the queries related to Scrape Tasks (CRUD operations for Scrape Tasks).
        """
        print(f"\n---Manager calling Scrape Tasks CRUD Agent with query: {query}---")
        from langchain.callbacks import get_openai_callback
        with get_openai_callback() as cb:
    # Invoke the agent with a query that requires a tool call
            response = self.scrape_task_crud_agent_executor.invoke({"input": query})
            
            # Print the token usage from the callback object
            print("\n--- Callback Token Usage for Scrape Tasks Agent---")
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
            
            save_memory(serialize_messages(self.scrape_task_crud_agent_executor.memory.chat_memory.messages),'scrape_tasks_memory.json')
        return response['output']
    def create_reports_crud_agent(self):
        """
        Creates and initializes the Reports CRUD Agent.
        This agent performs all the necessary actions required for CRUD operations for reports.
        """
        report_crud_tools = [self.bot_creation_api_tool,self.bot_creation_task_body_tool,self.device_names_api_tool,self.bot_names_api_tool, self.total_bots_tool, self.bot_details_api_tool, self.bot_delete_tool, self.bot_update_api_tool, self.bot_update_info_api_tool]
        report_crud_agent_runnable = create_react_agent(self.llm, report_crud_tools, report_crud_agent_prompt)
        self.reports_crud_agent_executor = AgentExecutor(
            agent=report_crud_agent_runnable,
            tools=report_crud_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=reports_memory
        )
    def invoke_reports_crud(self):
        """Initializes the Reports CRUD agent.""" 
        self.report_crud_tool = Tool(
            name="Reports_CRUD",
            func=self.report_crud_func,
            description="Understands the user query related to reports and call respective tool from available tools accordingly."
        )
    def report_crud_func(self, query: str) -> str:
        """
        An agent to handle all the queries related to Reports (CRUD operations for Reports).
        """
        print(f"\n---Manager calling Reports CRUD Agent with query: {query}---")
        from langchain.callbacks import get_openai_callback
        with get_openai_callback() as cb:
    # Invoke the agent with a query that requires a tool call
            response = self.reports_crud_agent_executor.invoke({"input": query})
            
            # Print the token usage from the callback object
            print("\n--- Callback Token Usage for Reports Agent---")
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
            
            save_memory(serialize_messages(self.reports_crud_agent_executor.memory.chat_memory.messages),'reports_memory.json')
        return response['output']
    def create_datahouse_crud_agent(self):
        """
        Creates and initializes the Data House CRUD Agent.
        This agent performs all the necessary actions required for CRUD operations for data house.
        """
        datahouse_crud_tools = [self.bot_creation_api_tool,self.bot_creation_task_body_tool,self.device_names_api_tool,self.bot_names_api_tool, self.total_bots_tool, self.bot_details_api_tool, self.bot_delete_tool, self.bot_update_api_tool, self.bot_update_info_api_tool]
        datahouse_crud_agent_runnable = create_react_agent(self.llm, datahouse_crud_tools, datahouse_crud_agent_prompt)
        self.datahouse_crud_agent_executor = AgentExecutor(
            agent=datahouse_crud_agent_runnable,
            tools=datahouse_crud_tools,
            return_intermediate_steps=True,
            verbose=True,
            handle_parsing_errors=True,
            memory=datahouse_memory
        )
    def invoke_datahouse_crud(self):
        """Initializes the datahouse CRUD agent.""" 
        self.datahouse_crud_tool = Tool(
            name="Datahouse_fetch",
            func=self.datahouse_fetch_func,
            description="Understands the user query related to getting/fetching data from Data house and call respective tool from available tools accordingly."
        )
    def datahouse_fetch_func(self, query: str) -> str:
        """
        An agent to handle all the queries related to Data House (Data fetching).
        """
        print(f"\n---Manager calling Datahouse data fetching Agent with query: {query}---")
        from langchain.callbacks import get_openai_callback
        with get_openai_callback() as cb:
    # Invoke the agent with a query that requires a tool call
            response = self.datahouse_crud_agent_executor.invoke({"input": query})
            
            # Print the token usage from the callback object
            print("\n--- Callback Token Usage for Datahouse Agent---")
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
            
            save_memory(serialize_messages(self.datahouse_crud_agent_executor.memory.chat_memory.messages),'datahouse_memory.json')
        return response['output']

def initialize_device_creation(self):
        """Initializes the Device Creation.""" 
        self.device_creation_task_body_tool = Tool(
            name="Task_Body_Creation_devices",
            func=self.task_body_creation_for_new_device,
            description="Creates the task body for Device creation tasks."
        )
def task_body_creation_for_new_device(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
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
        contents=f"""You have to precisely extract value of device name, serial number, server, os, brand and model from the {query} and"
        "after that you need to fill the folowing task body with those values precisely:"
        "Task body Example:"
        "{{
        "name": "from query",
        "serial_number": "from query",
        "connected_to_server": from query,
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
    query = json.loads(query)
    print(type(query))
    response=requests.post(data=json.dumps(query),url='https://3108a95be43e.ngrok-free.app/sessionbot/api/devices/create/',headers=headers,auth=auth)
    print(response)
    if response.status_code == 200:
        json_str = response.text
        parsed_data = json.loads(json_str)

        # Extract the 'data' list
        data_list = parsed_data['data']
        return data_list
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
    response=requests.get(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/device/',headers=headers, auth=auth)
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
    response=requests.get(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/device/',headers=headers, auth=auth)
    # print(response.text)
    data = response.text
    data = json.loads(data)
    devices = data.get('results')
    
    names = []
    
    for device in devices:
        name = device.get('name')
        print(name)
        id = device.get('id')
        if name == query:
            _resp = requests.get(url = f'https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/device/{id}/', headers=headers, auth=auth)
            # print(_resp.text)
    if _resp.status_code == 200:
        return _resp.text
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
    response=requests.get(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/device/',headers=headers, auth=auth)
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
def initialize_central_for_device_update_info(self):
    """Initializes the Central for Device Info Update.""" 
    self.device_update_info_api_tool = Tool(
        name="Device_Update",
        func=self.central_api_call_for_device_update_info,
        description="Updates the details of the bot from central using API call."
    )
def central_api_call_for_device_update_info(self, query):
    headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
    from requests.auth import HTTPBasicAuth
    auth=HTTPBasicAuth('jeni', 'jeni@123')
    query = json.loads(query)
    bot_id = query.get('id')
    query.pop('id')
    
    response = requests.patch(data=json.dumps(query), url=f"https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/device/{bot_id}/", headers=headers, auth=auth)
    if response.status_code == 200:
        return response
    else:
        return f"ResponseError: {response.status_code} - {response.text}"
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
    resp=requests.get(url='https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/device/',headers=headers)
    data = resp.text
    data = json.loads(data)
    devices = data.get('results')
    
    print(f"Query: {query} and type: {type(query)}")
    for device in devices:
        name = device.get('name')
        serial_number = device.get('serial_number')
        if name == query:
            print(f"Device Name :{name}, Serial Number: {serial_number}")
            _resp=requests.delete(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/devices/delete/{serial_number}/',headers=headers, auth =auth)
            print(_resp.text)
    return _resp.text
def initialize_device_delete_bulk(self):
    """Initializes the Device Delete Bulk Process.""" 
    self.device_delete_bulk_tool = Tool(
        name="Device_Delete_Bulk",
        func=self.task_body_creation_for_device_delete_bulk,
        description="Takes the names of the devices and delete the bots from central"
    )
def task_body_creation_for_device_delete_bulk(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
    headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
    from requests.auth import HTTPBasicAuth
    auth=HTTPBasicAuth('jeni', 'jeni@123')
    resp=requests.get(url='https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/device/',headers=headers)
    data = resp.text
    data = json.loads(data)
    devices = data.get('results')
    devices_to_delete = query.split(', ')
    print(f"Query: {query} and type: {type(query)}")
    for device in devices_to_delete:
        print(device)
        for device in devices:
            name = device.get('display_name')
            serial_number = device.get('serial_number')
            if name == device:
                print(f"Device :{name}, Serial Number: {serial_number}")
                _resp=requests.delete(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/devices/delete/{serial_number}/',headers=headers, auth =auth)
                print(_resp.text)
    return _resp.text
    def initialize_server_creation(self):
        """Initializes the Server Creation.""" 
        self.server_creation_task_body_tool = Tool(
            name="Task_Body_Creation_servers",
            func=self.task_body_creation_for_new_server,
            description="Creates the task body for Server creation tasks."
        )
    def task_body_creation_for_new_server(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.5, # Set your desired temperature here
    # other parameters like top_p, top_k, max_output_tokens can also be set here
)
        #simple LLM:
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
        query = json.loads(query)
        print(type(query))
        response=requests.post(data=json.dumps(query),url='https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/server/',headers=headers,auth=auth)
        print(response)
        if response.status_code == 200:
            json_str = response.text
            parsed_data = json.loads(json_str)

            # Extract the 'data' list
            data_list = parsed_data['data']
            return data_list
        else:
            return f"ResponseError: {response.status_code} - {response.text}"  
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
        response=requests.get(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/server/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        devices = data.get('count')
        return devices
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
        response=requests.get(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/server/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        servers = data.get('results')
        
        names = []
        
        for server in servers:
            name = server.get('name')
            print(name)
            server_id = server.get('id')
            if name == query:
                _resp = requests.get(url = f'https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/device/{server_id}/', headers=headers, auth=auth)
                # print(_resp.text)
        if _resp.status_code == 200:
            return _resp.text
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    
    def initialize_central_for_server_names(self):
        """Initializes the Central for server Names.""" 
        self.server_names_api_tool = Tool(
            name="Server_Names",
            func=self.central_api_call_for_server_names,
            description="Gets the name of the servers from central using API call."
        )
    def central_api_call_for_server_names(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/server/',headers=headers, auth=auth)
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
        query = json.loads(query)
        server_id = query.get('id')
        query.pop('id')
        
        response = requests.patch(data=json.dumps(query), url=f"https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/server/{server_id}/", headers=headers, auth=auth)
        if response.status_code == 200:
            return response
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
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
        resp=requests.get(url='https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/server/',headers=headers)
        data = resp.text
        data = json.loads(data)
        servers = data.get('results')
        
        print(f"Query: {query} and type: {type(query)}")
        for server in servers:
            name = server.get('name')
            id = server.get('id')
            if name == query:
                print(f"Server Name :{name}, IDNumber: {id}")
                _resp=requests.delete(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/devices/delete/{id}/',headers=headers, auth =auth)
                print(_resp.text)
        return _resp.text
    def initialize_server_delete_bulk(self):
        """Initializes the Server Delete Bulk Process.""" 
        self.server_delete_bulk_tool = Tool(
            name="Server_Delete_Bulk",
            func=self.task_body_creation_for_server_delete_bulk,
            description="Takes the names of the servers and delete the servers from central"
        )
    def task_body_creation_for_server_delete_bulk(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url='https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/server/',headers=headers)
        data = resp.text
        data = json.loads(data)
        servers = data.get('results')
        servers_to_delete = query.split(', ')
        print(f"Query: {query} and type: {type(query)}")
        for server in servers_to_delete:
            print(server)
            for server in servers:
                name = server.get('name')
                id = server.get('id')
                if name == server:
                    print(f"Server :{name}, ID: {id}")
                    _resp=requests.delete(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/resource/server/{id}/',headers=headers, auth =auth)
                    print(_resp.text)
        return _resp.text
    def initialize_audience_creation(self):
        """Initializes the Audience Creation.""" 
        self.audience_creation_task_body_tool = Tool(
            name="Task_Body_Creation_audiences",
            func=self.task_body_creation_for_new_audience,
            description="Creates the task body for Audience creation tasks."
        )
    def task_body_creation_for_new_audience(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
        from google.genai import types
        config = types.GenerateContentConfig(
        temperature=0.5, # Set your desired temperature here
    # other parameters like top_p, top_k, max_output_tokens can also be set here
)
        #simple LLM:
        print(f"\nAgent Query for Body Creation for New Server: {query}")
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=config,
            contents=f"""You have to precisely extract value of generalConfig and steps from the {query} and"
            "after that you need to fill the folowing task body with those values precisely:"
            "Task body Example:"
            "{{
            
                "generalConfig": "from query",
                "steps": "from query",   
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
    def initialize_central_for_audience_creation(self):
        """Initializes the Central for Audience Creation.""" 
        self.audience_creation_api_tool = Tool(
            name="Audience_Creation",
            func=self.central_api_call_for_audience_creation,
            description="Creates the audience on central using the respective payload."
        )
    def central_api_call_for_audience_creation(self, query):
        headers = {'Content-Type': 'application/json', 'username':'jeni','password':'jeni'}
        import json
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = json.loads(query)
        print(type(query))
        response=requests.post(data=json.dumps(query),url='https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/create/',headers=headers,auth=auth)
        print(response)
        if response.status_code == 200:
            json_str = response.text
            parsed_data = json.loads(json_str)

            # Extract the 'data' list
            data_list = parsed_data['data']
            return data_list
        else:
            return f"ResponseError: {response.status_code} - {response.text}"  
    def initialize_central_for_total_audiences(self):
        """Initializes the Central for getting the total number of audiences.""" 
        self.total_audiences_tool = Tool(
            name="Total_audiences",
            func=self.central_api_call_for_total_audiences,
            description="Gets the total number of the audiences from central using API call."
        )
    def central_api_call_for_total_audiences(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        devices = data.get('count')
        return devices
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
        response=requests.get(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        audiences = data.get('results')
        
        names = []
        
        for audience in audiences:
            name = audience.get('name')
            print(name)
            id = audience.get('id')
            if name == query:
                _resp = requests.get(url = f'https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/{id}/', headers=headers, auth=auth)
                # print(_resp.text)
        if _resp.status_code == 200:
            return _resp.text
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    
    def initialize_central_for_audience_names(self):
        """Initializes the Central for audience Names.""" 
        self.audience_names_api_tool = Tool(
            name="Audience_Names",
            func=self.central_api_call_for_audience_names,
            description="Gets the name of the audiences from central using API call."
        )
    def central_api_call_for_audience_names(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/',headers=headers, auth=auth)
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
    def initialize_central_for_audience_update_info(self):
        """Initializes the Central for Audience Info Update.""" 
        self.audience_update_info_api_tool = Tool(
            name="Audience_Update",
            func=self.central_api_call_for_audience_update_info,
            description="Updates the details of the audience from central using API call."
        )
    def central_api_call_for_audience_update_info(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = json.loads(query)
        audience_id = query.get('id')
        query.pop('id')
        
        response = requests.patch(data=json.dumps(query), url=f"https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/{audience_id}/", headers=headers, auth=auth)
        if response.status_code == 200:
            return response
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
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
        resp=requests.get(url='https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/',headers=headers)
        data = resp.text
        data = json.loads(data)
        audiences = data.get('results')
        
        print(f"Query: {query} and type: {type(query)}")
        for audience in audiences:
            name = audience.get('name')
            id = audience.get('id')
            if name == query:
                print(f"Server Name :{name}, IDNumber: {id}")
                _resp=requests.delete(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/{id}/',headers=headers, auth =auth)
                print(_resp.text)
        return _resp.text
    def initialize_audience_delete_bulk(self):
        """Initializes the Audience Delete Bulk Process.""" 
        self.audience_delete_bulk_tool = Tool(
            name="Audience_Delete_Bulk",
            func=self.task_body_creation_for_audience_delete_bulk,
            description="Takes the names of the audiences and delete the audiences from central"
        )
    def task_body_creation_for_audience_delete_bulk(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url='https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/',headers=headers)
        data = resp.text
        data = json.loads(data)
        audiences = data.get('results')
        audiences_to_delete = query.split(', ')
        print(f"Query: {query} and type: {type(query)}")
        for audience in audiences_to_delete:
            print(audience)
            for audience in audiences:
                name = audience.get('name')
                id = audience.get('id')
                if name == audience:
                    print(f"Server :{name}, ID: {id}")
                    _resp=requests.delete(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/server/{id}/',headers=headers, auth =auth)
                    print(_resp.text)
        return _resp.text
    def initialize_proxy_creation(self):
        """Initializes the Proxy Creation.""" 
        self.proxy_creation_task_body_tool = Tool(
            name="Task_Body_Creation_proxies",
            func=self.task_body_creation_for_new_proxy,
            description="Creates the task body for Proxy creation tasks."
        )
    def task_body_creation_for_new_proxy(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
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
    def initialize_central_for_audience_creation(self):
        """Initializes the Central for Audience Creation.""" 
        self.audience_creation_api_tool = Tool(
            name="Audience_Creation",
            func=self.central_api_call_for_audience_creation,
            description="Creates the audience on central using the respective payload."
        )
    def central_api_call_for_audience_creation(self, query):
        headers = {'Content-Type': 'application/json', 'username':'jeni','password':'jeni'}
        import json
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = json.loads(query)
        print(type(query))
        response=requests.post(data=json.dumps(query),url='https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/create/',headers=headers,auth=auth)
        print(response)
        if response.status_code == 200:
            json_str = response.text
            parsed_data = json.loads(json_str)

            # Extract the 'data' list
            data_list = parsed_data['data']
            return data_list
        else:
            return f"ResponseError: {response.status_code} - {response.text}"  
    def initialize_central_for_total_audiences(self):
        """Initializes the Central for getting the total number of audiences.""" 
        self.total_audiences_tool = Tool(
            name="Total_audiences",
            func=self.central_api_call_for_total_audiences,
            description="Gets the total number of the audiences from central using API call."
        )
    def central_api_call_for_total_audiences(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        devices = data.get('count')
        return devices
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
        response=requests.get(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/',headers=headers, auth=auth)
        # print(response.text)
        data = response.text
        data = json.loads(data)
        audiences = data.get('results')
        
        names = []
        
        for audience in audiences:
            name = audience.get('name')
            print(name)
            id = audience.get('id')
            if name == query:
                _resp = requests.get(url = f'https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/{id}/', headers=headers, auth=auth)
                # print(_resp.text)
        if _resp.status_code == 200:
            return _resp.text
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
    
    def initialize_central_for_audience_names(self):
        """Initializes the Central for audience Names.""" 
        self.audience_names_api_tool = Tool(
            name="Audience_Names",
            func=self.central_api_call_for_audience_names,
            description="Gets the name of the audiences from central using API call."
        )
    def central_api_call_for_audience_names(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        response=requests.get(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/',headers=headers, auth=auth)
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
    def initialize_central_for_audience_update_info(self):
        """Initializes the Central for Audience Info Update.""" 
        self.audience_update_info_api_tool = Tool(
            name="Audience_Update",
            func=self.central_api_call_for_audience_update_info,
            description="Updates the details of the audience from central using API call."
        )
    def central_api_call_for_audience_update_info(self, query):
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        query = json.loads(query)
        audience_id = query.get('id')
        query.pop('id')
        
        response = requests.patch(data=json.dumps(query), url=f"https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/{audience_id}/", headers=headers, auth=auth)
        if response.status_code == 200:
            return response
        else:
            return f"ResponseError: {response.status_code} - {response.text}"
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
        resp=requests.get(url='https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/',headers=headers)
        data = resp.text
        data = json.loads(data)
        audiences = data.get('results')
        
        print(f"Query: {query} and type: {type(query)}")
        for audience in audiences:
            name = audience.get('name')
            id = audience.get('id')
            if name == query:
                print(f"Server Name :{name}, IDNumber: {id}")
                _resp=requests.delete(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/{id}/',headers=headers, auth =auth)
                print(_resp.text)
        return _resp.text
    def initialize_audience_delete_bulk(self):
        """Initializes the Audience Delete Bulk Process.""" 
        self.audience_delete_bulk_tool = Tool(
            name="Audience_Delete_Bulk",
            func=self.task_body_creation_for_audience_delete_bulk,
            description="Takes the names of the audiences and delete the audiences from central"
        )
    def task_body_creation_for_audience_delete_bulk(self, query): #This particular func should return a json string always as it is necessary to be an input for another tool.
        headers = {'Content-Type': 'application/json','username':'jeni','password':'jeni',}
        from requests.auth import HTTPBasicAuth
        auth=HTTPBasicAuth('jeni', 'jeni@123')
        resp=requests.get(url='https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/',headers=headers)
        data = resp.text
        data = json.loads(data)
        audiences = data.get('results')
        audiences_to_delete = query.split(', ')
        print(f"Query: {query} and type: {type(query)}")
        for audience in audiences_to_delete:
            print(audience)
            for audience in audiences:
                name = audience.get('name')
                id = audience.get('id')
                if name == audience:
                    print(f"Server :{name}, ID: {id}")
                    _resp=requests.delete(url=f'https://3108a95be43e.ngrok-free.app/sessionbot/api/audience/server/{id}/',headers=headers, auth =auth)
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
        response=requests.post(data=json.dumps(query),url='https://3108a95be43e.ngrok-free.app/sessionbot/api/scrapetask/',headers=headers, auth=auth)
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
    