import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# from langchain_deepseek import ChatDeepSeek
from supabase import create_client, Client
from fastapi import Request, HTTPException

# Load environment variables from .env file
load_dotenv()
print(os.getenv("OPENAI_API_KEY"))

# Initialize LLMs using environment variables
gpt4o = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

deepseek = ChatOpenAI(
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0.7,
    api_key=os.getenv("DEEPSEEK_API_KEY")
) 