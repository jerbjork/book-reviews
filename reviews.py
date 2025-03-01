import db
from flask import abort

def latest_reviews():
    sql = """SELECT u.username, r.id, r.title, r.time, r.user_id
             FROM users u, reviews r
             WHERE u.id = r.user_id AND r.removed = 0
             ORDER BY r.id DESC
             LIMIT 20"""
    reviews = (db.query(sql, []))
    return reviews

def search_reviews(form, query):
        if form  == "category":
            sql = """SELECT u.username, r.id, r.title, r.user_id, r.removed 
                  FROM users u, reviews r, categories t, attach a 
                  WHERE t.title = ? AND a.category_id = t.id AND a.review_id = r.id AND u.id = r.user_id"""
            return (db.query(sql, [query]))
        
        else:
            sql = """SELECT u.username, r.id, r.title, r.user_id, r.removed 
                    FROM users u, reviews r
                    WHERE (u.id = r.user_id AND r.title LIKE ?)
                    OR (u.id = r.user_id AND u.username LIKE ?)"""
            return db.query(sql, ["%" + query + "%", "%" + query + "%"])

def add_review(title, content, id):
    sql = "INSERT INTO reviews (title, content, user_id, time) VALUES (?, ?, ?, datetime('now'))"
    db.execute(sql, [title, content, id])
   
def get_user_reviews(id):
    sql = "SELECT id, title, time, removed FROM reviews WHERE user_id = ?"
    return db.query(sql, [id])

def get_review_data(id):
    sql = """SELECT r.id, r.user_id, r.title, r.content, r.removed, u.username FROM reviews r, users u
             WHERE u.id = r.user_id AND r.id = ?"""
    query = db.query(sql, [id])
    if not query:
        abort(404)
    return query[0]

def update_review(title, content, id):
    sql = "UPDATE reviews SET (title, content, removed) = (?, ?, 0)  WHERE id = ?"
    db.execute(sql, [title, content, id])

def set_review_removed(id):
    sql = "UPDATE reviews SET removed = ? WHERE id = ?"
    db.execute(sql, [1, id])