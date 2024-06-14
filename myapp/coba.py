import os
# import subprocess
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
# from langchain_groq import ChatGroq
from langchain_community.llms import Ollama
# from langchain_community.chat_models import chatgroc
        
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
# from langchain_community.agent_toolkits import SQLDatabaseToolkit
# from langchain.agents.agent_types import AgentType
# from langchain.chat_models import ChatOpenAI
# from langchain.llms.openai import OpenAI
from langchain.sql_database import SQLDatabase


os.environ['OPENAI_API_KEY'] = "your_openai_api_key"
os.environ["SERPAPI_API_KEY"] = "dfb43c9bac528617738c27528ab2669f7329791e01fe8bbdcd10d29186df5360"

mysql_db = SQLDatabase.from_uri("mysql://read:12345@localhost:3306/accounting") 

llm = ChatGroq(model_name="mixtral-8x7b-32768",temperature=0)
# llm = Ollama(model="llama3")

tools = load_tools(["serpapi", "llm-math"], llm=llm)

tools_with_mysql = [tool for tool in tools]  # Copy existing tools
tools_with_mysql.append(SQLDatabaseToolkit(db=mysql_db,llm=llm))  # Add MySQL database toolkit

# agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
agent = initialize_agent(tools_with_mysql, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
agent.run("Tell me about this database.")

