CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    title TEXT UNIQUE
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    user_id INTEGER REFERENCES users
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
