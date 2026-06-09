import os
from twilio.rest import Client

TWILIO_SID   = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM  = os.getenv("TWILIO_FROM")


def send_sms_alert(flight_iata, delay_minutes, airport, to_number):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(
            body=f"✈️ Flight {flight_iata} is delayed by {delay_minutes} min at {airport}.",
            from_=TWILIO_FROM,
            to=to_number
        )
        print(f"✅ SMS alert sent to {to_number}")
        return True
    except Exception as e:
        print(f"❌ SMS failed: {e}")
        return False


def send_alerts(flight_iata, delay_minutes, airport, phone):
    if not delay_minutes or delay_minutes <= 0:
        return
    if not phone:
        print("No phone number on file — skipping SMS")
        return

    print(f"Flight {flight_iata} delayed by {delay_minutes} min — sending SMS to {phone}...")
    send_sms_alert(flight_iata, delay_minutes, airport, phone)