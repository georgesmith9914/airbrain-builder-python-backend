import os
import openai
import json
from dotenv import load_dotenv
from langchain_community.utilities import BingSearchAPIWrapper

from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.tools import BaseTool, StructuredTool, tool
from langchain.agents import create_openai_functions_agent
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import StringPromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
#from langchain.utilities import BingSearchAPIWrapper
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish
from langchain import hub
import re

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

search = BingSearchAPIWrapper()

tools = [
    Tool(
        name = "Search",
        func=search.run,
        description="useful for when you need to answer questions about current events"
    )
]

#prompt = hub.pull("hwchase17/openai-functions-agent")

assistant_system_message = """You are a Solana Blockchain Expert. \
Use tools (only if necessary) to best answer the users questions."""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", assistant_system_message),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

print(prompt.messages)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

agent = create_openai_functions_agent(ChatOpenAI(temperature=0), tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
result = agent_executor.invoke({"input": "Who are you?"})
print(result["output"])