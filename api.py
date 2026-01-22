from fastapi import APIRouter, Request, HTTPException
from gsc import GSCClient
from analyst import Analyst
from pydantic import BaseModel
from datetime import date
import json

router = APIRouter()
analyst = Analyst()

class ChatRequest(BaseModel):
    question: str
    site_url: str

@router.get("/sites")
def list_sites(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        client = GSCClient(user)
        sites = client.list_sites()
        # Filter for siteUrl and permission level if needed, but returning full object is fine
        return [{"siteUrl": s['siteUrl'], "permissionLevel": s['permissionLevel']} for s in sites]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
def chat(request: Request, body: ChatRequest):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # 1. Parse Intent
        query_params = analyst.parse_intent(body.question, str(date.today()))
        if not query_params:
            return {"insight": "I'm sorry, I couldn't understand how to query GSC for that. could you try rephrasing?"}
        
        # 2. Fetch Data
        client = GSCClient(user)
        
        # Construct GSC Payload
        # We need to map our simplified JSON to the actual GSC API structure
        # GSC API expects 'startDate', 'endDate', 'dimensions', 'rowLimit'
        
        # Default fallback
        if "startDate" not in query_params:
             query_params["startDate"] = "2023-01-01" # Should be dynamic in production if Analyst failed
        if "endDate" not in query_params:
             query_params["endDate"] = "2023-01-28"

        gsc_payload = {
            "startDate": query_params.get("startDate"),
            "endDate": query_params.get("endDate"),
            "dimensions": query_params.get("dimensions", ["date"]),
            "rowLimit": query_params.get("rowLimit", 10)
        }
        
        # Add metrics filter if needed, but GSC API returns all metrics by default usually, 
        # unless specific aggregationType is set. We'll just take what we get.
        
        data = client.query_search_analytics(body.site_url, gsc_payload)
        
        comparison_data = None
        if query_params.get("comparison"):
            # Calculate previous period (simplified logic for demo: shift back by same days)
             # Real implementation would use datetime parsing
             pass 

        # 3. Generate Insight
        insight = analyst.generate_insight(body.question, data, comparison_data)
        
        return {"insight": insight, "data": data} # Returning raw data for debug if needed
        
    except Exception as e:
        # Log error in production
        return {"error": str(e)}
