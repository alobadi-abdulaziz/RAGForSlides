import os
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List

load_dotenv()

# --- Connection Configuration ---
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS").lower() == 'true',
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS").lower() == 'true',
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_verification_email(recipients: List[str], verification_link: str):
    """
    Sends a verification email to the user.
    """
    html_content = f"""
    <html>
        <body>
            <h1>Welcome to RAG App!</h1>
            <p>Thanks for signing up. Please click the link below to verify your email address:</p>
            <a href="{verification_link}">Verify Email</a>
            <p>If you did not sign up for this account, you can ignore this email.</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject="Verify Your Email for RAG App",
        recipients=recipients,
        body=html_content,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
