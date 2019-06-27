CREATE DATABASE covalent_demo_mt
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

CREATE TABLE public_net_users (
    id SERIAL CONSTRAINT user_primary_id PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(100),
    company VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME zone NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
);

ALTER TABLE public_net_users ADD CONSTRAINT unique_email UNIQUE (email);

ALTER TABLE public_net_users ADD COLUMN is_verified boolean DEFAULT false;

ALTER TABLE public_net_users ADD COLUMN hash VARCHAR(255);

ALTER TABLE public_net_users ADD COLUMN address VARCHAR(255);

ALTER TABLE public_net_users ADD COLUMN private_key VARCHAR(255);

ALTER TABLE public_net_users RENAME COLUMN address TO eth_address;

ALTER TABLE public_net_users RENAME COLUMN private_key TO eth_private_key;

ALTER TABLE public_net_users ADD COLUMN bdb_public_key TEXT;

ALTER TABLE public_net_users ADD COLUMN bdb_private_key TEXT;

ALTER TABLE public_net_users ADD COLUMN rsa_public_key TEXT;

ALTER TABLE public_net_users ADD COLUMN rsa_private_key TEXT;
