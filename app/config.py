import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# from langchain_deepseek import ChatDeepSeek
from supabase import create_client, Client
from fastapi import Request, HTTPException

# Load environment variables from .env file
load_dotenv()

# Initialize LLMs using environment variables
gpt4o = ChatOpenAI(
    model="gpt-4o",
    temperature=0.01,
    api_key=os.environ.get("OPENAI_API_KEY")
)

deepseek = ChatOpenAI(
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0.7,
    api_key=os.environ.get("DEEPSEEK_API_KEY")
) 

deepseek_openrouter = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    model="deepseek/deepseek-chat",
    temperature=0.9,
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

deepseek_openrouter_low = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    model="deepseek/deepseek-chat",
    temperature=0.1,
    api_key=os.environ.get("OPENROUTER_API_KEY")
)