import sqlite3
from flask import g

def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()

def query(sql, all: bool, params=[]):
    con = get_connection()
    if all:
        result = con.execute(sql, params).fetchall()
    else:
        result = con.execute(sql, params).fetchone()
    con.close()
    return result

def last_insert_id():
    return g.last_insert_id