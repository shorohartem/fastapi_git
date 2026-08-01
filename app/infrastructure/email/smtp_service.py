import smtplib
from email.message import EmailMessage
from app.domain.interfaces import EmailService
from app.core.config import settings


class SMTPEmailService(EmailService):
    def send_notification(self, recipient: str, image_path: str, extracted_text: str) -> bool:
        msg = EmailMessage()
        msg["Subject"] = "Изображение проанализировано"
        msg["From"] = (
            settings.NOTIFICATION_EMAIL
            or settings.SMTP_USER
            or "noreply@example.com"
        )
        msg["To"] = recipient

        body = f"""
        Изображение: {image_path}
        Распознанный текст:
        {extracted_text}
        """
        msg.set_content(body.strip())

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        return True
