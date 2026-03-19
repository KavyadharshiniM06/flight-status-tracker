import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from api import get_flight_data
from scraper import get_airport_info
from alerts import send_alerts
from app import parse_time, format_time, get_delay, format_delay

load_dotenv()
API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    flights = []
    alert_status = None

    if request.method == "POST":
        raw   = request.form.get("iata", "")
        email = request.form.get("email", "").strip() or None
        iata_codes = [i.strip().upper() for i in raw.split(",") if i.strip()]

        for iata in iata_codes:
            try:
                flight   = get_flight_data(API_KEY, iata)
                dep      = flight["departure"]
                arr      = flight["arrival"]
                dep_info = get_airport_info(dep["airport"])
                arr_info = get_airport_info(arr["airport"])

                def enrich(data, info):
                    scheduled = parse_time(data.get("scheduled"))
                    estimated = parse_time(data.get("estimated"))
                    actual    = parse_time(data.get("actual"))
                    best      = actual or estimated
                    delay     = get_delay(scheduled, best)
                    return {
                        "airport":       data.get("airport", "N/A"),
                        "country":       info.get("country", "N/A"),
                        "timezone":      info.get("timezone", "N/A"),
                        "terminal":      data.get("terminal") or "N/A",
                        "gate":          data.get("gate") or "N/A",
                        "scheduled":     format_time(scheduled),
                        "estimated":     format_time(estimated),
                        "actual":        format_time(actual),
                        "delay":         format_delay(delay, flight["flight_status"]),
                        "delay_minutes": delay
                    }

                dep_enriched = enrich(dep, dep_info)
                arr_enriched = enrich(arr, arr_info)

                # ---- alert trigger (change 25 to dep_enriched.get("delay_minutes") after testing) ----
                delay_minutes = dep_enriched.get("delay_minutes") # fake delay for testing — revert after confirming alerts work
                send_alerts(
                    flight_iata=iata,
                    delay_minutes=delay_minutes,
                    airport=dep.get("airport"),
                    email=email
                )

                if delay_minutes and delay_minutes > 0:
                    alert_status = f"⚠️ Alert sent for {iata} — delayed by {delay_minutes} min"
                else:
                    alert_status = f"✅ {iata} is on time — no alerts sent"

                flights.append({
                    "airline":   flight["airline"]["name"],
                    "iata":      flight["flight"]["iata"],
                    "status":    flight["flight_status"],
                    "departure": dep_enriched,
                    "arrival":   arr_enriched
                })

            except Exception as e:
                flights.append({"error": str(e), "iata": iata})

    return render_template("index.html", flights=flights, alert_status=alert_status)


if __name__ == "__main__":
    app.run(debug=True)