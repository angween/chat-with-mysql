from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
from flask import Flask, request


def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
  db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
  return SQLDatabase.from_uri(db_uri)


def get_sql_chain(db, llm):
  template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
    
    <SCHEMA>{schema}</SCHEMA>
    
    Conversation History: {chat_history}
    
    Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks. 
    Do not use backslash (\) to escape underscores (_) in column names. 
    
    For example:
    Question: which 3 artists have the most tracks?
    SQL Query: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;
    Question: Name 10 artists
    SQL Query: SELECT Name FROM Artist LIMIT 10;
    
    Your turn:
    
    Question: {question}
    SQL Query:
    """
    
  prompt = ChatPromptTemplate.from_template(template)
  
  def get_schema(_):
    return db.get_table_info()
  
  return (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | llm
    | StrOutputParser()
  )


def get_response(user_query: str, db: SQLDatabase, chat_history: list, llm: Ollama):
  sql_chain = get_sql_chain(db, llm)
  
  template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, question, sql query, and sql response, write a natural language response without including
    the SQL query.
    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    User question: {question}
    SQL Response: {response}"""
    
  prompt = ChatPromptTemplate.from_template(template)
  
  chain = (
    RunnablePassthrough.assign(query=sql_chain).assign(
      query=lambda vars: vars["query"],
      schema=lambda _: db.get_table_info(),
      response=lambda vars: db.run(vars["query"]),
    )
    | prompt
    | llm
    | StrOutputParser()
  )
  
  return chain.invoke({
    "question": user_query,
    "chat_history": chat_history,
  })


db_user = "read"
db_password = "12345"
db_host = "localhost"
db_name = "accounting"

db = init_database(
    db_user,
    db_password,
    db_host,
    '3306',
    db_name
)

app = Flask(__name__)
llm = Ollama(model="llama3", temperature=0)
chat_history = []

@app.route("/ai", methods=["POST"])
def aiPost():
    json_content = request.json

    user_query = json_content.get("query")

    # print(f"\nQuestion:\n{user_query}")

    response = get_response(user_query, db, chat_history, llm)

    # print(f"\nAnswer:\n{response}\n==================================\n")

    chat_history.append({
      'question': user_query,
      'answer': response
    })
    
    return response


def start_app():
    app.run(host="0.0.0.0", port=8080, debug=True)


if __name__ == "__main__":
    start_app()