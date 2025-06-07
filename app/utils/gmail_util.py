import base64
from typing import List, Dict


def extract_message_body(payload):
    """
    Extracts all text/plain and text/html content and attachment metadata from Gmail message payload.

    Args:
        payload (dict): Gmail API message payload

    Returns:
        str: A combined plain-text body, including attachment info
    """
    plain_text_parts = []
    html_text_parts = []
    attachments = []

    parts = [payload] if "parts" not in payload else payload.get("parts", [])
    part_queue = list(parts)  # BFS traversal of parts

    while part_queue:
        part = part_queue.pop(0)
        mime_type = part.get("mimeType", "")
        body = part.get("body", {})
        data = body.get("data")
        filename = part.get("filename")

        if mime_type == "text/plain" and data:
            decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            plain_text_parts.append(decoded)

        elif mime_type == "text/html" and data:
            decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            html_text_parts.append(decoded)

        elif mime_type.startswith("multipart/") and "parts" in part:
            part_queue.extend(part["parts"])

        elif filename and body.get("attachmentId"):
            attachments.append({
                "filename": filename,
                "mime_type": mime_type,
                "attachment_id": body["attachmentId"],
                "size": body.get("size", "unknown")
            })

    # Build final message
    message_text = "\n\n".join(plain_text_parts).strip()

    # Fallback to HTML if no plain text
    if not message_text and html_text_parts:
        message_text = "\n\n".join(html_text_parts).strip()

    # Add formatted attachment summary
    if attachments:
        attachment_texts = [
            f"[Attachment] {a['filename']} ({a['mime_type']}, size: {a['size']})"
            for a in attachments
        ]
        message_text += "\n\nAttachments:\n" + "\n".join(attachment_texts)

    return message_text




def extract_headers(payload: dict, header_names: List[str]) -> Dict[str, str]:
    """
    Extract specified headers from a Gmail message payload.

    Args:
        payload: The message payload from Gmail API
        header_names: List of header names to extract

    Returns:
        Dict mapping header names to their values
    """
    headers = {}
    for header in payload.get("headers", []):
        if header["name"] in header_names:
            headers[header["name"]] = header["value"]
    return headers


def generate_gmail_web_url(item_id: str, account_index: int = 0) -> str:
    """
    Generate Gmail web interface URL for a message or thread ID.
    Uses #all to access messages from any Gmail folder/label (not just inbox).

    Args:
        item_id: Gmail message ID or thread ID
        account_index: Google account index (default 0 for primary account)

    Returns:
        Gmail web interface URL that opens the message/thread in Gmail web interface
    """
    return f"https://mail.google.com/mail/u/{account_index}/#all/{item_id}"