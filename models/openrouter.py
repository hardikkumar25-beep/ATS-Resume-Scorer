from autogen_ext.models.openai import OpenAIChatCompletionClient
import os
from dotenv import load_dotenv
load_dotenv()

def getOpenRouterModel():
    api_key = os.getenv('OPENROUTER_API_KEY')
    model_client = OpenAIChatCompletionClient(
        base_url="https://openrouter.ai/api/v1",
        model='nvidia/nemotron-3-nano-30b-a3b:free',
        api_key=api_key,
        temperature=0,
        model_info={
            "family": "nvidia",
            "vision":True,
            "function_calling":True,
            "json_output":False
        })
    return model_client