import asyncio
import base64
import logging
from email.mime.text import MIMEText
from typing import List, Optional, Literal, Any

from app.utils.gmail_util import (
    extract_message_body,
    extract_headers,
    generate_gmail_web_url,
)
from app.webclients.gmail.google_service_builder import generate_authenticated_client
from app.webclients.gmail.base import GmailClientBase

logger = logging.getLogger(__name__)
service_name = 'gmail'
version = 'v1'

class GmailClientImpl(GmailClientBase):

    async def search_messages(self, user_uuid: str, query: str, page_size: int = 10) -> Any:
        gmail_authenticated_clients = await generate_authenticated_client(user_uuid, service_name, version)

        for service in gmail_authenticated_clients:
            try:
                response = await asyncio.to_thread(
                    service.users().messages().list(userId="me", q=query, maxResults=page_size).execute
                )
                messages = response.get("messages", [])
                return messages
            except Exception as e:
                logger.error(f"Gmail API error searching messages: {e}", exc_info=True)
                raise

    async def get_message_content(self, user_uuid: str, message_id: str) -> Any:
        gmail_authenticated_clients = await generate_authenticated_client(user_uuid, service_name, version)

        for service in gmail_authenticated_clients:
            try:
                message_metadata = await asyncio.to_thread(
                    service.users().messages().get(
                        userId="me",
                        id=message_id,
                        format="metadata",
                        metadataHeaders=["Subject", "From"],
                    ).execute
                )

                headers = {
                    h["name"]: h["value"]
                    for h in message_metadata.get("payload", {}).get("headers", [])
                }
                subject = headers.get("Subject", "(no subject)")
                sender = headers.get("From", "(unknown sender)")

                message_full = await asyncio.to_thread(
                    service.users().messages().get(
                        userId="me",
                        id=message_id,
                        format="full",
                    ).execute
                )
                payload = message_full.get("payload", {})
                body_data = extract_message_body(payload)

                return {
                    "subject": subject,
                    "from": sender,
                    "body": body_data,
                    "id": message_id,
                    "web_url": generate_gmail_web_url(message_id)
                }
            except Exception as e:
                logger.error(f"Gmail API error getting message content: {e}", exc_info=True)
                raise

    async def get_messages_content_batch(self, user_uuid: str, message_ids: List[str], format: Literal["full", "metadata"] = "full") -> Any:
        gmail_authenticated_clients = await generate_authenticated_client(user_uuid, service_name, version)

        for service in gmail_authenticated_clients:
            output_messages = []
            for mid in message_ids:
                try:
                    if format == "metadata":
                        msg = await asyncio.to_thread(
                            service.users().messages().get(
                                userId="me",
                                id=mid,
                                format="metadata",
                                metadataHeaders=["Subject", "From"]
                            ).execute
                        )
                    else:
                        msg = await asyncio.to_thread(
                            service.users().messages().get(
                                userId="me",
                                id=mid,
                                format="full"
                            ).execute
                        )
                    payload = msg.get("payload", {})
                    if format == "metadata":
                        headers = extract_headers(payload, ["Subject", "From"])
                        output_messages.append({
                            "id": mid,
                            "subject": headers.get("Subject", "(no subject)"),
                            "from": headers.get("From", "(unknown sender)"),
                            "web_url": generate_gmail_web_url(mid)
                        })
                    else:
                        headers = extract_headers(payload, ["Subject", "From"])
                        body = extract_message_body(payload)
                        output_messages.append({
                            "id": mid,
                            "subject": headers.get("Subject", "(no subject)"),
                            "from": headers.get("From", "(unknown sender)"),
                            "body": body,
                            "web_url": generate_gmail_web_url(mid)
                        })
                except Exception as e:
                    logger.warning(f"Error retrieving message {mid}: {e}")
                    output_messages.append({"id": mid, "error": str(e)})
            return output_messages

    async def send_message(self, user_uuid: str, to: str, subject: str, body: str) -> Any:
        gmail_authenticated_clients = await generate_authenticated_client(user_uuid, service_name, version)

        for service in gmail_authenticated_clients:
            try:
                message = MIMEText(body)
                message["to"] = to
                message["subject"] = subject
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
                send_body = {"raw": raw_message}
                sent_message = await asyncio.to_thread(
                    service.users().messages().send(userId="me", body=send_body).execute
                )
                return sent_message.get("id")
            except Exception as e:
                logger.error(f"Gmail API error sending message: {e}", exc_info=True)
                raise

    async def draft_message(self, user_uuid: str, subject: str, body: str, to: Optional[str] = None) -> Any:
        gmail_authenticated_clients = await generate_authenticated_client(user_uuid, service_name, version)

        for service in gmail_authenticated_clients:
            try:
                message = MIMEText(body)
                message["subject"] = subject
                if to:
                    message["to"] = to
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
                draft_body = {"message": {"raw": raw_message}}
                created_draft = await asyncio.to_thread(
                    service.users().drafts().create(userId="me", body=draft_body).execute
                )
                return created_draft.get("id")
            except Exception as e:
                logger.error(f"Gmail API error creating draft: {e}", exc_info=True)
                raise

    async def get_thread_content(self, user_uuid: str, thread_id: str) -> Any:
        gmail_authenticated_clients = await generate_authenticated_client(user_uuid, service_name, version)

        for service in gmail_authenticated_clients:
            try:
                thread_response = await asyncio.to_thread(
                    service.users().threads().get(userId="me", id=thread_id, format="full").execute
                )
                messages = thread_response.get("messages", [])
                thread_content = []
                for message in messages:
                    payload = message.get("payload", {})
                    headers = extract_headers(payload, ["Subject", "From", "Date"])
                    body = extract_message_body(payload)
                    thread_content.append({
                        "from": headers.get("From"),
                        "date": headers.get("Date"),
                        "subject": headers.get("Subject"),
                        "body": body
                    })
                return thread_content
            except Exception as e:
                logger.error(f"Gmail API error getting thread content: {e}", exc_info=True)
                raise

    async def list_labels(self, user_uuid: str) -> Any:
        gmail_authenticated_clients = await generate_authenticated_client(user_uuid, service_name, version)

        for service in gmail_authenticated_clients:
            try:
                response = await asyncio.to_thread(
                    service.users().labels().list(userId="me").execute
                )
                return response.get("labels", [])
            except Exception as e:
                logger.error(f"Gmail API error listing labels: {e}", exc_info=True)
                raise

    async def manage_label(self, user_uuid: str, action: Literal["create", "update", "delete"], name: Optional[str] = None,
                           label_id: Optional[str] = None, label_list_visibility: Literal["labelShow", "labelHide"] = "labelShow",
                           message_list_visibility: Literal["show", "hide"] = "show") -> Any:
        gmail_authenticated_clients = await generate_authenticated_client(user_uuid, service_name, version)

        for service in gmail_authenticated_clients:
            try:
                if action == "create":
                    label_object = {
                        "name": name,
                        "labelListVisibility": label_list_visibility,
                        "messageListVisibility": message_list_visibility,
                    }
                    created_label = await asyncio.to_thread(
                        service.users().labels().create(userId="me", body=label_object).execute
                    )
                    return created_label

                elif action == "update":
                    current_label = await asyncio.to_thread(
                        service.users().labels().get(userId="me", id=label_id).execute
                    )
                    label_object = {
                        "id": label_id,
                        "name": name if name is not None else current_label["name"],
                        "labelListVisibility": label_list_visibility,
                        "messageListVisibility": message_list_visibility,
                    }
                    updated_label = await asyncio.to_thread(
                        service.users().labels().update(userId="me", id=label_id, body=label_object).execute
                    )
                    return updated_label

                elif action == "delete":
                    label = await asyncio.to_thread(
                        service.users().labels().get(userId="me", id=label_id).execute
                    )
                    await asyncio.to_thread(
                        service.users().labels().delete(userId="me", id=label_id).execute
                    )
                    return {"deleted": True, "name": label["name"], "id": label_id}
            except Exception as e:
                logger.error(f"Gmail API error managing label: {e}", exc_info=True)
                raise

    async def modify_message_labels(self, user_uuid: str, message_id: str, add_label_ids: Optional[List[str]] = None,
                                    remove_label_ids: Optional[List[str]] = None) -> Any:
        gmail_authenticated_clients = await generate_authenticated_client(user_uuid, service_name, version)

        for service in gmail_authenticated_clients:
            try:
                body = {}
                if add_label_ids:
                    body["addLabelIds"] = add_label_ids
                if remove_label_ids:
                    body["removeLabelIds"] = remove_label_ids
                result = await asyncio.to_thread(
                    service.users().messages().modify(userId="me", id=message_id, body=body).execute
                )
                return result
            except Exception as e:
                logger.error(f"Gmail API error modifying message labels: {e}", exc_info=True)
                raise
