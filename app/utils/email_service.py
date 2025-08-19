# app/services/email_service.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USERNAME,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_FROM,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_SERVER,
    MAIL_TLS=settings.SMTP_TLS,
    MAIL_SSL=settings.SMTP_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True   # Add this (important for Gmail/Outlook etc.)
)

async def send_setup_email(to_email: str, setup_link: str):
    message = MessageSchema(
        subject="Set up your LeaveEase password",
        recipients=[to_email],
        body=f"""
        <html>
            <body>
                <p>Hello,</p>
                <p>Click the link below to set up your password:</p>
                <a href="{setup_link}">{setup_link}</a>
                <p>Thank you!</p>
            </body>
        </html>
        """,
        subtype="html"
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        print(f"✅ Email sent successfully to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

