import openai
import json
from dotenv import load_dotenv
import os

load_dotenv()

ai_client = openai.AzureOpenAI(
    api_key=os.environ.get('AI_KEY'),
    azure_endpoint=os.environ.get("AI_ENDPOINT"),
    api_version=os.environ.get("AI_API_VERSION")    
)