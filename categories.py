import sqlite3
from flask import abort
import db

def get_categories():
    sql = "SELECT title, id FROM categories"
    return db.query(sql)

def get_selected_categories(id):
    sql = """SELECT c.title, c.id, a.id AS selected
             FROM categories c 
             LEFT JOIN attach a
             ON a.review_id = ? AND c.id = a.category_id"""
    return (db.query(sql, [id]))

def get_review_categories(id):
    sql = "SELECT t.title FROM categories t, attach a WHERE a.review_id = ? AND t.id = a.category_id"
    return (db.query(sql, [id]))

def detach_categories(id):
    sql = "SELECT attach.id FROM attach, reviews WHERE attach.review_id = reviews.id AND reviews.id = ?"
    for attach_id in db.query(sql, [id]):
        sql = "DELETE FROM attach WHERE id = ?"
        db.execute(sql, [attach_id[0]])

def attach_categories(categories, id):
    for category_id in categories:
        sql = "INSERT INTO attach (category_id, review_id) VALUES (?, ?)"
        try:
            with db.get_connection() as conn:
                conn.execute(sql, [category_id, id])
        except sqlite3.IntegrityError:
            abort(403)