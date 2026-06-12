import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPException

logger = logging.getLogger(__name__)

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')



def send_email(to, subject, body):
    message = MIMEMultipart()
    message["From"] = EMAIL_HOST_USER
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))
    server = smtplib.SMTP(host=EMAIL_HOST, port=EMAIL_PORT)
    try:
        server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.send_message(msg=message, from_addr=EMAIL_HOST_USER, to_addrs=to)
        logger.info("Письмо успешно отправлено!")
    except SMTPException as e:
        logger.error(f"Произошла SMTP ошибка при отправке письма: {e}")
    finally:
        server.quit()
