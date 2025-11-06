import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi_app.core.config import settings


def send_email(to_email: str, subject: str, message: str) -> bool:
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False


def send_phone_otp(phone_number: str) -> dict:
    """
    Mock function for sending phone OTP
    Replace with actual SMS service integration
    """
    try:
        # Replace with actual SMS service API call
        print(f"Sending OTP to {phone_number}")
        return {"success": True, "message": "OTP sent successfully"}
    except Exception as e:
        return {"error": str(e)}


def verify_mobile_otp(mobile_number: str, otp: str) -> dict:
    """
    Mock function for verifying mobile OTP
    Replace with actual SMS service verification
    """
    try:
        # Replace with actual SMS service verification
        print(f"Verifying OTP {otp} for {mobile_number}")
        return {"success": True, "message": "OTP verified successfully"}
    except Exception as e:
        return {"error": str(e)}