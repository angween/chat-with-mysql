import os
# from langchain.agents import *
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.llms import Ollama
# from langchain.sql_database import SQLDatabase
# from langchain_groq import ChatGroq
# from langchain.llms import OpenAI
# from langchain.chat_models import ChatOpenAI
# from langchain_community.chat_models import ChatOpenAI

db_user = "read"
db_password = "12345"
db_host = "localhost"
db_name = "contoh"


# llm = ChatOpenAI(model_name="gpt-3.5-turbo")
# llm = ChatGroq(model_name="mixtral-8x7b-32768", temperature=0, max_tokens=2500)
llm = Ollama(model="llama3")

db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

toolkit = SQLDatabaseToolkit(llm=llm, db=db)

agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True
)


# Prompt the user for input
# user_prompt = input("Please enter your prompt: ")
# agent_executor.run("Find the top 5 products with the highest total sales revenue")

# Run the agent with the user-provided prompt
# agent_executor.run(user_prompt)


# agent_executor.run("Describe the tables that start with journal on its name and how they are related")

# agent_executor.run("Describe the PurchaseDetails table")


while True:
    prompt = input("\nPlease enter your prompt: ")

    if (prompt == 'exit'):
        break

    response = agent_executor.run(prompt)
    # agent_executor.invoke(input=prompt)

    print(response)

