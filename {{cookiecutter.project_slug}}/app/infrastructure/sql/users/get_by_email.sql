SELECT id, name, email, password_hash, created_at, updated_at
FROM users
WHERE email = :email
