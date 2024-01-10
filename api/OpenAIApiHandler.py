import os
import openai
import json
from flask_restful import Api, Resource, reqparse
from pysondb import getDb
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import HumanMessage, SystemMessage

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

class OpenAIApiHandler(Resource):

  # def get(self, place):
  def post(self):
    print("got request in OpenAIApiHandler")
    parser = reqparse.RequestParser()
    parser.add_argument('agent_uuid', type=str)
    parser.add_argument('agent_flow', type=str)
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

       output = llm(
        chat_prompt.format_prompt(
            persona="You are " + agent_details["agent_persona"], text=args.question + "  . Try to limit answer in 1-2 sentences."
          ).to_messages()
        )

       print(output)

       return {
          'resultStatus': 'SUCCESS',
          #'message': llm(question).split("\n\n")
          'message': output.content
          }
    else:
       print("set agent details")
       agent_details = {
          "agent_uuid": args.agent_uuid,
          "agent_flow": args.agent_flow
       }
       OpenAIApiHandler.setAgentDetails(agent_details)
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
    for item in OpenAIApiHandler.agent_details:
        if item["agent_uuid"] == agent_uuid:
           return item

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
