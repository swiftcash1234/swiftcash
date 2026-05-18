import requests

MEGAPAY_API_URL = "https://megapay.co.ke/backend/v1"
MEGAPAY_API_KEY = "MGPY5nBRzeut"
MEGAPAY_EMAIL = "smilejaym711@gmail.com"

def initiate_stk_push(amount, msisdn, reference):
    payload = {
        "api_key": MEGAPAY_API_KEY,
        "email": MEGAPAY_EMAIL,
        "amount": str(amount),
        "msisdn": msisdn,
        "reference": reference,
    }
    response = requests.post(f"{MEGAPAY_API_URL}/initiatestk", json=payload)
    response.raise_for_status()
    return response.json()

def check_transaction_status(transaction_request_id):
    payload = {
        "api_key": MEGAPAY_API_KEY,
        "email": MEGAPAY_EMAIL,
        "transaction_request_id": transaction_request_id,
    }
    response = requests.post(f"{MEGAPAY_API_URL}/transactionstatus", json=payload)
    response.raise_for_status()
    return response.json()
