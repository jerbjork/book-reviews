import sqlite3
import secrets

from flask import Flask
from flask import redirect, render_template, request, session, abort, make_response, flash
import markupsafe

from messages import (get_message, update_message, delete_message,
                      get_review_id, get_review_messages, add_message)
from reviews import (latest_reviews, search_reviews, get_user_reviews,
                     get_review_data, update_review, set_review_removed, add_review)
from categories import (get_categories, get_review_categories, get_selected_categories,
                        attach_categories, detach_categories)
from users import (get_user_data, add_profile_picture, get_image, add_account, attempt_login)
from validations import check_length, check_csrf, check_login
import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    reviews = latest_reviews()
    return render_template("index.html", reviews=reviews)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/register")
def register():
    return render_template("register.html", filled={})

@app.route("/search", methods=["GET", "POST"])
def search():
    categories = get_categories()

    if request.method == "GET":
        return render_template("search.html", categories=categories)

    if request.method == "POST":
        query = request.form["query"]
        search_type = request.form["search"]
        check_length(query, 3, 100)
        results = search_reviews(search_type, query)
        return render_template("search.html", query=query, results=results, categories=categories)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", filled={})

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = attempt_login(username, password)
        if user_id:
            session["username"] = username
            session["user_id"] = user_id
            session["csrf_token"] = secrets.token_hex(16)
            flash("Log in successful")
            return redirect("/")

        flash("Incorrect username or password")
        filled = {"username": username}
        return render_template("/login.html", filled=filled)

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
    user = get_user_data(user_id)
    reviews = get_user_reviews(user_id)
    return render_template("userpage.html", user=user, reviews=reviews)

@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    check_login()

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

        add_profile_picture(image, session["user_id"])
        flash("Profile picture updated")
        return redirect("/user/" + str(session["user_id"]))

@app.route("/image/<int:user_id>")
def show_image(user_id):
    image = get_image(user_id)
    response = make_response(bytes(image[0][0]))
    response.headers.set("Content-Type", "image*")
    return response

@app.route("/edit_message/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):

    message = get_message(message_id)
    if message["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit_message.html", message=message)

    if request.method == "POST":
        check_csrf()
        content = request.form["content"]
        check_length(content, 1, 1000)
        update_message(content, message_id)
        flash("Comment updated")
        return redirect("/review/" + str(message["review_id"]))

@app.route("/remove_message/<int:message_id>", methods=["GET", "POST"])
def remove_message(message_id):

    message = get_message(message_id)
    if message["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_message.html", message=message)

    if request.method == "POST":
        check_csrf()
        review_id = get_review_id(message_id)
        if "continue" in request.form:
            delete_message(message_id)
            flash("Comment deleted")

        return redirect("/review/" + str(review_id))

@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"])
def edit_review(review_id):

    review = get_review_data(review_id)
    if review["user_id"] != session["user_id"]:
        abort(403)

    categories = get_selected_categories(review_id)
    if request.method == "GET":
        return render_template("edit_review.html", review=review, categories=categories)

    if request.method == "POST":
        check_csrf()
        title = request.form["title"]
        content = request.form["content"]
        check_length(title, 1, 100)
        check_length(content, 1, 10000)

        if update_review(title, content, review_id):
            flash("You have already posted a review with that title")
            return render_template("edit_review.html", review=review, categories=categories)

        categories = request.form.getlist("categories")
        detach_categories(review_id)
        attach_categories(categories, review_id)
        flash("Review updated")
        return redirect("/review/" + str(review_id))

@app.route("/remove_review/<int:review_id>", methods=["GET", "POST"])
def remove_review(review_id):

    review = get_review_data(review_id)
    if review["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_review.html", review=review)

    if request.method == "POST":
        check_csrf()
        if "continue" in request.form:
            set_review_removed(review_id)
            flash("Review removed")
        return redirect("/review/" + str(review_id))

@app.route("/add_review", methods=["GET", "POST"])
def new_review():
    check_login()
    categories = get_categories()

    if request.method == "GET":
        return render_template("add_review.html", categories=categories, filled={})

    if request.method == "POST":
        check_csrf()
        title = request.form["title"]
        content = request.form["content"]
        check_length(title, 1, 100)
        check_length(content, 1, 10000)
        review_id = add_review(title, content, session["user_id"])

        if not review_id:
            flash("You have already posted a review with that title")
            filled = {"content": content, "title": title}
            return render_template("add_review.html", categories=categories, filled=filled)

        attach_categories(request.form.getlist("categories"), review_id)
        flash("Review added")
        return redirect("/review/" + str(review_id))

@app.route("/review/<int:review_id>")
def show_review(review_id):

    review = get_review_data(review_id)
    categories = get_review_categories(review_id)
    messages = get_review_messages(review_id)
    return render_template("review.html", review=review, categories=categories, messages=messages)

@app.route("/create", methods=["POST"])
def create():
    if "username" in session:
        flash("Please log out first")
        return redirect(request.url)

    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    check_length(username, 4, 20)
    check_length(password1, 8, 20)

    if password1 != password2:
        flash("Passwords do not match")
        filled = {"username": username}
        return render_template("/register.html", filled=filled)
    if not add_account(username, password1):
        flash("Username is already taken")
        filled = {"username": username}
        return render_template("/register.html", filled=filled)

    flash("Account created")
    return redirect("/")

@app.route("/new_message", methods=["POST"])
def new_message():
    check_login()
    check_csrf()
    content = request.form["content"]
    review_id = request.form["review_id"]
    check_length(content, 1, 500)
    add_message(content, session["user_id"], review_id)
    flash("Comment posted")
    return redirect("/review/" + str(review_id))
