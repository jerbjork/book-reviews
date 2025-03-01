from flask import request, abort, session

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