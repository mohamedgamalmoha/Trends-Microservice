import smtplib
from typing import Dict, Any
from email.utils import formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from jinja2 import Environment, FileSystemLoader

from app.conf import settings


def create_message(
        sender_username: str,
        sender_name: str,
        receiver_email: str,
        subject: str,
        plain_text: str = None,
        html_content: str = None
    ) -> MIMEMultipart:
    """
    Create an email message with optional plain text and HTML content.
    """
    # Create message container
    message = MIMEMultipart("alternative")
    message['From'] = formataddr(pair=(sender_name, sender_username))
    message['To'] = receiver_email
    message['Subject'] = subject

    # Always add plain text part if provided
    if plain_text:
        message.attach(
            payload=MIMEText(
                _text=plain_text,
                _subtype='plain'
            )
        )

    # Add HTML part if provided
    if html_content:
        message.attach(
            payload=MIMEText(
                _text=html_content,
                _subtype='html'
            )
        )

    return message


def render_template(template_file: str, template_data: Dict[str, Any], templates_folder: str = 'app/templates') -> str:
    """
    Render an HTML template with the provided data.
    """
    env = Environment(
        loader=FileSystemLoader(
            searchpath=templates_folder
        )
    )
    template = env.get_template(name=template_file)
    return template.render(
        ** template_data
    )


def send_email(
        receiver_email: str,
        subject: str,
        plain_text: str = None,
        template_file: str = None,
        template_data: Dict[str, Any] = None,
        sender_username: str = settings.MAIL_USERNAME,
        sender_password: str = settings.MAIL_PASSWORD,
        sender_name: str = settings.MAIL_NAME,
        sender_server: str = settings.MAIL_SERVER,
        sender_port: int = settings.MAIL_PORT
    ) -> None:
    """
    Send an email using the provided SMTP server.
    """
    assert plain_text is not None or template_file is not None
    assert (template_file is not None and template_data is not None) \
           or (template_file is None and template_data is None)

    html_content = None
    if template_file and template_data:
        html_content = render_template(template_file=template_file, template_data=template_data)

    message = create_message(
        sender_username=sender_username,
        sender_name=sender_name,
        receiver_email=receiver_email,
        subject=subject,
        plain_text=plain_text,
        html_content=html_content
    )


    with smtplib.SMTP(host=sender_server, port=sender_port) as server:
        # Start TLS for security
        server.starttls()

        # Authentication
        server.login(
            user=sender_username,
            password=sender_password
        )

        # Send email
        server.send_message(msg=message)
