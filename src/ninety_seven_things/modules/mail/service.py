# Standard Library Imports
import base64
import logging
import pathlib
from typing import Dict

# 3rd-Party Imports
import sendgrid
from beanie import PydanticObjectId
from jinja2 import Environment, PackageLoader, Template, select_autoescape
from pydantic.networks import EmailStr
from python_http_client.exceptions import ForbiddenError
from sendgrid.helpers.mail import Mail

# Application-Local Imports
from wj.core.config import settings
from wj.modules.address import schemas as address_schemas
from wj.modules.mail import schemas as mail_schemas

# Local Folder Imports
from .exceptions import MailException

jinja_env = Environment(loader=PackageLoader("wj"), autoescape=select_autoescape())

logger = logging.getLogger(settings.LOG_NAME)


def create_attachment(attachment_create: mail_schemas.AttachmentCreate) -> sendgrid.Attachment:
    encoded_contents = base64.b64encode(attachment_create.raw_contents).decode()

    attachment = sendgrid.Attachment()

    attachment.file_content = sendgrid.FileContent(encoded_contents)
    attachment.file_type = sendgrid.FileType(attachment_create.file_type)
    attachment.file_name = attachment_create.destination_file_name
    attachment.disposition = sendgrid.Disposition("attachment")
    attachment.content_id = attachment_create.content_id

    return attachment


def delete_attachment(path: pathlib.Path) -> None:
    path.unlink()


def send_mail(
    mail_to: EmailStr | str,
    subject_template: Template,
    body_template: Template,
    attachment: mail_schemas.AttachmentCreate = None,
    environment: Dict = None,
) -> None:
    if environment is None:
        environment = {}

    subject = subject_template.render(environment)
    body = body_template.render(environment)

    message = Mail(from_email=settings.MAIL_FROM_ADDRESS, to_emails=mail_to, subject=subject, html_content=body)

    sendgrid_client = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)

    if attachment:
        message.attachment = create_attachment(attachment)

    try:
        sendgrid_client.send(message)
    except ForbiddenError as exc:
        message = "Failed to send mail = received HTTP 403 from mail provider API"
        raise MailException(message=message) from exc
    finally:
        if attachment:
            delete_attachment(path=attachment.source_file_name)


def send_booking_reminder_mail(
    mail_to: EmailStr | str,
    given_name: str,
    family_name: str | None,
    booking_start: str,
    booking_end: str,
    booking_id: PydanticObjectId,
    location: address_schemas.Address,
    attachment_path: pathlib.Path,
) -> None:
    subject_template = jinja_env.from_string(f"{settings.ENTITY_NAME} - Booking Reminder")
    body_template = jinja_env.get_template("booking_reminder.html")

    with open(attachment_path, "rb") as f:
        attachment_contents = f.read()
        f.close()

    attachment = mail_schemas.AttachmentCreate(
        raw_contents=attachment_contents,
        file_type="text/calendar",
        source_file_name=attachment_path,
        destination_file_name=f"{location}_booking.ics",
        content_id="Example Content ID",
    )

    send_mail(
        mail_to=mail_to,
        subject_template=subject_template,
        body_template=body_template,
        attachment=attachment,
        environment={
            "project_name": settings.ENTITY_NAME,
            "email": mail_to,
            "given_name": given_name,
            "family_name": family_name,
            "booking_start": booking_start,
            "booking_end": booking_end,
            "booking_id": booking_id,
            "location": location,
        },
    )

    # delete_attachment(attachment_path=attachment_path)


def send_internal_server_mail(mail_to: EmailStr | str, body: Dict) -> None:
    subject_template = jinja_env.from_string(f"{settings.PROJECT_NAME} - Internal Server Error")
    body_template = jinja_env.get_template("internal_server_error.html")

    send_mail(
        mail_to=mail_to,
        subject_template=subject_template,
        body_template=body_template,
        environment={"project_name": settings.PROJECT_NAME, "body": body, "email": mail_to},
    )


def send_forgot_password_mail(
    mail_to: EmailStr | str,
    given_name: str,
    family_name: str | None,
    token: str,
    base_url: str,
) -> None:
    subject_template = jinja_env.from_string(f"{settings.ENTITY_NAME} - Password recovery for {given_name}")
    body_template = jinja_env.get_template("forgot_password.html")
    link = f"{base_url}/reset-password?token={token}"

    send_mail(
        mail_to=mail_to,
        subject_template=subject_template,
        body_template=body_template,
        environment={
            "project_name": settings.ENTITY_NAME,
            "given_name": given_name,
            "family_name": family_name,
            "email": mail_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def send_reset_password_mail(mail_to: EmailStr | str, given_name: str, family_name: str | None, base_url: str) -> None:
    subject_template = jinja_env.from_string(f"{settings.ENTITY_NAME} - Password has been reset for {given_name}")
    body_template = jinja_env.get_template("reset_password.html")

    send_mail(
        mail_to=mail_to,
        subject_template=subject_template,
        body_template=body_template,
        environment={
            "project_name": settings.ENTITY_NAME,
            "given_name": given_name,
            "family_name": family_name,
            "email": mail_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": base_url,
        },
    )


def send_new_account_mail(mail_to: EmailStr | str, full_name: str, dashboard_link: str) -> None:
    subject_template = jinja_env.from_string(f"{settings.ENTITY_NAME} - New account for {full_name}")
    body_template = jinja_env.get_template("new_account.html")

    send_mail(
        mail_to=mail_to,
        subject_template=subject_template,
        body_template=body_template,
        environment={
            "project_name": settings.ENTITY_NAME,
            "full_name": full_name,
            "email": mail_to,
            "dashboard_link": dashboard_link,
        },
    )


def send_new_account_confirmation_mail(
    mail_to: EmailStr | str, given_name: str, family_name: str | None, confirmation_link: str
) -> None:
    if family_name:
        full_name = f"{given_name} {family_name}"
    else:
        full_name = given_name

    subject_template = jinja_env.from_string(f"{settings.ENTITY_NAME} - Account verification for {full_name}")
    body_template = jinja_env.get_template("email_confirmation.html")

    send_mail(
        mail_to=mail_to,
        subject_template=subject_template,
        body_template=body_template,
        environment={
            "project_name": settings.ENTITY_NAME,
            "full_name": full_name,
            "email": mail_to,
            "confirmation_link": confirmation_link,
        },
    )
