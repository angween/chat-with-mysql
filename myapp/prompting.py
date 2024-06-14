from langchain_community.utilities import SQLDatabase

db_user = "read"
db_password = "12345"
db_host = "localhost"
db_name = "chinook"
db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")


print(db.dialect)
print(db.get_usable_table_names())
# print(db.get_table_names())

# response = db.run("SELECT * FROM Artist LIMIT 10;")
# print(response)

from langchain.chains import create_sql_query_chain
from langchain_community.llms import Ollama
import re 
# from langchain_groq import ChatGroq


def clean_query(query):
  cleaned_query = query.replace("\\_", "_")
  cleaned_query = cleaned_query.replace("\\*", "*")
  return cleaned_query


def grab_query(text):
  pattern = r'```sql(.*?)```'

  result = re.search(pattern, text, re.DOTALL)

  if result:
    return result.group(1).strip()
  else:
    return None

# llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
# llm = Ollama(model="llama3", temperature=0.0)
# chain = create_sql_query_chain(llm, db)
# queryLine = chain.invoke({"question": "How many customers do we have"})
# queryLine = grab_query(queryLine)
# queryLine = clean_query(queryLine)
# chain.get_prompts()[0].pretty_print()

# response = db.run(queryLine)
# print(response)




# from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

# execute_query = QuerySQLDataBaseTool(db=db)

# write_query = create_sql_query_chain(llm, db)

# chain = write_query | execute_query

# chain.invoke({"question": "How many customers are there"})

# print(chain)

# print(response)