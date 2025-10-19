CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    name TEXT,
    instructions TEXT,
    user_id INTEGER REFERENCES users,
    slug TEXT,
    image BLOB
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT,
    plural TEXT,
    slug TEXT
);

CREATE TABLE recipe_tag (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER REFERENCES recipes,
    tag_id INTEGER REFERENCES tags
);

CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY,
    name TEXT
);

CREATE TABLE recipe_ingredient (
    id INTEGER PRIMARY KEY,
    ingredient_id INTEGER REFERENCES ingredients,
    recipe_id INTEGER REFERENCES recipes,
    amount TEXT
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER REFERENCES recipes,
    user_id INTEGER REFERENCES users,
    comment TEXT,
    sent_at TEXT
);

CREATE INDEX idx_recipe_tag_tag_id ON recipe_tag(tag_id);

CREATE INDEX idx_tags_slug ON tags(slug);