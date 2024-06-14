# import os

# os.environ["OPENAI_API_KEY"] = ""
# os.environ["groq_api_key"] = "d"

db_user = "read"
db_password = "12345"
db_host = "localhost"
db_name = "contoh"

from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
# from langchain_openai import ChatOpenAI
# from langchain_groq import ChatGroq
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.llms import Ollama


db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")
# llm = ChatGroq(model_name="mixtral-8x7b-32768", temperature=0, max_tokens=2500)
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
llm = Ollama(model="llama3")


# ---
# Testing db
# ---
# print(db.get_usable_table_names())
# print(db.table_info)


# ---
# perintahkan langchain untuk membuat query ke database berdasar dari informasi database dari db
# ---
generate_query = create_sql_query_chain(llm, db)
query = generate_query.invoke({"question": "what is price of `1968 Ford Mustang`"})



# jalankan hasil query buatan langchain
execute_query = QuerySQLDataBaseTool(db=db,verbose=True)
# execute_query.invoke(query)


chain = generate_query | execute_query
# response = chain.invoke({"question": "How many orders are there"})

# print(chain)
# print(response)

# chain.get_prompts()[0].pretty_print()


from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Given the following user question, corresponding SQL query, and SQL result, answer the user question. 
# Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks. 
# Do not use backslash (\) to escape underscores (_) in column names. 

answer_prompt = PromptTemplate.from_template(
    """
    You have access to our MySQL database, given the following user Question, corresponding SQL query, \
    and SQL result, answer the user question. Write only the SQL Query and nothing else, no pre-amble.

    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: 
    """
)

rephrase_answer = answer_prompt | llm | StrOutputParser()

chain = (
    RunnablePassthrough.assign(query=generate_query).assign(
        result=itemgetter("query") | execute_query
    )
    | rephrase_answer
)

response = chain.invoke({"question": "Tell me 5 employee name"})

print(response)