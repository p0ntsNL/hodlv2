# pylint: disable-all
import json

from flask import redirect, render_template, request, session, url_for
from model import *
from run import app


@app.route("/", methods=["GET"])
def home():
    if "username" in session:
        return render_template(
            "index.html",
            active_trades=get_active_trades(),
            profits=get_profits(),
            finished_trades=get_finished_trades(),
            username=finduser()[1],
        )
    else:
        if finduser()[0]:
            return redirect(url_for("login"))
        else:
            return redirect(url_for("register"))


@app.route("/configuration", methods=["GET"])
def configuration():
    if "username" in session:
        return render_template(
            "configuration.html",
            configuration=get_configuration(),
            username=finduser()[1],
        )
    else:
        if finduser()[0]:
            return redirect(url_for("login"))
        else:
            return redirect(url_for("register"))


@app.route("/logging", methods=["GET"])
def logging():
    if "username" in session:
        return render_template(
            "logging.html",
            logging=get_logging(),
            username=finduser()[1],
        )
    else:
        if finduser()[0]:
            return redirect(url_for("login"))
        else:
            return redirect(url_for("register"))


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

@app.route("/checkconfig", methods=["POST"])
def checkConfig():
    return checkconfig()


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))
