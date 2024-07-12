# Test if agent can work



#from langchain_core.callbacks import FileCallbackHandler, StdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
#from langchain_openai import OpenAI
#from loguru import logger
from langchain_openai import ChatOpenAI, OpenAI
from langchain_experimental.plan_and_execute import (
    PlanAndExecute,
    load_agent_executor,
    load_chat_planner,
)
import inspect
from tools import seoul_api
from config import OPENAI_API_KEY,MODEL_NAME
from prompts import queries
#logfile = "output.log"

tools=[seoul_api.get_bike_rental_info,seoul_api.get_city_population]

model = ChatOpenAI(temperature=0,openai_api_key=OPENAI_API_KEY,model=MODEL_NAME)
planner = load_chat_planner(model)
executor = load_agent_executor(model, tools, verbose=True)
agent = PlanAndExecute(planner=planner, executor=executor, verbose=True,return_intermediate_steps=True)


questions=queries.tests
agent.invoke(questions[-1])