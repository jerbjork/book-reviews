import sqlite3
import secrets
from flask import Flask, redirect, render_template, request, session, abort, make_response, flash
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
app = Flask(__name__)
app.secret_key = config.secret_key

def check_length(text, lower_limit, upper_limit):
        if len(text) < lower_limit:
            abort(411)
            redirect(request.url)
        if len(text) > upper_limit:
            abort(413)
            redirect(request.url)

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/")
def index():
    sql = """SELECT u.username, r.id, r.title, r.time, r.user_id
             FROM users u, reviews r
             WHERE u.id = r.user_id AND r.removed = 0
             ORDER BY r.id DESC
             LIMIT 20"""
    reviews = (db.query(sql, []))
    return render_template("index.html", reviews=reviews)

@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html")
    
    if request.method == "POST":
        query = request.form["query"]
        check_length(query, 3, 100)
        sql = """SELECT u.username, r.id, r.title, r.user_id, r.removed 
                FROM users u, reviews r
                WHERE (u.id = r.user_id AND r.title LIKE ?)
                OR (u.id = r.user_id AND u.username LIKE ?)"""
        results = db.query(sql, ["%" + query + "%", "%" + query + "%"])
        return render_template("search.html", query=query, results=results)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        password_hash = (db.query(sql, [username]))
        if password_hash:

            if check_password_hash(password_hash[0][1], password):
                session["username"] = username
                session["user_id"] = password_hash[0][0]
                session["csrf_token"] = secrets.token_hex(16)
                flash("Log in successfull")
                return redirect("/")
        flash("Incorrect username or password")
        return redirect("/login")

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["username"]
        del session["user_id"]
        del session["csrf_token"]
        flash("Logged out successfully")
    return redirect("/")

@app.route("/user/<int:user_id>", methods=["GET"])
def show_user(user_id):
    sql = "SELECT * FROM users WHERE id = ?"
    query = db.query(sql, [user_id])
    if not query:
        abort(404)

    sql = "SELECT * FROM reviews WHERE user_id = ?"
    reviews = db.query(sql, [user_id])
    sql = "SELECT * FROM messages WHERE user_id = ?"
    messages = db.query(sql, [user_id])
    return render_template("userpage.html", user=query[0], reviews=reviews, messages=messages)

@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    if not session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("add_image.html")

    if request.method == "POST":
        check_csrf()
        file = request.files["image"]
        if not file.filename.endswith((".jpg", ".jpeg", ".png")):
            flash("Incorrect file format")
            return redirect("/add_image")
        
        image = file.read()
        if len(image) > 1000 * 1024:
            flash("Filesize exceeds 1 MB")
            return redirect("/add_image")
        
        sql = "UPDATE users SET image = ? WHERE id = ?"
        db.execute(sql, [image, session["user_id"]])
        flash("Profile picture updated")
        return redirect("/user/" + str(session["user_id"]))
    
@app.route("/image/<int:user_id>")
def show_image(user_id):
    sql = "SELECT image FROM users WHERE id = ?"
    image = (db.query(sql, [user_id]))
    if not image:
        abort(404)

    response = make_response(bytes(image[0][0]))
    response.headers.set("Content-Type", "image*")
    return response

@app.route("/edit_message/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    sql = "SELECT * FROM messages WHERE id = ?"
    query = db.query(sql, [message_id])
    if not query:
        abort(404)

    message = query[0]
    if message["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit_message.html", message=message)

    if request.method == "POST":
        check_csrf()
        content = request.form["content"]
        check_length(content, 1, 1000)
        sql = "UPDATE messages SET content = ? WHERE id = ?"
        db.execute(sql, [content, message_id])
        sql = "SELECT r.id FROM reviews r, messages m WHERE m.review_id = r.id AND m.id = ?"
        review_id = db.query(sql, [message_id])[0][0]
        flash("Comment updated")
        return redirect("/review/" + str(review_id))
    
@app.route("/remove_message/<int:message_id>", methods=["GET", "POST"])
def remove_message(message_id):
    sql = "SELECT * FROM messages WHERE id = ?"
    query = db.query(sql, [message_id])
    if not query:
        abort(404)

    message = query[0]
    if message["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_message.html", message=message)

    if request.method == "POST":
        check_csrf()

        if "continue" in request.form:
                sql = "SELECT r.id FROM reviews r, messages m WHERE m.review_id = r.id AND m.id = ?"
                review_id = db.query(sql, [message_id])[0][0]
                sql = "DELETE FROM messages WHERE id = ?"
                flash("Comment deleted")
                db.execute(sql, [message_id])

        return redirect("/review/" + str(review_id))
    
@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    sql = "SELECT * FROM reviews WHERE id = ?"
    query = db.query(sql, [review_id])
    if not query:
        abort(404)

    review = query[0]
    if review["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit_review.html", review=review)

    if request.method == "POST":
        check_csrf()
        title = request.form["title"]
        content = request.form["content"]
        check_length(title, 1, 100)
        check_length(content, 1, 10000)
        sql = "UPDATE reviews SET (title, content, removed) = (?, ?, 0)  WHERE id = ?"
        db.execute(sql, [title, content, review_id])
        flash("Review updated")
        return redirect("/review/" + str(review_id))
    
@app.route("/remove_review/<int:review_id>", methods=["GET", "POST"])
def remove_review(review_id):
    sql = "SELECT * FROM reviews WHERE id = ?"
    review = (db.query(sql, [review_id]))
    if not review:
        abort(404)

    if review[0]["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_review.html", review=review[0])

    if request.method == "POST":
        check_csrf()
        if "continue" in request.form:
            sql = "UPDATE reviews SET removed = ? WHERE id = ?"
            db.execute(sql, [1, review_id])
        flash("Review removed")
        return redirect("/review/" + str(review_id))

@app.route("/add_review", methods=["GET", "POST"])
def new_review():
    if request.method == "GET":
        return render_template("add_review.html")
    
    if request.method == "POST":
        check_csrf()
        title = request.form["title"]
        content = request.form["content"]
        tags = request.form["tags"]
        check_length(title, 1, 100)
        check_length(content, 1, 10000)
        check_length(tags, 1, 100)
        sql = "INSERT INTO reviews (title, content, user_id, time) VALUES (?, ?, ?, datetime('now'))"
        db.execute(sql, [title, content, session["user_id"]])
        review_id = db.last_insert_id()

        for tag in tags.split(", "):
            tag.lower()
            sql = "SELECT id FROM tags WHERE title = ?"
            tag_id = (db.query(sql, [tag]))
            if not tag_id:
                sql = "INSERT INTO tags (title) VALUES (?)"
                db.execute(sql, [tag])
                tag_id = db.last_insert_id()

            else:
                tag_id = tag_id[0][0]
            sql = "INSERT INTO attach (tag_id, review_id) VALUES (?, ?)"
            print(tag_id, review_id)
            db.execute(sql, [tag_id, review_id])

        flash("Review added")
        return redirect("/review/" + str(review_id))

@app.route("/review/<int:review_id>")
def show_review(review_id):
    sql = "SELECT * FROM reviews WHERE id = ?"
    query = db.query(sql, [review_id])
    if not query:
        abort(404)

    review = query[0]
    sql = "SELECT t.title FROM tags t, attach a WHERE a.review_id = ? AND t.id = a.tag_id"
    tags = (db.query(sql, [review_id]))
    sql = """SELECT u.username, m.content, m.id, m.time, m.user_id 
             FROM users u, messages m, reviews r 
             WHERE r.id = ? AND r.id = m.review_id AND m.user_id = u.id"""
    messages = (db.query(sql, [review_id]))
    sql = "SELECT users.username FROM users, reviews WHERE users.id = reviews.user_id AND reviews.id = ?"
    user = db.query(sql, [review_id])[0]
    return render_template("review.html", review=review, tags=tags, messages=messages, user=user)
    
@app.route("/browse")
def browse():
    sql = "SELECT title FROM tags"
    tags = db.query(sql)
    return render_template("browse.html", tags=tags)

@app.route("/tags/<string:tag>")
def show_tags(tag):
    sql = """SELECT u.username, r.id, r.title, r.user_id, r.removed 
             FROM users u, reviews r, tags t, attach a 
             WHERE t.title = ? AND a.tag_id = t.id AND a.review_id = r.id AND u.id = r.user_id"""
    reviews = (db.query(sql, [tag]))
    return render_template("tags.html", reviews=reviews, tag=tag)

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    check_length(username, 4, 20)
    check_length(password1, 8, 20)

    if password1 != password2:
        return "Passwords do not match"
    
    password_hash = generate_password_hash(password1)
    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])

    except sqlite3.IntegrityError:
        flash("Username is already taken")
        return redirect(request.url)
    
    flash("Account created")
    return redirect("/")

@app.route("/new_message", methods=["POST"])
def new_message():
    check_csrf()
    content = request.form["content"]
    review_id = request.form["review_id"]
    check_length(content, 1, 500)
    sql = "INSERT INTO messages (content, time, user_id, review_id) VALUES (?, datetime('now'), ?, ?)"
    db.execute(sql, [content, session["user_id"], review_id])
    flash("Comment posted")
    return redirect("/review/" + str(review_id))