CREATE TABLE IF NOT EXISTS external_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_uuid UUID NOT NULL,
    external_client TEXT NOT NULL, -- e.g. 'slack', 'gmail'
    external_source_id TEXT,       -- e.g. 'T1234567890' for Slack, or user email for Gmail
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
