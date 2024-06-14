



# DB
from llama_index.core import SQLDatabase
db_user = "read"
db_password = "12345"
db_host = "localhost"
db_name = "contoh"
sql_database = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")



# llm
from llama_index.llms.ollama import Ollama
llm = Ollama(model="llama3", temperature=0)


# # prompt
# from llama_index.core.query_pipeline import QueryPipeline
# from llama_index.core.prompts import PromptTemplate

# prompt_str = "Please tell related movie to The Departed"
# prompt_templ = PromptTemplate(prompt_str)

# p = QueryPipeline(chain=[prompt_templ, llm], verbose=True) 
# output = p.run()

# print(output)


# db + llm
from llama_index.core import ServiceContext
from llama_index.core.query_engine import NLSQLTableQueryEngine

service_context = ServiceContext.from_defaults(
  llm=llm,
)

query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    service_context=service_context
)

from llama_index.core import Settings
Settings.llm = Ollama(model="llama3")




#
from llama_index.core.query_pipeline import QueryPipeline as QP
from llama_index.core.agent import QueryPipelineAgentWorker, AgentRunner
from llama_index.core.callbacks import CallbackManager

qp = QP(verbose=True)

agent_worker = QueryPipelineAgentWorker(qp)
agent = AgentRunner(
    agent_worker, callback_manager=CallbackManager([]), verbose=True
)

task = agent.create_task(
    "What are some tracks from the artist AC/DC? Limit it to 3"
)

step_output = agent.run_step(task.task_id)


response = agent.finalize_response(task.task_id)

print("\n\n")
print(str(response))