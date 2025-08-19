import smtplib
from email.message import EmailMessage
from app.core.config import settings

def send_password_setup_email(to_email: str, token: str):
    """
    Sends an email to the employee with a link to set their password.
    """
    msg = EmailMessage()
    msg["Subject"] = "LeaveEase: Set Your Password"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    # Construct the link (replace localhost with your frontend URL in production)
    setup_link = f"http://localhost:3000/set-password?token={token}"

    msg.set_content(
        f"Hello,\n\n"
        f"Welcome to LeaveEase! Please set your password using the link below:\n\n"
        f"{setup_link}\n\n"
        f"This link is valid for 24 hours.\n\n"
        f"Thanks,\nLeaveEase Team"
    )

    # Connect to Gmail SMTP and send
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(msg)
        print(f"Password setup email sent to {to_email}")
    except Exception as e:
        print("Error sending email:", e)
