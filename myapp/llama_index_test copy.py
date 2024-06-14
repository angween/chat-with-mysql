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