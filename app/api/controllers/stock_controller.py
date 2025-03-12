from fastapi import APIRouter, HTTPException, Depends
import aiohttp
from typing import Optional
from app.supabase import supabase, get_authenticated_user

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

async def get_stock_info(ticker: str) -> dict:
    """Fetch stock info from Sina API"""
    # Convert ticker format
    sina_ticker = convert_ticker(ticker)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'http://hq.sinajs.cn/list={sina_ticker}',
            headers={'referer': 'https://finance.sina.com.cn/'}
        ) as response:
            if response.status != 200:
                raise HTTPException(status_code=502, detail="Failed to fetch stock data")
            
            text = await response.text()
            
            # Parse the response text
            # Format: var hq_str_sh601318="中国平安,27.500,27.450,27.880,28.000,27.450,27.870,27.880,..."
            data = text.split('=')[1].strip('"').split(',')
            
            if not data or len(data) < 2:
                raise HTTPException(status_code=404, detail="Stock data not found")
                
            return {
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
            }

@router.get("/info")
async def get_info(
    id: Optional[str] = None,
    ticker: Optional[str] = None,
    # user=Depends(get_authenticated_user)
):
    """Get stock information by ID or ticker"""
    if not id and not ticker:
        raise HTTPException(status_code=400, detail="Either id or ticker must be provided")

    # If ID is provided, look up the ticker in Supabase
    if id:
        result = supabase.table("stock").select("ticker").eq("id", id).execute()
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Stock ID not found")
        ticker = result.data[0]["ticker"]

    try:
        stock_info = await get_stock_info(ticker)
        return {
            "ticker": ticker,
            "data": stock_info
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 