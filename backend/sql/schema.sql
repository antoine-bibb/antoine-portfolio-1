CREATE TYPE plan_type AS ENUM ('guest', 'free', 'paid');
CREATE TYPE clip_status AS ENUM ('pending', 'processing', 'complete', 'failed');

CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email TEXT UNIQUE,
  password_hash TEXT,
  plan_type plan_type NOT NULL DEFAULT 'free',
  usage_count_total INTEGER NOT NULL DEFAULT 0,
  monthly_clip_count INTEGER NOT NULL DEFAULT 0,
  monthly_reset_date TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE guest_sessions (
  id BIGSERIAL PRIMARY KEY,
  ip_address INET NOT NULL,
  fingerprint TEXT NOT NULL,
  clips_generated INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (ip_address, fingerprint)
);

CREATE TABLE clips (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  guest_session_id BIGINT REFERENCES guest_sessions(id),
  source_video_url TEXT NOT NULL,
  output_video_url TEXT,
  status clip_status NOT NULL DEFAULT 'pending',
  virality_score INTEGER CHECK (virality_score BETWEEN 0 AND 100),
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE usage_events (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  guest_session_id BIGINT REFERENCES guest_sessions(id),
  clip_id BIGINT REFERENCES clips(id),
  action TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE subscriptions (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  stripe_customer_id TEXT NOT NULL,
  stripe_subscription_id TEXT NOT NULL,
  status TEXT NOT NULL,
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  UNIQUE (stripe_subscription_id)
);

CREATE TABLE payments (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  stripe_payment_intent_id TEXT NOT NULL UNIQUE,
  amount NUMERIC(10,2) NOT NULL,
  currency TEXT NOT NULL DEFAULT 'usd',
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_clips_user_created ON clips(user_id, created_at DESC);
CREATE INDEX idx_guest_lookup ON guest_sessions(ip_address, fingerprint);
CREATE INDEX idx_usage_user_created ON usage_events(user_id, created_at DESC);
