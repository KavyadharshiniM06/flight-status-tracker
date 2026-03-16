import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from api import get_flight_data
from scraper import get_airport_info
from app import parse_time, format_time, get_delay, format_delay

load_dotenv()
API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    flight_data = None
    error = None

    if request.method == "POST":
        iata = request.form.get("iata", "").strip().upper()
        try:
            flight = get_flight_data(API_KEY, iata)

            dep = flight["departure"]
            arr = flight["arrival"]
            dep_info = get_airport_info(dep["airport"])
            arr_info = get_airport_info(arr["airport"])

            def enrich(data, info):
                scheduled = parse_time(data.get("scheduled"))
                estimated = parse_time(data.get("estimated"))
                actual = parse_time(data.get("actual"))
                best = actual or estimated
                delay = get_delay(scheduled, best)
                return {
                    "airport":   data.get("airport", "N/A"),
                    "country":   info.get("country", "N/A"),
                    "timezone":  info.get("timezone", "N/A"),
                    "terminal":  data.get("terminal") or "N/A",
                    "gate":      data.get("gate") or "N/A",
                    "scheduled": format_time(scheduled),
                    "estimated": format_time(estimated),
                    "actual":    format_time(actual),
                    "delay":     format_delay(delay, flight["flight_status"])
                }

            flight_data = {
                "airline": flight["airline"]["name"],
                "iata":    flight["flight"]["iata"],
                "status":  flight["flight_status"],
                "departure": enrich(dep, dep_info),
                "arrival":   enrich(arr, arr_info)
            }
        except Exception as e:
            error = str(e)

    return render_template("index.html", flight=flight_data, error=error)


if __name__ == "__main__":
    app.run(debug=True)