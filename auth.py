from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os
import json

router = APIRouter()

# Scopes for GSC Readonly
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

def get_flow(redirect_uri=None):
    # Try loading from environment variables first (Render/Prod)
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    if client_id and client_secret:
        client_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
    elif os.path.exists('client_secret.json'):
         # Fallback to file for local dev if exists
        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=SCOPES
        )
    else:
        raise HTTPException(status_code=500, detail="Google Credentials not found (env or json)")

    if redirect_uri:
        flow.redirect_uri = redirect_uri
    return flow

@router.get("/login")
def login(request: Request):
    # Determine the callback URL dynamically based on env
    base_url = os.getenv("APP_BASE_URL", "http://localhost:8000")
    redirect_uri = f"{base_url}/auth/callback"
    
    flow = get_flow(redirect_uri)
    auth_url, _ = flow.authorization_url(prompt='consent')
    return RedirectResponse(auth_url)

@router.get("/callback")
def callback(request: Request, code: str):
    try:
        base_url = os.getenv("APP_BASE_URL", "http://localhost:8000")
        redirect_uri = f"{base_url}/auth/callback"
        flow = get_flow(redirect_uri)
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Store credentials in session (in production, store in DB and keep session ID)
        # We serialize to JSON for simplicity in this cookie-based session
        creds_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        request.session['user'] = creds_data
        
        return RedirectResponse(f"{base_url}/static/index.html")
    except Exception as e:
        return {"error": str(e)}

@router.get("/user")
def get_user(request: Request):
    user = request.session.get('user')
    if not user:
        return {"authenticated": False}
    return {"authenticated": True}

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    base_url = os.getenv("APP_BASE_URL", "http://localhost:8000")
    return RedirectResponse(f"{base_url}/static/index.html")
