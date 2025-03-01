import db
from flask import abort

def get_message(id):
    sql = "SELECT id, content, user_id, review_id FROM messages WHERE id = ?"
    query = db.query(sql, [id])
    if not query:
        abort(404)
    return query[0]

def update_message(content, id):
    sql = "UPDATE messages SET content = ? WHERE id = ?"
    db.execute(sql, [content, id])

def get_review_id(message_id):
    sql = "SELECT review_id FROM messages WHERE id = ?"
    return db.query(sql, [message_id])[0][0]

def delete_message(id):
    sql = "DELETE FROM messages WHERE id = ?"
    db.execute(sql, [id])

def get_review_messages(id):
    sql = """SELECT u.username, m.content, m.id, m.time, m.user_id 
             FROM users u, messages m, reviews r 
             WHERE r.id = ? AND r.id = m.review_id AND m.user_id = u.id"""
    return (db.query(sql, [id]))

def add_message(content, user, id):
    sql = "INSERT INTO messages (content, time, user_id, review_id) VALUES (?, datetime('now'), ?, ?)"
    db.execute(sql, [content, user, id])