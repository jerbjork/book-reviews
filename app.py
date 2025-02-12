import sqlite3
from flask import Flask, redirect, render_template, request, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

def add_review(title, content, tags):
    sql = "INSERT INTO reviews (title, content, tag_string, user_id) VALUES (?, ?, ?, ?)"
    db.execute(sql, [title, content, tags, session["user_id"]])
    review_id = db.last_insert_id()
    for tag in tags.split(", "):
        tag.lower()
        sql = "SELECT id FROM tags WHERE title = ?"
        tag_id = (db.query(sql, False, [tag]))
        if not tag_id:
            sql = "INSERT INTO tags (title) VALUES (?)"
            db.execute(sql, [tag])
            tag_id = db.last_insert_id()
        else:
            tag_id = tag_id[0]
        sql = "INSERT INTO attach (tag_id, review_id) VALUES (?, ?)"
        db.execute(sql, [tag_id, review_id])
    return review_id

@app.route("/edit/<int:reply_id>", methods=["GET", "POST"])
def edit_reply(reply_id):
    sql = "SELECT id, content, user_id FROM messages WHERE id = ?"
    reply = (db.query(sql, False, [reply_id]))
    if not reply:
        abort(404)
    if reply["user_id"] != session["user_id"]:
        abort(403)
    if request.method == "GET":
        return render_template("edit.html", reply=reply)

    if request.method == "POST":
        content = request.form["content"]
        sql = "SELECT r.id FROM reviews r, messages m WHERE m.review_id = r.id AND m.id = ?"
        review_id = (db.query(sql, False, [reply_id]))
        sql = "UPDATE messages SET content = ? WHERE id = ?"
        db.execute(sql, [content, reply_id])
        return redirect("/review/" + str(review_id[0]))
    
@app.route("/remove/<int:reply_id>", methods=["GET", "POST"])
def remove_reply(reply_id):
    sql = "SELECT id, content, user_id FROM messages WHERE id = ?"
    reply = (db.query(sql, False, [reply_id]))
    if not reply:
        abort(404)
    if reply["user_id"] != session["user_id"]:
        abort(403)
    if request.method == "GET":
        return render_template("delete.html", reply=reply)

    if request.method == "POST":
        sql = "SELECT r.id FROM reviews r, messages m WHERE m.review_id = r.id AND m.id = ?"
        review_id = (db.query(sql, False, [reply_id]))
        if "continue" in request.form:
                sql = "DELETE FROM messages WHERE id = ?"
                db.execute(sql, [reply_id])
        return redirect("/review/" + str(review_id[0]))
    
@app.route("/edit/review/<int:review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    sql = "SELECT * FROM reviews WHERE id = ?"
    review = (db.query(sql, False, [review_id]))
    if not review:
        abort(404)
    if review["user_id"] != session["user_id"]:
        abort(403)
    if request.method == "GET":
        return render_template("edit_review.html", review=review)

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        tags = request.form["tags"]
        sql = "UPDATE reviews SET (title, content, tag_string, removed) = (?, ?, ?, 0)  WHERE id = ?"
        db.execute(sql, [title, content, tags, review_id])
        return redirect("/review/" + str(review_id))
    
@app.route("/remove/review/<int:review_id>", methods=["GET", "POST"])
def remove_review(review_id):
    sql = "SELECT * FROM reviews WHERE id = ?"
    review = (db.query(sql, False, [review_id]))
    if not review:
        abort(404)
    if review["user_id"] != session["user_id"]:
        abort(403)
    if request.method == "GET":
        return render_template("delete_review.html", review=review)

    if request.method == "POST":
        if "continue" in request.form:
            sql = "UPDATE reviews SET removed = ? WHERE id = ?"
            db.execute(sql, [1, review_id])
        return redirect("/review/" + str(review_id))

@app.route("/new_review", methods=["POST"])
def new_review():
    title = request.form["title"]
    content = request.form["content"]
    tags = request.form["tags"]
    review_id = add_review(title, content, tags)
    return redirect("/review/" + str(review_id))

@app.route("/review/<int:review_id>")
def show_review(review_id):
    sql = "SELECT * FROM reviews WHERE id = ?"
    review = db.query(sql, True, [review_id])
    if not review:
            abort(404)
    else:
        review = review[0]
        sql = "SELECT t.title FROM tags t, attach a WHERE a.review_id = ? AND t.id = a.tag_id"
        tags = (db.query(sql, True, [review_id]))
        sql = "SELECT u.username, m.content, m.id, m.time FROM users u, messages m, reviews r WHERE r.id = ? AND r.id = m.review_id AND m.user_id = u.id"
        replies = (db.query(sql, True, [review_id]))
        return render_template("review.html", review=review, tags=tags, replies=replies, review_id=review_id)
    
@app.route("/browse")
def browse():
    sql = "SELECT title FROM tags"
    tags = (db.query(sql, True, []))
    return render_template("browse.html", tags=tags)

@app.route("/tags/<string:tag>")
def show_tags(tag):
    sql = "SELECT u.username, r.id, r.title, r.removed FROM users u, reviews r, tags t, attach a WHERE t.title = ? AND a.tag_id = t.id AND a.review_id = r.id AND u.id = r.user_id"
    reviews = (db.query(sql, True, [tag]))
    return render_template("tags.html", reviews=reviews, tag=tag)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "Passwords do not match"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "Username is already taken"

    return "Account created"

@app.route("/new_reply", methods=["POST"])
def new_reply():
    content = request.form["content"]
    user_id = session["user_id"]
    review_id = request.form["review_id"]
    sql = "INSERT INTO messages (content, time, user_id, review_id) VALUES (?, datetime('now'), ?, ?)"
    print([content, user_id, review_id])
    db.execute(sql, [content, user_id, review_id])
    return redirect("/review/" + str(review_id))
    


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    
    password_hash = (db.query(sql, False, [username]))
    if password_hash:

        if check_password_hash(password_hash[1], password):
            session["username"] = username
            session["user_id"] = password_hash[0]
            return redirect("/")

    return "Incorrect username or password"

@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
    return redirect("/")