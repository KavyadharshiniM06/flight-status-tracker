from api import get_flight_data
from scraper import get_airport_info
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

def parse_time(ts):
    """Parse ISO timestamp to datetime object, return None if missing."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def format_time(dt):
    """Format datetime to readable string."""
    if not dt:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M %Z")

def get_delay(scheduled, actual_or_estimated):
    """Return delay in minutes, or None if can't be calculated."""
    if not scheduled or not actual_or_estimated:
        return None
    delta = actual_or_estimated - scheduled
    return int(delta.total_seconds() / 60)


def format_delay(minutes, flight_status):
    if minutes is None:
        if flight_status == "scheduled":
            return "  ⏳ Not yet departed"
        return "  N/A"
    if minutes <= 0:
        return "  ✅ On time"
    return f"  ⚠️  Delayed by {minutes} min"

def print_endpoint(label, data, airport_info,flight_status):
    scheduled  = parse_time(data.get("scheduled"))
    estimated  = parse_time(data.get("estimated"))
    actual     = parse_time(data.get("actual"))

    # Use actual if available, otherwise estimated, for delay calc
    best_time  = actual or estimated
    delay      = get_delay(scheduled, best_time)

    print(f"\n{label}:")
    print("  Airport:   ", data.get("airport", "N/A"))
    print("  Country:   ", airport_info.get("country", "N/A"))
    print("  Timezone:  ", airport_info.get("timezone", "N/A"))
    print("  Terminal:  ", data.get("terminal") or "N/A")
    print("  Gate:      ", data.get("gate") or "N/A")
    print("  Scheduled: ", format_time(scheduled))
    print("  Estimated: ", format_time(estimated))
    print("  Actual:    ", format_time(actual))
    print("  Delay:     ", format_delay(delay, flight_status) if delay is not None else format_delay(None, flight_status))


def main():
    if not API_KEY:
        print("Error: AVIATIONSTACK_API_KEY not set in .env")
        return

    flight_iata = input("Enter flight IATA number: ").strip().upper()
    try:
        flight = get_flight_data(API_KEY, flight_iata)

        dep_airport = flight["departure"]["airport"]
        arr_airport = flight["arrival"]["airport"]

        dep_info = get_airport_info(dep_airport)
        arr_info = get_airport_info(arr_airport)

        print("\n✈️  Flight Status")
        print("---------------------------")
        print("Airline: ", flight["airline"]["name"])
        print("Flight:  ", flight["flight"]["iata"])
        print("Status:  ", flight["flight_status"])

        print_endpoint("Departure", flight["departure"], dep_info, flight["flight_status"])
        print_endpoint("Arrival",   flight["arrival"],   arr_info, flight["flight_status"])

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()