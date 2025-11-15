```shell
sudo -u postgres psql
CREATE DATABASE translator;
CREATE USER diracai WITH PASSWORD 'ajitsir';
GRANT ALL PRIVILEGES ON DATABASE translator TO diracai;
GRANT CONNECT ON DATABASE translator TO diracai;
\c translator
GRANT USAGE ON SCHEMA public TO diracai;
GRANT CREATE ON SCHEMA public TO diracai;

CREATE TABLE users (
id SERIAL PRIMARY KEY,
email VARCHAR(255) UNIQUE NOT NULL,
hashed_password VARCHAR(255) NOT NULL,
is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);
```
