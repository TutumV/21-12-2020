CREATE TABLE IF NOT EXISTS users
(
    id       serial PRIMARY KEY  NOT NULL UNIQUE,
    email    varchar(150) UNIQUE NOT NULL,
    password varchar(150)        NOT NULL
);
