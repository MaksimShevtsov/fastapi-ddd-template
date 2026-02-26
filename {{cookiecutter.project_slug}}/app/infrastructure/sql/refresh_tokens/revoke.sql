UPDATE refresh_tokens
SET revoked_at = :revoked_at
WHERE id = :id
