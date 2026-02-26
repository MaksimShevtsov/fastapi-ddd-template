UPDATE refresh_tokens
SET revoked_at = :revoked_at
WHERE user_id = :user_id AND revoked_at IS NULL
