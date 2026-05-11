import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_USER = os.getenv("GMAIL_USER", "your_email@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "your_app_password")


def send_hotel_email(jb_code: str, hotel_email: str, hotel_name: str,
                     guests: str, checkin: str, checkout: str, rooms: str) -> bool:
    """Send hotel booking request email via Gmail."""

    subject = f"{jb_code} – Booking Request | {hotel_name} | {checkin} – {checkout}"

    body = f"""Dear {hotel_name} Team,

I hope this message finds you well.

We would like to request availability and rates for the following booking:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BOOKING REFERENCE: {jb_code}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📅 Check-in:      {checkin}
  📅 Check-out:     {checkout}
  👥 Guests:        {guests}
  🛏  Room(s):       {rooms}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Could you please confirm availability, rates, and any applicable conditions?

We look forward to your prompt response.

Best regards,
JB Travel — Tour Operator, Almaty
"""

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = hotel_email

        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, hotel_email, msg.as_string())

        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False
