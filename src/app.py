import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
# from langchain_openai import ChatOpenAI
# from langchain_groq import ChatGroq
# from langchain_community.chat_models import ChatGroq

def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
  db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
  return SQLDatabase.from_uri(db_uri)


def get_sql_chain(db, llm):
  # Conversation History: {chat_history}
  # Do not use backslash (\) to escape underscores (_) in column names. 

  template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, write a SQL query that would answer the user's question. Avoid ambiguous query by using alias.
    
    <SCHEMA>{schema}</SCHEMA>

    Write only the SQL query and nothing else because we will run your query to retrieves data. Do not wrap the SQL query in any other text, not even backticks. 
    
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
  
  # llm = ChatOpenAI(model="gpt-4-0125-preview")
  # llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0, max_tokens=2500)
  
  def get_schema(_):
    return db.get_table_info()
  
  return (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | llm
    | StrOutputParser()
  )



def clean_query(query):
  cleaned_query = query.replace("\\_", "_")
  # print("Cleaned Query:", cleaned_query)  # Print the cleaned query
  return cleaned_query
    


def get_response(user_query: str, db: SQLDatabase, chat_history: list, llm: Ollama):
  sql_chain = get_sql_chain(db, llm)

  # <SCHEMA>{schema}</SCHEMA>
  # SQL_Query: <SQL>{query}</SQL>
  


  template = """
    You are interacting with a user who is asking you questions about the company's database.
    Write a natural language just from the 'SQL_Response' bellow for answering the 'User_question'. 
    Take the conversation history into account.

    User_question: {question}
    SQL_Response: {response}

    This is all the Conversation History: {chat_history}
    """
    
  prompt = ChatPromptTemplate.from_template(template)
  
  # llm = ChatOpenAI(model="gpt-4-0125-preview")
  # llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
  # llm = ollama(temperature=0)
  
  chain = (
    RunnablePassthrough.assign(query=sql_chain).assign(
      query=lambda vars: clean_query(vars["query"]),    # tambahan: utk bersihkan '\'
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
    


if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
      AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database."),
    ]



load_dotenv()

st.set_page_config(page_title="Chat with MySQL", page_icon=":speech_balloon:")
st.title("Chat with MySQL")
with st.sidebar:
    st.subheader("Settings")
    st.write("This is a simple chat application using MySQL. Connect to the database and start chatting.")
    
    st.text_input("Host", value="localhost", key="Host")
    st.text_input("Port", value="3306", key="Port")
    st.text_input("User", value="read", key="User")
    st.text_input("Password", type="password", value="", key="Password")
    st.text_input("Database", value="sirukam", key="Database")
    
    if st.button("Connect"):
        with st.spinner("Connecting to database..."):
            db = init_database(
                st.session_state["User"],
                st.session_state["Password"],
                st.session_state["Host"],
                st.session_state["Port"],
                st.session_state["Database"]
            )
            st.session_state.db = db
            st.success("Connected to database!")
    

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)


user_query = st.chat_input("Type a message...")
llm = Ollama(model="qwen2", temperature=0)


if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history, llm)
        st.markdown(response)
        
    st.session_state.chat_history.append(AIMessage(content=response))