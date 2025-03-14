import os
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import Request, HTTPException, Response
import logging

logger = logging.getLogger("uvicorn")

# Load environment variables from .env file
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def get_authenticated_user(request: Request, response: Response):
    """Authenticate user and handle token refresh"""
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(status_code=401, detail="No authorization header")

    token = auth_header.split(" ")[1]  # Extract the token

    try:
        user = supabase.auth.get_user(token)  # Try to validate the token
        return user
    except Exception as e:
        
        # Try to refresh the token if validation failed
        refresh_token = request.headers.get("x-refresh-token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="No refresh token")
            
        try:
            # Attempt to refresh the token
            refresh_response = supabase.auth.refresh_session(refresh_token)
            
            new_token = refresh_response.session.access_token
            
            # Set the new token in response header
            response.headers["x-access-token"] = new_token
            response.headers["x-refresh-token"] = refresh_response.session.refresh_token
            # Return user with refreshed token
            user = supabase.auth.get_user(new_token)
            return user
        except Exception:
            raise HTTPException(status_code=401, detail="Failed to refresh token")