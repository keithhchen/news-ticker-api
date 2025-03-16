from fastapi import APIRouter, HTTPException, Depends, Response, Request
import aiohttp
from typing import Optional, Union, List
from app.supabase import supabase, get_authenticated_user
from pydantic import BaseModel
import asyncio
import logging
from .graph_controller import process_with_graph, GraphInput
from uuid import UUID

logger = logging.getLogger("uvicorn")

router = APIRouter(
    prefix="/stock",
    tags=["stock"]
)

def convert_ticker(ticker: str) -> str:
    """Convert ticker from format like '000000.SH' to 'sh000000'"""
    if '.' not in ticker:
        return ticker
        
    code, market = ticker.split('.')
    return f"{market.lower()}{code}"

async def get_stock_info(tickers: Union[str, List[str]]) -> List[dict]:
    """Fetch stock info from Sina API
    Args:
        tickers: A single ticker string or a list of ticker strings
    Returns:
        A list of stock info dicts, even for single ticker
    """
    # Handle single ticker case
    if isinstance(tickers, str):
        tickers = [tickers]
    
    # Convert ticker format for each ticker
    sina_tickers = [convert_ticker(ticker) for ticker in tickers]
    sina_ticker_str = ','.join(sina_tickers)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'http://hq.sinajs.cn/list={sina_ticker_str}',
            headers={'referer': 'https://finance.sina.com.cn/'}
        ) as response:
            if response.status != 200:
                raise HTTPException(status_code=502, detail="Failed to fetch stock data")
            
            text = await response.text()
            # Split response into individual stock data strings
            stock_data_strings = [s for s in text.split(';') if s.strip()]
            
            if not stock_data_strings:
                raise HTTPException(status_code=404, detail="Stock data not found")
            
            result = []
            for data_string in stock_data_strings:
                # Parse each stock data string
                # Format: var hq_str_sh601318="中国平安,27.500,27.450,27.880,28.000,27.450,27.870,27.880,..."
                data = data_string.split('=')[1].strip('"').split(',')
                
                if not data or len(data) < 2:
                    continue
                    
                result.append({
                    "name": data[0],
                    "open": data[1],
                    "prev_close": data[2],
                    "current": data[3],
                    "high": data[4],
                    "low": data[5],
                    "bid": data[6],
                    "ask": data[7],
                    "volume": data[8] if len(data) > 8 else None,
                    "amount": data[9] if len(data) > 9 else None,
                    "timestamp": data[-3] + " " + data[-2] if len(data) > 30 else None
                })
            
            # Always return a list, even for single ticker
            return result

# @router.get("/info", dependencies=[Depends(get_authenticated_user)])
class StockInfoRequest(BaseModel):
    id: Optional[List[str]] = None
    ticker: Optional[List[str]] = None

@router.post("/info")
async def get_info(request: StockInfoRequest):
    """Get stock information by ID or ticker
    Args:
        id: Single stock ID or list of stock IDs
        ticker: Single ticker or list of tickers
    Returns:
        Dictionary containing stock info and real-time data
    """
    if not request.id and not request.ticker:
        raise HTTPException(status_code=400, detail="Either id or ticker must be provided")

    # Initialize list to store tickers
    tickers_to_fetch = []

    # If IDs are provided, look up the tickers in Supabase
    if request.id:
        for stock_id in request.id:
            result = supabase.table("stock").select("ticker").eq("id", stock_id).execute()
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
            tickers_to_fetch.append(result.data[0]["ticker"])

    # Add directly provided tickers
    if request.ticker:
        tickers_to_fetch.extend(request.ticker)

    try:
        stock_info = await get_stock_info(tickers_to_fetch)
        # Always return an array of results
        return [
            {
                "info": ticker,
                "real_time_data": info
            } for ticker, info in zip(tickers_to_fetch, stock_info)
        ]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class NewsStockRequest(BaseModel):
    news_id: str
    stock_id: int

@router.post("/news-and-stock", dependencies=[Depends(get_authenticated_user)])
# @router.post("/news-and-stock")
async def get_news_and_stock(
    request: NewsStockRequest,
):
    """Get both news and stock information by their IDs"""

    async def fetch_news():
        news_result = supabase.table("news").select("*").eq("id", request.news_id).execute()
        if not news_result.data or len(news_result.data) == 0:
            raise HTTPException(status_code=404, detail="News not found")
        return news_result.data[0]
    
    async def fetch_stock():
        stock_result = supabase.table("stocks").select("*").eq("id", request.stock_id).execute()
        if not stock_result.data or len(stock_result.data) == 0:
            raise HTTPException(status_code=404, detail="Stock not found")
        return stock_result.data[0]
    
    # Fetch both concurrently
    news_data, stock_data = await asyncio.gather(
        fetch_news(),
        fetch_stock(),
        return_exceptions=True
    )
    
    # Handle any exceptions that occurred
    if isinstance(news_data, Exception):
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(news_data)}")
    if isinstance(stock_data, Exception):
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock: {str(stock_data)}")
    
    stock_real_time_data = await get_stock_info(stock_data["ticker"])
            
    graph_input = GraphInput(
        input_text=f"""title: {news_data["title"]}, summary: {news_data["summary"]}, source: {news_data["source"]}, published_at: {news_data["published_at"]}""",
        ticker=f'{stock_data["ticker"]} {stock_data["name"]}, current price: {stock_real_time_data["current"]}, volume: {stock_real_time_data["volume"]}'
    )
    logger.info(graph_input)
    graph_result = await process_with_graph(graph_input)
    
    return {
        "news": news_data,
        "stock": {
            "info": stock_data,
            "real_time_data": stock_real_time_data
        },
        "analysis": graph_result.get("result")  # Use .get() to safely handle None
    } 

class AddFavoriteStockRequest(BaseModel):
    stock_id: int
    reverse: bool = False

@router.post("/favorite", dependencies=[Depends(get_authenticated_user)])
async def add_favorite_stock(request: AddFavoriteStockRequest, user=Depends(get_authenticated_user)):
    """Add or remove a stock to user's favorites"""

    try:
        # Look up the stock ticker from the stocks table
        stock_result = supabase.table("stocks").select("ticker").eq("id", request.stock_id).execute()
        if not stock_result.data or len(stock_result.data) == 0:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        # Check if the stock is already in favorites
        existing = supabase.table("user_stocks").select("*").match({
            "uid": user.id,
            "stock_id": request.stock_id
        }).execute()
        
        
        if request.reverse:
            # Remove from favorites
            if not existing.data:
                raise HTTPException(status_code=400, detail="股票不在持仓中")
            supabase.table("user_stocks").delete().match({
                "uid": user.id,
                "stock_id": request.stock_id
            }).execute()
        else:
            # Add to favorites
            if existing.data:
                raise HTTPException(status_code=400, detail="股票已在持仓中")
            supabase.table("user_stocks").insert({
                "uid": user.id,
                "stock_id": request.stock_id,
            }).execute()
        
        # Fetch all favorite stocks for the user
        all_favorites = supabase.table("user_stocks").select("*").eq("uid", user.id).execute()
        
        return {
            "stocks": all_favorites.data
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error adding favorite stock: {e}")
        raise HTTPException(status_code=500, detail=str(e))