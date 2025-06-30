fetch_token_by_user_id_and_client="""
SELECT access_token, refresh_token, expires_at, metadata FROM external_tokens
WHERE user_uuid = $1 AND external_client = $2
"""

update_token_by_user_id_and_client="""
UPDATE external_tokens
SET access_token = $1, refresh_token = $2, expires_at = $3, updated_at = NOW()
WHERE user_uuid = $4 AND external_client = $5
"""

fetch_chunk="""
select uuid, chunk_content from chunked_data
where uuid = ANY($1)
"""

fetch_message_data="""
select message_id, conversation_id, content, tools_called, model_metadata_id, created_at, updated_at
from messages
where message_id = ANY($1)
"""