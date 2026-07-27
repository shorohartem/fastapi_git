import smtplib
from email.message import EmailMessage
from app.domain.interfaces import EmailService
from app.core.config import settings


class SMTPEmailService(EmailService):
    def send_notification(self, recipient: str, image_path: str, extracted_text: str) -> bool:
        msg = EmailMessage()
        msg["Subject"] = "Изображение проанализировано"
        msg["From"] = "test@example.com"
        msg["To"] = recipient

        body = f"""
        Изображение: {image_path}
        Распознанный текст:
        {extracted_text}
        """
        msg.set_content(body.strip())

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:

            server.send_message(msg)

        return True