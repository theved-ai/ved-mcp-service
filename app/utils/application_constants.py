
gmail_service_name = 'gmail'
gmail_service_version = 'v1'
gcalendar_service_name = 'calendar'
gcalendar_service_version = 'v3'
google_external_client = 'google'
google_tasks_service_name = "tasks"
google_tasks_service_version = "v1"
EMBEDDING_MODEL_NAME= 'BAAI/bge-large-en-v1.5'
QDRANT_GRPC_URL='http://localhost:6333'
THRESHOLD_VECTOR_MATCHING_SCORE=0.5

# Defaults
default_google_token_uri = 'https://oauth2.googleapis.com/token'

# Env variables
app_env_key = 'APP_ENV'
google_token_uri_key = 'GOOGLE_TOKEN_URI'
db_url_key = 'DATABASE_URL'
google_client_id_key = "GOOGLE_CLIENT_ID"
google_client_secret_key = "GOOGLE_CLIENT_SECRET"

# Exceptions
db_fetch_token_failed= 'Exception while fetching token for user and client'
db_token_update_failed='Exception while updating token for user and client'
db_fetch_chunks_failed= 'Exception while fetching chunks'
db_fetch_chat_failed= 'Exception while fetching chat for user'
fetch_token_failed= '[ExternalTokenService] Exception while fetching token metadata for user and client'
token_update_failed='[ExternalTokenService] Exception while updating token for user and client'
fetch_access_token_failed= '[ExternalTokenService] Exception while fetching access token for user and client'
listing_gcal_tool_failed="Error listing Google Calendars"
fetching_gcal_events_tool_failed="Error getting Google Calendar events"
creating_gcal_event_tool_failed="Error creating Google Calendar event"
update_gcal_event_tool_failed="Error modifying Google Calendar event"
delete_gcal_event_tool_failed="Error deleting Google Calendar event"
gmail_search_tool_failed="Error searching Gmail messages"
gmail_fetch_tool_failed="Error getting Gmail message content"
gmail_fetch_batch_tool_failed="Error getting Gmail messages content batch"
gmail_mail_send_tool_failed="Error sending Gmail message"
gmail_draft_creation_tool_failed="Error creating Gmail draft"
gmail_thread_count_tool_failed="Error getting Gmail thread content"
gmail_listing_labels_tool_failed="Error listing Gmail labels"
gmail_labels_tool_failed="Error managing Gmail label"
gmail_labels_update_tool_failed="Error modifying Gmail message labels"
gtask_listing_tool_failed="Error listing Google Tasklists"
gtask_fetch_failed="Error getting Google Tasklist"
gtask_listing_failed="Error listing Google Tasks"
gtask_fetch_task_failed="Error getting Google Task"
gtask_create_task_failed="Error creating Google Task"
gtask_modify_task_failed="Error modifying Google Task"
gtask_delete_task_failed="Error deleting Google Task"
pensieve_search_failed="Error searching Pensieve chunks"
pensieve_search_chat_failed="Error searching user's chat"