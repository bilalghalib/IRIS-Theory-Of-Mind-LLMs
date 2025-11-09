-- Aperture Database Schema for Supabase
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== USERS ====================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id TEXT UNIQUE NOT NULL,  -- Customer's internal user ID
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_external_id ON users(external_id);

-- ==================== CONVERSATIONS ====================

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- ==================== MESSAGES ====================

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    aperture_link TEXT,  -- Short link for "Why this response?"
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- ==================== CONSTRUCTS ====================

CREATE TABLE constructs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type TEXT NOT NULL,  -- 'theory_of_mind', 'skill_profile', 'custom', etc.
    name TEXT NOT NULL,
    description TEXT,
    config JSONB NOT NULL,  -- JSON configuration for the construct
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_constructs_user_id ON constructs(user_id);
CREATE INDEX idx_constructs_type ON constructs(type);

-- ==================== ASSESSMENTS ====================

CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    construct_id UUID REFERENCES constructs(id) ON DELETE SET NULL,
    element TEXT NOT NULL,  -- What aspect (e.g., 'technical_confidence', 'emotion')

    value_type TEXT NOT NULL CHECK (value_type IN ('score', 'range', 'tag', 'text')),
    value_data JSONB NOT NULL,  -- Actual value (format depends on value_type)

    reasoning TEXT NOT NULL,  -- LLM explanation
    confidence NUMERIC(3,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),

    user_corrected BOOLEAN DEFAULT FALSE,
    observation_count INTEGER DEFAULT 1,

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_assessments_user_id ON assessments(user_id);
CREATE INDEX idx_assessments_element ON assessments(element);
CREATE INDEX idx_assessments_confidence ON assessments(confidence);
CREATE INDEX idx_assessments_updated_at ON assessments(updated_at);

-- ==================== EVIDENCE ====================

CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,  -- The actual user message
    context TEXT,  -- Surrounding conversation context
    confidence_contribution NUMERIC(3,2) DEFAULT 0.5,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_evidence_assessment_id ON evidence(assessment_id);
CREATE INDEX idx_evidence_timestamp ON evidence(timestamp);

-- ==================== RESPONSE TRACKING ====================
-- For "Why this response?" short links

CREATE TABLE response_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    short_id TEXT UNIQUE NOT NULL,  -- Short identifier (e.g., 'a8f2x')
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    assessment_ids UUID[] DEFAULT '{}',  -- Array of assessment IDs used for this response
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_response_tracking_short_id ON response_tracking(short_id);

-- ==================== TRIGGERS ====================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_constructs_updated_at BEFORE UPDATE ON constructs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assessments_updated_at BEFORE UPDATE ON assessments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==================== ROW LEVEL SECURITY (optional, for future) ====================
-- Uncomment if you want to enable RLS

-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE constructs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE response_tracking ENABLE ROW LEVEL SECURITY;

-- Example RLS policy (customize as needed)
-- CREATE POLICY "Users can only see their own data"
--     ON users FOR SELECT
--     USING (auth.uid()::text = external_id);
