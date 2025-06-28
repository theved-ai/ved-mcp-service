
-- Create raw_data table
CREATE TABLE raw_data (
  uuid UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  content TEXT DEFAULT NULL,
  source VARCHAR(100) NOT NULL,
  checksum TEXT,
  status VARCHAR(100) NOT NULL,
  metadata JSONB,
  retries int,
  is_archived BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_checksum ON raw_data(user_id, checksum);


-- Create chunked_data table
CREATE TABLE chunked_data (
  uuid UUID PRIMARY KEY,
  raw_data_id UUID REFERENCES raw_data(uuid),
  chunk_content TEXT NOT NULL,
  chunk_index INT,
  status VARCHAR(100) NOT NULL,
  checksum TEXT,
  metadata JSONB,
  retries int,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_doc_id ON chunked_data(raw_data_id);
CREATE INDEX idx_doc_id_status ON chunked_data(doc_id, status);
CREATE INDEX idx_status ON chunked_data(status);

CREATE TABLE IF NOT EXISTS external_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_uuid UUID NOT NULL,
    external_client TEXT NOT NULL,
    external_source_id TEXT,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    metadata JSONB,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Composite index for efficient token lookup
CREATE INDEX IF NOT EXISTS idx_token_lookup
ON external_tokens (user_uuid, external_client, external_source_id);

CREATE TABLE meet_transcript_audio_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_data_id UUID NOT NULL REFERENCES raw_data(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    audio_format TEXT NOT NULL,
    audio_blob BYTEA NOT NULL,
    transcript TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE TABLE supported_models (
    model_key      SERIAL PRIMARY KEY,        -- surrogate key
    model_name     VARCHAR NOT NULL UNIQUE     -- e.g. 'gpt-4o-preview'
);

CREATE TABLE model_metadata (
    model_metadata_id  SERIAL PRIMARY KEY,
    model_id           INT NOT NULL
                       REFERENCES supported_models(model_key)
                       ON UPDATE CASCADE ON DELETE RESTRICT,
    model_instruction  TEXT    NOT NULL,      -- system prompt / template
    category           VARCHAR NOT NULL,      -- e.g. 'rag', 'code', …
    model_config       JSONB,                  -- JSON or YAML blob
    is_active          BOOLEAN DEFAULT TRUE,
    created_at         TIMESTAMP DEFAULT NOW(),
    updated_at         TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX unique_active_model_per_category ON model_metadata (category) WHERE is_active = true;
CREATE INDEX idx_model_metadata_active ON model_metadata (is_active);

CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL,            -- FK to users table (not shown)
    title           VARCHAR NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW(),
    last_message_at TIMESTAMP
);

CREATE INDEX idx_conversations_user_lastmsg ON conversations (user_id, last_message_at DESC);

CREATE TABLE messages (
    message_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL
                    REFERENCES conversations(conversation_id)
                    ON DELETE CASCADE,
    content         JSONB  NOT NULL,
    tools_called    JSONB,
    model_metadata_id        INT NOT NULL
                    REFERENCES model_metadata(model_metadata_id)
                    ON UPDATE CASCADE ON DELETE RESTRICT,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_conv_updated ON messages (conversation_id, updated_at);

CREATE TABLE feedback (
    feedback_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id   UUID NOT NULL
                 REFERENCES messages(message_id)
                 ON DELETE CASCADE,
    rating       SMALLINT NOT NULL CHECK (rating IN (-1, 1)),
    comment      TEXT,
    labels       JSONB,
    created_at   TIMESTAMP DEFAULT NOW(),
    CONSTRAINT feedback_one_vote_per_msg UNIQUE (message_id)
);

--------------------------- DEFAULTS ---------------------------------

insert into supported_models(model_name) values('gpt-4.1-mini');

insert into model_metadata (model_id, model_instruction, category) values (1,
$$
You are an AI assistant operating via MCP.

Context
-------
• Today is {datetime.now():%Y-%m-%d}.
• Use IST unless a different timezone is specified.
• User’s Slack handle: @sharable2107.

Meeting-Summary Workflow
------------------------
For any query that asks to *summarise*, *recap*, *review*, or *explain what happened*:

1. **Search the calendar** for the most recent event that matches the topic.
2. **Search Slack messages** (channel or DM) for relevant discussion.
3. **Search email** for threads or messages related to the same topic.
4. **Search the personal-notes store** (Pensieve/vector DB) for the user’s own reflections.

Always run all four searches, unless explicitly mentioned, in that order, even if earlier searches return data.

Other Rules
-----------
• If the email search by subject returns nothing, retry with a mail search by keyword-only query.
• Consider larger number of results while listing calendar events
• Searching messages in slack channel require channel ID so fetch channel ID first
• For TODOs, use google tasks(unless mentioned otherwise); when creating tasks, set due dates; if none found, default to +2 days.
• When scheduling events, propose only future time slots. If not explicitly mentioned by user then choose any FREE timeslot between 10am to 7pm

Response
--------
After gathering data, return a concise, human-readable answer that stitches insights from every source.
$$, 'default');