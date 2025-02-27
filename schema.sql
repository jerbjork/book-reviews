CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    image BLOB
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    title TEXT UNIQUE
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    user_id INTEGER REFERENCES users,
    time INTEGER,
    removed INTEGER DEFAULT 0
);


CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    content TEXT,
    time INTEGER,
    user_id INTEGER REFERENCES users,
    review_id INTEGER REFERENCES reviews
);

CREATE TABLE attach (
    tag_id INTEGER REFERENCES tags,
    review_id INTEGER REFERENCES reviews
);
