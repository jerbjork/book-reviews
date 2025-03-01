from flask import request, abort, session

def check_length(text, lower_limit, upper_limit):
        if len(text) < lower_limit or len(text) > upper_limit:
            abort(403)

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

def check_login():
    if not session["user_id"]:
        abort(403)