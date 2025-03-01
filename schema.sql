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

INSERT INTO categories (title) VALUES ("Adult");
INSERT INTO categories (title) VALUES ("Adventure");
INSERT INTO categories (title) VALUES ("Childrens");
INSERT INTO categories (title) VALUES ("Contemporary");
INSERT INTO categories (title) VALUES ("Crime");
INSERT INTO categories (title) VALUES ("Fiction");
INSERT INTO categories (title) VALUES ("History");
INSERT INTO categories (title) VALUES ("Horror");
INSERT INTO categories (title) VALUES ("Mystery");
INSERT INTO categories (title) VALUES ("Non-fiction");
INSERT INTO categories (title) VALUES ("Philosophy");
INSERT INTO categories (title) VALUES ("Poetry");
INSERT INTO categories (title) VALUES ("Politics");
INSERT INTO categories (title) VALUES ("Romance");
INSERT INTO categories (title) VALUES ("Science");
INSERT INTO categories (title) VALUES ("Science Fiction");
INSERT INTO categories (title) VALUES ("Young-adult");
INSERT INTO categories (title) VALUES ("War");