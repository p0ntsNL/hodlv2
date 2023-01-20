from app import app
from flask import redirect, render_template, request, session, url_for
from model import *


@app.route("/", methods=["GET"])
def home():
    if "username" in session:
        return render_template(
            "index.html",
            active_trades=find_trades({"status": "active"}),
            finished_trades=count_documents("trades", {"status": "finished"}),
            username=finduser()[1],
        )
    else:
        if finduser()[0]:
            return redirect(url_for("login"))
            return render_template("login.html")
        else:
            return redirect(url_for("register"))
            return render_template("register.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if finduser()[0]:
            if "username" in session:
                return redirect(url_for("home"))
            else:
                return redirect(url_for("login"))
        return render_template("register.html")
    elif request.method == "POST":
        registerUser()
        return redirect(url_for("login"))


@app.route("/login", methods=["GET"])
def login():
    if request.method == "GET":
        if "username" not in session:
            if finduser()[0]:
                return render_template("login.html")
            else:
                return redirect(url_for("register"))
        else:
            return redirect(url_for("home"))


@app.route("/checkloginusername", methods=["POST"])
def checkUserlogin():
    return checkloginusername()


@app.route("/checkloginpassword", methods=["POST"])
def checkUserpassword():
    return checkloginpassword()


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))
