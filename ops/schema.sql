-- Enable UUIDs (Postgres 13+)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) ON DELETE SET NULL,
  role TEXT CHECK (role IN ('driver','rider','partner','general')),
  name TEXT,
  email TEXT,
  phone TEXT,
  city TEXT,
  zip TEXT,
  verified_email BOOLEAN DEFAULT FALSE,
  verified_phone BOOLEAN DEFAULT FALSE,
  sentiment_avg NUMERIC DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
  channel TEXT CHECK (channel IN ('web','sms','whatsapp','email','social','voice')),
  status TEXT DEFAULT 'open',
  last_intent TEXT,
  last_summary TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  role TEXT CHECK (role IN ('user','assistant','system')) NOT NULL,
  content TEXT NOT NULL,
  sentiment NUMERIC,
  meta JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- scheduled callbacks / nurtures
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
  type TEXT CHECK (type IN ('follow_up','callback')) NOT NULL,
  run_at TIMESTAMPTZ NOT NULL,
  payload JSONB,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- simple helper to keep updated_at fresh
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

CREATE TRIGGER contacts_updated BEFORE UPDATE ON contacts
FOR EACH ROW EXECUTE PROCEDURE set_updated_at();

CREATE TRIGGER conversations_updated BEFORE UPDATE ON conversations
FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
