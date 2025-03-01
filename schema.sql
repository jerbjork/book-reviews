CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    image BLOB
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    title TEXT UNIQUE
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    user_id INTEGER REFERENCES users,
    time INTEGER,
    removed INTEGER DEFAULT 0,
    UNIQUE (user_id, title)
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    content TEXT,
    time INTEGER,
    user_id INTEGER REFERENCES users,
    review_id INTEGER REFERENCES reviews
);

CREATE TABLE attach (
    id INTEGER PRIMARY KEY,
    category_id INTEGER REFERENCES categories ON DELETE CASCADE,
    review_id INTEGER REFERENCES reviews ON DELETE CASCADE,
    UNIQUE (category_id, review_id)
);
