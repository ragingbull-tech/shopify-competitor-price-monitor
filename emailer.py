import os
import smtplib
from email.message import EmailMessage


def send_email_report(subject: str, body: str) -> bool:
    try:
        smtp_host = os.environ["SMTP_HOST"]
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_username = os.environ["SMTP_USERNAME"]
        smtp_password = os.environ["SMTP_PASSWORD"]
        report_from = os.environ["REPORT_FROM"]
        report_to = os.environ["REPORT_TO"]

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = report_from
        message["To"] = report_to
        message.set_content(body)

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

        print("Email report sent successfully.")
        return True

    except KeyError as error:
        print(f"Missing email environment variable: {error}")
        return False

    except smtplib.SMTPAuthenticationError:
        print("Email authentication failed. Check SMTP_USERNAME and SMTP_PASSWORD.")
        return False

    except smtplib.SMTPException as error:
        print(f"SMTP error while sending email: {error}")
        return False

    except Exception as error:
        print(f"Unexpected error while sending email: {error}")
        return False