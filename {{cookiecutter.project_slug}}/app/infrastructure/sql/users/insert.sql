INSERT INTO users (id, name, email, password_hash, created_at)
VALUES (:id, :name, :email, :password_hash, :created_at)
ON CONFLICT (id) DO UPDATE SET
    name = :name,
    email = :email,
    password_hash = :password_hash
