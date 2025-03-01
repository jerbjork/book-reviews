import db
from flask import abort

def get_password_hash(username):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    return (db.query(sql, [username]))

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
    image = (db.query(sql, [id]))
    if not image:
        abort(404)
    return image
