from flask import Flask
app = Flask(__name__)

from views import *

if __name__ == "__main__":
    app.run(host="localhost", port="8080", debug="true")
