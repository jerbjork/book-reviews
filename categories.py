import sqlite3
from flask import abort
import db

def get_categories():
    sql = "SELECT title, id FROM categories"
    return db.query(sql)

def get_selected_categories(categoty_id):
    sql = """SELECT c.title, c.id, a.id AS selected
             FROM categories c 
             LEFT JOIN attach a
             ON a.review_id = ? AND c.id = a.category_id"""
    return db.query(sql, [categoty_id])

def get_review_categories(categoty_id):
    sql = """SELECT t.title FROM categories t, attach a
             WHERE a.review_id = ? AND t.id = a.category_id"""
    return db.query(sql, [categoty_id])

def detach_categories(review_id):
    sql = """SELECT attach.id FROM attach, reviews
             WHERE attach.review_id = reviews.id AND reviews.id = ?"""
    for attach_id in db.query(sql, [review_id]):
        sql = "DELETE FROM attach WHERE id = ?"
        db.execute(sql, [attach_id[0]])

def attach_categories(categories, review_id):
    for category_id in categories:
        sql = "INSERT INTO attach (category_id, review_id) VALUES (?, ?)"
        try:
            with db.get_connection() as conn:
                conn.execute(sql, [category_id, review_id])
        except sqlite3.IntegrityError:
            abort(403)
