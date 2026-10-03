from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services import plaid_service

router = APIRouter(prefix="/plaid", tags=["Plaid Banking Integration"])

class LinkTokenResponse(BaseModel):
    link_token: str

class ExchangeRequest(BaseModel):
    public_token: str

class IncomeResponse(BaseModel):
    verified_income: float

# 1. Frontend calls this to get permission to open the popup
@router.post("/create_link_token", response_model=LinkTokenResponse)
def create_link_token():
    try:
        # Use a dummy user ID for sandbox
        link_token = plaid_service.create_link_token(user_id="user_123")
        return {"link_token": link_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Frontend calls this AFTER user logs in to verify income
@router.post("/verify_income", response_model=IncomeResponse)
def verify_income(data: ExchangeRequest):
    try:
        # A. Get Access Token
        access_token = plaid_service.exchange_public_token(data.public_token)
        
        # B. Calculate Income from history
        income = plaid_service.get_income_from_transactions(access_token)
        
        return {"verified_income": income}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))