# import os
# import subprocess

# def activate_virtualenv(env_folder):
#     # Check if the folder exists
#     if not os.path.isdir(env_folder):
#         print(f"Error: Virtual environment folder '{env_folder}' does not exist.")
#         return
    
#     # Activate the virtual environment
#     activate_script = os.path.join(env_folder, 'Scripts' if os.name == 'nt' else 'bin', 'activate')
#     activate_command = f"source {activate_script}" if os.name != 'nt' else activate_script
#     subprocess.run(activate_command, shell=True)

# if __name__ == "__main__":
#     env_folder = "../.venv"
#     activate_virtualenv(env_folder)

from dotenv import load_dotenv
import streamlit as st
from langchain_community.llms import Ollama
from langchain_community.utilities import SQLDatabase

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
# from langchain_openai import ChatOpenAI
# from langchain_groq import ChatGroq
# from langchain_community.chat_models import ChatGroq

def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
  db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
  return SQLDatabase.from_uri(db_uri)

def get_sql_chain(db):
    template = """
        Anda adalah seorang Data Analis di sebuah perusahaan. Anda berinteraksi dengan pengguna yang menanyakan tentang database perusahaan. Berdasarkan skema tabel di bawah, tulis SQL Query yang akan menjawab pertanyaan pengguna. Pertimbangkan riwayat percakapan.

        <SCHEMA>{schema}</SCHEMA>

        Riwayat Percakapan: {chat_history}

        Tulis hanya SQL query dan tidak ada tambahan kalimat lain. Jangan gabungkan SQL Query dengan teks lain, bahkan tanda backticks.

        Sebagai contoh:
        Question: sebutkan 3 artis dengan track terbanyak?
        SQL Query: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;
        Question: sebutkan 10 orang artis.
        SQL Query: SELECT Name FROM Artist LIMIT 10;

        Giliran anda:

        Question: {question}
        SQL Query:
        """

    prompt = ChatPromptTemplate.from_template(template)
  
    # llm = ChatOpenAI(model="gpt-4-0125-preview")
    # llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0, max_tokens=2500)
    llm = Ollama(model="llama3")
  
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
  print("Cleaned Query:", cleaned_query)  # Print the cleaned query
  return cleaned_query
    


def get_response(user_query: str, db: SQLDatabase, chat_history: list):
    sql_chain = get_sql_chain(db)
    
    template = """
        Anda adalah seorang analis data di sebuah perusahaan. Anda berinteraksi dengan pengguna yang menanyakan pertanyaan tentang database perusahaan. Berdasarkan skema tabel di bawah ini, pertanyaan, SQL query, dan SQL response, tulis respons bahasa alami.
        <SCHEMA>{schema}</SCHEMA>

        Riwayat percakapan: {chat_history}
        SQL Query: <SQL>{query}</SQL>
        Pertanyaan user: {question}
        SQL Response: {response}"""
    
    prompt = ChatPromptTemplate.from_template(template)
  
    # llm = ChatOpenAI(model="gpt-4-0125-preview")
    # llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
    llm = Ollama(model="llama3")


    chain = (
        RunnablePassthrough.assign(query=sql_chain).assign(
            # query=lambda vars: clean_query(vars["query"]),    # tambahan: utk bersihkan '\'
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
      AIMessage(content="Halo! Saya adalah asisten SQL. Silahkan tanya apapun tentang database Anda."),
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
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
        st.markdown(response)
        
    st.session_state.chat_history.append(AIMessage(content=response))