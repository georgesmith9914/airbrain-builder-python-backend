import os
import openai
from flask_restful import Api, Resource, reqparse


from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import HumanMessage, SystemMessage

openai.api_key = os.getenv("OPENAI_API_KEY")

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
    parser.add_argument('question', type=str)

    args = parser.parse_args()

    print(args)
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
    output = llm(
    chat_prompt.format_prompt(
        persona="You are a game expert.", text=args.question + "  . Try to limit answer in 1-2 sentences."
      ).to_messages()
    )

    print(output)

    return {
      'resultStatus': 'SUCCESS',
      #'message': llm(question).split("\n\n")
      'message': output.content
      }

  