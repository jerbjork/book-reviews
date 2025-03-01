import sqlite3
from flask import abort
from werkzeug.security import generate_password_hash, check_password_hash
import db

def get_user_data(id):
    sql = "SELECT id, username, image FROM users WHERE id = ?"
    query = db.query(sql, [id])
    if not query:
        abort(404)
    return query[0]

def add_profile_picture(image, id):
    sql = "UPDATE users SET image = ? WHERE id = ?"
    db.execute(sql, [image, id])

def get_image(id):
    sql = "SELECT image FROM users WHERE id = ?"
    image = db.query(sql, [id])
    if not image:
        abort(404)
    return image

def add_account(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    try:
        with db.get_connection() as conn:
            return conn.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return None

def attempt_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    password_hash = db.query(sql, [username])
    if password_hash:
        if check_password_hash(password_hash[0][1], password):
            return password_hash[0][0]
    return None
