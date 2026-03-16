import requests

BASE_URL="http://api.aviationstack.com/v1/flights"

def get_flight_data(api_key:str,flight_iata:str)->dict:
    params={
        "access_key":api_key,
        "flight_iata":flight_iata
    }

    response=requests.get(BASE_URL,params=params,timeout=10)
    response.raise_for_status()

    data=response.json()

    if not data.get("data"):
        raise ValueError("No data found")
    
    return data["data"][0]