import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
TWILIO_SID       = os.getenv("TWILIO_SID")
TWILIO_TOKEN     = os.getenv("TWILIO_TOKEN")
TWILIO_FROM      = os.getenv("TWILIO_FROM")
TWILIO_TO        = os.getenv("TWILIO_TO")


def send_email_alert(flight_iata, delay_minutes, airport, to_email):
    message = Mail(
        from_email="alerts@yourdomain.com",
        to_emails=to_email,
        subject=f"⚠️ Flight {flight_iata} Delayed by {delay_minutes} min",
        html_content=f"""
            <h2>Flight Delay Alert ✈️</h2>
            <p>Your flight <strong>{flight_iata}</strong> is delayed by
            <strong>{delay_minutes} minutes</strong> at <strong>{airport}</strong>.</p>
            <p>Please check the latest status before heading to the airport.</p>
        """
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        print(f"✅ Email alert sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False


def send_sms_alert(flight_iata, delay_minutes, airport):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(
            body=f"✈️ Flight {flight_iata} is delayed by {delay_minutes} min at {airport}.",
            from_=TWILIO_FROM,
            to=TWILIO_TO
        )
        print(f"✅ SMS alert sent to {TWILIO_TO}")
        return True
    except Exception as e:
        print(f"❌ SMS failed: {e}")
        return False


def send_alerts(flight_iata, delay_minutes, airport, email=None):
    if not delay_minutes or delay_minutes <= 0:
        return

    print(f"Flight {flight_iata} delayed by {delay_minutes} min — sending alerts...")
    send_sms_alert(flight_iata, delay_minutes, airport)

    if email:
        send_email_alert(flight_iata, delay_minutes, airport, email)