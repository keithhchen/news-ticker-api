from fastapi import APIRouter, HTTPException
from app.supabase import supabase
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import os
from pydantic import BaseModel

logger = logging.getLogger("uvicorn")

router = APIRouter(
    prefix="/news",
    tags=["news"]
)

TIANAPI_KEY = os.environ.get("TIANAPI_KEY")

class NewsFetchRequest(BaseModel):
    category: str = "caijing"
    page: int = 1

async def fetch_article_content(url: str) -> str:
    """Fetch and extract the main content of an article"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text and clean it up
                    text = soup.get_text(separator='\n', strip=True)
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    return '\n'.join(lines)  # Return the complete article content
                return ""
    except Exception as e:
        logger.error(f"Error fetching article content: {e}")
        return ""

async def fetch_news(category: str, page: int):
    """Fetch news from Tianapi"""
    tianapi_url = f"https://apis.tianapi.com/{category}/index"
    async with aiohttp.ClientSession() as session:
        params = {
            'key': TIANAPI_KEY,
            'num': 50,
            'page': page
        }
        async with session.post(tianapi_url, data=params) as response:
            if response.status == 200:
                return await response.json()
            raise HTTPException(status_code=response.status, detail="Failed to fetch news")

@router.post("/fetch")
async def fetch_and_store_news(category: str, page: int):
    """Fetch news and store in Supabase"""
    try:
        # Fetch news from API
        news_data = await fetch_news(category, page)
        
        if news_data['code'] != 200:
            raise HTTPException(status_code=400, detail=news_data['msg'])
        
        stored_count = 0
        for news_item in news_data['result']['newslist']:
            # Clean up URL if it starts with '//' by adding 'https:'
            if news_item['url'].startswith('//'):
                news_item['url'] = f'https:{news_item["url"]}'

            # Check if news already exists
            existing = supabase.table("news").select("*").eq("url", news_item['url']).execute()
            
            if not existing.data:
                # Fetch article content for summary
                summary = await fetch_article_content(news_item['url'])
                
                # Prepare news data
                news_record = {
                    "published_at": news_item['ctime'],
                    "title": news_item['title'],
                    "thumbnail": news_item['picUrl'],
                    "url": news_item['url'],
                    "source": news_item['source'],
                    "summary": summary,
                }
                
                # Store in Supabase
                supabase.table("news").insert(news_record).execute()
                stored_count += 1
        
        return {"message": f"Successfully stored {stored_count} new news items"}
    
    except Exception as e:
        logger.error(f"Error in fetch_and_store_news: {e}")
        raise HTTPException(status_code=500, detail=str(e))