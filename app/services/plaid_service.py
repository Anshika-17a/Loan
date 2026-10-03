import plaid
from plaid.api import plaid_api
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Configuration
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': os.getenv("PLAID_CLIENT_ID"),
        'secret': os.getenv("PLAID_SECRET"),
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# 2. Helper: Create a Link Token
def create_link_token(user_id: str):
    from plaid.model.link_token_create_request import LinkTokenCreateRequest
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
    from plaid.model.products import Products
    from plaid.model.country_code import CountryCode

    request = LinkTokenCreateRequest(
        products=[Products('transactions')],
        client_name="Loan Risk EWS (India Demo)", # Updated Name
        # Note: Plaid Sandbox primarily supports US/CA/UK/EU. 
        # India is not natively supported in the standard public sandbox yet.
        country_codes=[CountryCode('US')], 
        language='en',
        user=LinkTokenCreateRequestUser(
            client_user_id=str(user_id)
        )
    )
    response = client.link_token_create(request)
    return response['link_token']

# 3. Helper: Exchange Public Token for Access Token
def exchange_public_token(public_token: str):
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
    
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    return response['access_token']

# 4. Helper: Calculate Income from Transactions
def get_income_from_transactions(access_token: str):
    from plaid.model.transactions_get_request import TransactionsGetRequest
    from datetime import date, timedelta
    
    start_date = date.today() - timedelta(days=365)
    end_date = date.today()
    
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )
    response = client.transactions_get(request)
    
    total_income = 0.0
    for t in response['transactions']:
        # In Plaid, negative amount usually means money IN (deposit) for depository accounts
        if t['amount'] < 0 and abs(t['amount']) > 100:
            total_income += abs(t['amount'])
            
    return total_income