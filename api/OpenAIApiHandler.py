import os
import openai
import json
import pandas as pd
import yaml
import requests
from flask_restful import Api, Resource, reqparse
from pysondb import getDb
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import HumanMessage, SystemMessage
from dotmap import DotMap
from benedict import benedict
from langchain.agents import Tool, AgentExecutor
from dotenv import load_dotenv
from langchain_community.utilities import BingSearchAPIWrapper
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, load_tools
from langchain.tools import tool
from pretty_html_table import build_table


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

airbrain_db = getDb('airbrain.json')


llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

template = (
    "{persona}."
)
system_message_prompt = SystemMessagePromptTemplate.from_template(template)
human_template = "{text}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

@tool("lower_case", return_direct=True)
def to_lower_case(input:str) -> str:
  """Returns the input as all lower case."""
  return input.lower()

@tool("solana_fm_token_balances", return_direct=True)
def solana_fm_token_balances(input:str) -> str:
  """Only returns Solana blockchain token balances using Solana.FM API."""
  url = "https://api.solana.fm/v1/addresses/" + input +"/tokens"
  headers = {"accept": "application/json"}
  response = requests.get(url, headers=headers)
  jsonResp = json.loads(response.text)
  tokens = jsonResp["tokens"]
  tokenBalances = []
  for key in tokens:
      try:
         #print(key)
         #print(tokens[key]["tokenData"]["tokenMetadata"]["onChainInfo"]["symbol"])
         #print(tokens[key]["balance"])
         tokenBalances.append([tokens[key]["tokenData"]["tokenMetadata"]["onChainInfo"]["symbol"], tokens[key]["balance"]]) 
      except:
         print("An exception occurred")

  df = pd.DataFrame(tokenBalances, columns=['Token', 'Balance'])
  df['Balance']=df['Balance'].apply(lambda x:round(x,2))
  df = df.sort_values(by=['Token'], ascending=True)
  print(df)
  return build_table(df, 'blue_light', text_align='right')

class OpenAIApiHandler(Resource):

  # def get(self, place):
  def post(self):
    print("got request in OpenAIApiHandler")
    parser = reqparse.RequestParser()
    parser.add_argument('agent_uuid', type=str)
    parser.add_argument('agent_flow', type=str)
    parser.add_argument('agent_name', type=str)
    parser.add_argument('question', type=str)
    #parser.add_argument('agent_details', type=str)
    parser.add_argument('agent_telegram_bot_id', type=str)
    args = parser.parse_args()

    print(args.agent_uuid)

    if(args.question):
       print("Invoke LLM")
       print(args.question)  
       agent_details = None

       if(args.agent_telegram_bot_id):
          agent_details = OpenAIApiHandler.getAgentDetailsforTelegramBot(args.agent_telegram_bot_id)
          print(agent_details)
       else:
          #agent_details = OpenAIApiHandler.getAgentDetails(args.agent_uuid) 
          print("In local else")
          agent_details = OpenAIApiHandler.getAgentDetails(args.agent_uuid)
          invalid_json = json.dumps(agent_details)
          valid_json =  invalid_json.replace("\'", "\"")
          valid_json =  valid_json.replace('"{', '{')
          valid_json =  valid_json.replace('}"', '}')
          valid_json =  valid_json.replace('True', 'true')
          valid_json =  valid_json.replace('False', 'false')
          print(valid_json)  
          print("agent persona is ")
          persona = "" 
          tools = []

          for agent in json.loads(valid_json):
             nodes = agent["agent_flow"]["nodes"]
             for node in nodes:
                type = node["type"]
                label = node["data"]["label"]
                if(type == "personanode"):
                   persona = label
                if((type == "skillnode") and (label =="Internet Search")):
                   search = BingSearchAPIWrapper()
                   tools = [
                        Tool(
                           name = "Search",
                           func=search.run,
                           description="useful for these type of questions: get current price of blockchain tokens, get current stock prices, answer questions about current events"
                        )
                     ]
          tools.extend(load_tools(['wikipedia']))
          tools.append(to_lower_case)
          tools.append(solana_fm_token_balances)
          print(persona)   
          print(tools)

          assistant_system_message = """You are a  """ + persona + """  . \
            Use tools (only if necessary) to best answer the users questions. Keep your answers concise with 1-2 sentences."""
          prompt = ChatPromptTemplate.from_messages(
               [
                  ("system", assistant_system_message),
                  ("user", "{input}"),
                  MessagesPlaceholder(variable_name="agent_scratchpad"),
               ]
            )
          agent = create_openai_functions_agent(ChatOpenAI(temperature=0), tools, prompt)

          agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
          result = agent_executor.invoke({"input": args.question})

       #output = llm(
       # chat_prompt.format_prompt(
       #     persona="You are " + persona, text=args.question + "  . Try to limit answer in 1-2 sentences."
       #  ).to_messages()
       # )

       print(result)

       return {
          'resultStatus': 'SUCCESS',
          #'message': output.content
          'message': result["output"]
          #'message': ""
          }
    else:
       print("set agent details")
       agent_details = {
          "agent_uuid": args.agent_uuid,
          "agent_flow": json.loads(json.dumps(args.agent_flow)),
          "agent_name": args.agent_name
       }
       saved_item_id = OpenAIApiHandler.setAgentDetails(agent_details)
       return {
          'resultStatus': 'SUCCESS',
          #'message': llm(question).split("\n\n")
          'message': "flow saved with item id: " + str(saved_item_id)
          }

    # higher temperature leads to more variation, randomness and creativity
    # temperature between 0.7 and 0.9 is most commonly used if you want to experiment and create many variations quickly
    # llm = OpenAI(temperature=0.9)
    # https://python.langchain.com/en/latest/modules/prompts/prompt_templates.html
    # prompt = PromptTemplate(
    #    input_variables=["place"],  # list of variables
    #    template="What are the 3 best places to eat in {place}?",  # prompt
    # )
    # question = prompt.format(place=place)
    # split() is used to split the items into a list. The llm response will look like:
    # "\n\n1. <first item>.\n\n2. <second item>..."

  
  def getAgentDetails(agent_uuid):
    q = {"agent_uuid": agent_uuid}
    data = airbrain_db.getByQuery(query=q)
    return data
  
  def getAgentDetailsforTelegramBot(agent_telegram_bot_id):
    for item in OpenAIApiHandler.agent_details:
        if item["agent_telegram_bot_id"] == agent_telegram_bot_id:
           return item

  def setAgentDetails(agent_details):
    print("Entered in setAgentDetails")
    print(agent_details["agent_uuid"])
    #add or update
    q = {"agent_uuid": agent_details["agent_uuid"]}
    data = airbrain_db.getByQuery(query=q)
    print(data)

    if(data):
       print("record exists")
       query_data = q
       updated_data = agent_details
       airbrain_db.updateByQuery(db_dataset=query_data, new_dataset=updated_data)
    else:
       print("record does not exist")
       item_id = airbrain_db.add(agent_details)
       print(item_id)
       return item_id  