from api import get_flight_data
from scraper import get_airport_info
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("AVIATIONSTACK_API_KEY")


def main():
    flight_iata=input("Enter flight IATA number:").strip().upper()
    try:
        flight=get_flight_data(API_KEY,flight_iata)
        dep_airport=flight["departure"]["airport"]
        arr_airport=flight["arrival"]["airport"]

        dep_info=get_airport_info(dep_airport)
        arr_info=get_airport_info(arr_airport)

        print("\n✈️ Flight Status")
        print("---------------------------")
        print("Airline:", flight["airline"]["name"])
        print("Flight:", flight["flight"]["iata"])
        print("Status:", flight["flight_status"])

        print("\nDeparture:")
        print("Airport:", dep_airport)
        print("Country:", dep_info.get("country", "N/A"))
        print("Timezone:", dep_info.get("timezone", "N/A"))

        print("\nArrival:")
        print("Airport:", arr_airport)
        print("Country:", arr_info.get("country", "N/A"))
        print("Timezone:", arr_info.get("timezone", "N/A"))
    except Exception as e:
        print("Error:", e)

if __name__=="__main__":
    main()