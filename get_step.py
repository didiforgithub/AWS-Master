import zipfile
import os
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.schema import BaseOutputParser
import re

# parse zip file structure
def parse_zip(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        parse_list = []
        for info in zip_file.infolist():
            # print(info.filename)
            parse_list.append(info.filename)

# parse directory structure
def parse_dir(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_paths.append(file_path)
    return file_paths

# unzip file
def unzip_file(zip_path, unzip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        zip_file.extractall(unzip_path)


class CommaSeparatedListOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""


    def parse(self, text: str):
        """Parse the output of an LLM call."""
        # print(text)
        text_list = text.strip().split("\n")
        result = []
        for item in text_list:
            match = re.match(r"^\d+\.", item)
            if match:
                result.append(item[len(match.group()):].strip())
        return result

# get steps to deploy
def get_steps2deploy(file_paths):
    template = """You are a helpful assistant who generates comma separated lists.
    A user will pass in a program, specifically, a list of file paths of this program, you need to
    generate steps about how to deploy it to Amazon EC2 depends on what program it will be.
    Summarize each step in one sentence and make it an element of the list
    ONLY return the list and nothing more."""
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    chain = LLMChain(
        llm = ChatOpenAI(max_tokens=1500,
                     model_name="gpt-3.5-turbo", # gpt-4
                     openai_api_key="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") ,
        prompt=chat_prompt,
        output_parser=CommaSeparatedListOutputParser()
    )
    result = chain.run(file_paths)
    print(result)
    return result
