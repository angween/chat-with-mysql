from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.llms import Ollama
# from dotenv import load_dotenv
# import os

# load_dotenv()
# OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
# PG_DB_URL = os.environ.get('PG_DB_URL')

# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
db_user = "read"
db_password = "12345"
db_host = "localhost"
db_name = "contoh"
db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

llm = Ollama(model="llama3", temperature=0)

# db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)
db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=True)

db_chain.invoke("tell me 5 top spender customers we have")