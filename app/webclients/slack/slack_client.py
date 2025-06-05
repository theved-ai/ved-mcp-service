import logging
from slack_sdk.web.async_client import AsyncWebClient, AsyncSlackResponse
from app.webclients.slack.base import SlackClient
from app.decorators.retry_decorator import async_retryable
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

class SlackClientImpl(SlackClient):
    def __init__(self):
        self.client = AsyncWebClient()

    @async_retryable()
    async def list_conversations(self, token: str) -> AsyncSlackResponse:
        try:
            return await self.client.conversations_list(token=token, types=["public_channel", "private_channel"])
        except SlackApiError as e:
            logger.error(f"Slack API error in list_conversations: {e}")
            raise
        except Exception:
            logger.exception("Unexpected error in list_conversations")
            raise

    @async_retryable()
    async def get_conversation_info(self, token: str, channel_id: str) -> AsyncSlackResponse:
        try:
            return await self.client.conversations_info(token=token, channel=channel_id)
        except SlackApiError as e:
            logger.error(f"Slack API error in get_conversation_info: {e}")
            raise
        except Exception:
            logger.exception("Unexpected error in get_conversation_info")
            raise

    @async_retryable()
    async def get_conversation_history(self, token: str, channel_id: str, limit: int) -> AsyncSlackResponse:
        try:
            return await self.client.conversations_history(token=token, channel=channel_id, limit=limit)
        except SlackApiError as e:
            logger.error(f"Slack API error in get_conversation_history: {e}")
            raise
        except Exception:
            logger.exception("Unexpected error in get_conversation_history")
            raise

    @async_retryable()
    async def get_conversation_replies(self, token: str, channel_id: str, ts: str) -> AsyncSlackResponse:
        try:
            return await self.client.conversations_replies(token=token, channel=channel_id, ts=ts)
        except SlackApiError as e:
            logger.error(f"Slack API error in get_conversation_replies: {e}")
            raise
        except Exception:
            logger.exception("Unexpected error in get_conversation_replies")
            raise

    @async_retryable()
    async def get_user_info(self, token: str, user_id: str) -> AsyncSlackResponse:
        try:
            return await self.client.users_info(token=token, user=user_id)
        except SlackApiError as e:
            logger.error(f"Slack API error in get_user_info: {e}")
            raise
        except Exception:
            logger.exception("Unexpected error in get_user_info")
            raise

    @async_retryable()
    async def list_users(self, token: str) -> AsyncSlackResponse:
        try:
            return await self.client.users_list(token=token)
        except SlackApiError as e:
            logger.error(f"Slack API error in list_users: {e}")
            raise
        except Exception:
            logger.exception("Unexpected error in list_users")
            raise

    @async_retryable()
    async def search_messages_in_conversation(self, request: dict) -> AsyncSlackResponse:
        try:
            return await self.client.conversations_history(
                token=request["bot_token"],
                channel=request["channel_id"],
                limit=request.get("limit", 100)
            )
        except SlackApiError as e:
            logger.error(f"Slack API error in search_messages_in_conversation: {e}")
            raise
        except Exception:
            logger.exception("Unexpected error in search_messages_in_conversation")
            raise

    @async_retryable()
    async def get_messages_mentioning_user(self, request: dict) -> dict:
        try:
            history_response = await self.client.conversations_history(
                token=request["bot_token"],
                channel=request["channel_id"],
                limit=request.get("limit", 100)
            )
            keyword = f"<@{request['user_id']}>"
            # Copy response data for safe manipulation
            history_data = history_response.data.copy()

            filtered = [
                msg for msg in history_data.get("messages", [])
                if keyword in msg.get("text", "")
            ]
            history_data["messages"] = filtered
            return history_data
        except SlackApiError as e:
            logger.error(f"Slack API error in get_messages_mentioning_user: {e}")
            raise
        except Exception:
            logger.exception("Unexpected error in get_messages_mentioning_user")
            raise

    @async_retryable()
    async def is_bot_member_of_conversation(self, request: dict) -> bool:
        try:
            response = await self.client.conversations_info(
                token=request["bot_token"],
                channel=request["channel_id"]
            )
            return response["channel"].get("is_member", False)
        except SlackApiError as e:
            logger.error(f"Slack API error in is_bot_member_of_conversation: {e}")
            raise
        except Exception:
            logger.exception("Unexpected error in is_bot_member_of_conversation")
            raise

    @async_retryable()
    async def get_conversation_members(self, request: dict) -> dict:
        try:
            members_resp = await self.client.conversations_members(
                token=request["bot_token"],
                channel=request["channel_id"]
            )
            member_ids = members_resp.get("members", [])
            member_info = []
            for user_id in member_ids:
                user_resp = await self.client.users_info(token=request["bot_token"], user=user_id)
                member_info.append({
                    "id": user_id,
                    "name": user_resp["user"]["name"]
                })
            return {"members": member_info}
        except SlackApiError as e:
            logger.error(f"Slack API error in get_conversation_members: {e}")
            raise
        except Exception:
            logger.exception("Unexpected error in get_conversation_members")
            raise
