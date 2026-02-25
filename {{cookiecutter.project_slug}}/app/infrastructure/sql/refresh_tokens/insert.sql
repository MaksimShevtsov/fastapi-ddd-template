INSERT INTO refresh_tokens (id, user_id, token_hash, expires_at, revoked_at, created_at)
VALUES (:id, :user_id, :token_hash, :expires_at, :revoked_at, :created_at)
