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

RSS_FEEDS = [
    "https://feedx.net/rss/mrdx.xml",
    "https://feedx.net/rss/thepaper.xml",
    "https://feedx.net/rss/jingjiribao.xml",
    "https://www.chinanews.com.cn/rss/world.xml",
    "https://www.chinanews.com.cn/rss/finance.xml",
    "https://www.chinanews.com.cn/rss/scroll-news.xml",
    
    "http://district.ce.cn/newarea/index.xml",
    "http://www.chinanews.com/rss/finance.xml",
    "http://xueqiu.com/hots/topic/rss",
    "https://feedx.net/rss/thepaper.xml",
    "http://feedmaker.kindle4rss.com/feeds/CBNweekly2008.weixin.xml",
    "http://www.eeo.com.cn/rss.xml",
    "https://rsshub.app/guancha/headline",
    "http://www.people.com.cn/rss/finance.xml",
    "http://copy.hexun.com/rss.jsp",
    "https://rsshub.app/cls/telegraph",
]

async def fetch_rss_feed(url: str) -> str:
    """Fetch RSS feed content from URL"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                return ""
    except Exception as e:
        logger.error(f"Error fetching RSS feed from {url}: {e}")
        return ""

async def parse_rss_items(xml_content: str):
    """Parse RSS feed XML content and extract news items"""
    try:
        from xml.etree import ElementTree as ET
        root = ET.fromstring(xml_content)
        channel = root.find('channel')
        if channel is None:
            return []
            
        items = []
        for item in channel.findall('item'):
            title = item.find('title')
            link = item.find('link')
            description = item.find('description')
            pub_date = item.find('pubDate')
            
            items.append({
                'title': title.text.strip() if title is not None and title.text else '',
                'url': link.text.strip() if link is not None and link.text else '',
                'description': description.text if description is not None and description.text else '',
                'pubDate': pub_date.text if pub_date is not None and pub_date.text else ''
            })
        return items
    except Exception as e:
        logger.error(f"Error parsing RSS feed: {e}")
        return []

@router.post("/fetch-rss")
async def fetch_and_store_rss():
    """Fetch news from RSS feeds and store in database"""
    try:
        stored_count = 0
        for feed_url in RSS_FEEDS:
            # Fetch RSS feed content
            xml_content = await fetch_rss_feed(feed_url)
            if not xml_content:
                continue
                
            # Parse RSS items
            news_items = await parse_rss_items(xml_content)
            
            # Store each news item
            for item in news_items:
                # Check if news already exists
                existing = supabase.table("news").select("*").eq("url", item['url']).execute()
                
                if not existing.data:
                    # Fetch full article content
                    summary = await fetch_article_content(item['url'])
                    
                    # Prepare news record
                    news_record = {
                        "published_at": item['pubDate'],
                        "title": item['title'],
                        "url": item['url'],
                        "source": feed_url.split('/')[-1].replace('.xml', ''),
                        "summary": summary or item['description']
                    }
                    
                    # Store in Supabase
                    supabase.table("news").insert(news_record).execute()
                    stored_count += 1
        
        return {"message": f"Successfully stored {stored_count} new RSS news items"}
        
    except Exception as e:
        logger.error(f"Error in fetch_and_store_rss: {e}")
        raise HTTPException(status_code=500, detail=str(e))