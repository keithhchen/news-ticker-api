from fastapi import APIRouter, HTTPException
from app.supabase import supabase
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import os
from pydantic import BaseModel
import feedparser
from typing import List

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

RSS_FEEDS = [
    # "https://feedx.net/rss/mrdx.xml",
    # "https://feedx.net/rss/thepaper.xml",
    # "https://feedx.net/rss/jingjiribao.xml",
    # "https://www.chinanews.com.cn/rss/world.xml",
    # "https://www.chinanews.com.cn/rss/finance.xml",
    # "https://www.chinanews.com.cn/rss/scroll-news.xml",
    
    # "http://district.ce.cn/newarea/index.xml",
    # "http://copy.hexun.com/rss.jsp",
    # "http://feedmaker.kindle4rss.com/feeds/CBNweekly2008.weixin.xml",
    "http://www.chinanews.com/rss/finance.xml",
    "http://xueqiu.com/hots/topic/rss",
    "https://feedx.net/rss/thepaper.xml",
    "http://www.eeo.com.cn/rss.xml",
    "https://rsshub.app/guancha/headline",
    "http://www.people.com.cn/rss/finance.xml",

]

def clean_html_content(html_content: str) -> str:
    """Remove HTML tags and images from content"""
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove images
    for img in soup.find_all('img'):
        img.decompose()
    
    # Get text content
    text = soup.get_text(separator=' ', strip=True)
    return text

async def fetch_rss_feed(url: str) -> List[dict]:
    """Fetch and parse RSS feed"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    items = []
                    for entry in feed.entries:
                        item = {
                            "published_at": entry.get('published', entry.get('pubDate', '')),
                            "title": entry.get('title', ''),
                            "url": entry.get('link', ''),
                            "source": entry.get('author', feed.feed.get('title', '')),
                            "summary": clean_html_content(entry.get('description', ''))
                        }
                        items.append(item)
                    return items
                return []
    except Exception as e:
        logger.error(f"Error fetching RSS feed {url}: {e}")
        return []

@router.post("/fetch-rss")
async def fetch_and_store_rss():
    """Fetch all RSS feeds and store items in database"""
    try:
        success_items = []
        failed_items = []
        
        # Fetch all feeds concurrently
        feed_tasks = [fetch_rss_feed(url) for url in RSS_FEEDS]
        feed_results = await asyncio.gather(*feed_tasks)
        
        # Process all items from all feeds
        for items in feed_results:
            for item in items:
                try:
                    # Check if news already exists
                    existing = supabase.table("news").select("*").eq("url", item['url']).execute()
                    
                    if not existing.data:
                        # Store in Supabase
                        result = supabase.table("news").insert(item).execute()
                        success_items.append({
                            "title": item['title'],
                            "url": item['url'],
                            "source": item['source']
                        })
                except Exception as e:
                    logger.error(f"Error storing RSS item: {e}")
                    failed_items.append({
                        "title": item.get('title', ''),
                        "url": item.get('url', ''),
                        "source": item.get('source', ''),
                        "error": str(e)
                    })
        
        return {
            "success": success_items,
            "failed": failed_items,
            "total_success": len(success_items),
            "total_failed": len(failed_items)
        }
    
    except Exception as e:
        logger.error(f"Error in fetch_and_store_rss: {e}")
        raise HTTPException(status_code=500, detail=str(e))
