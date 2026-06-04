import os

from flask import Flask

app = Flask(__name__)

SECRET_KEY = os.environ["SECRET_KEY"]
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
DEBUG = os.environ.get("DEBUG")
PORT = int(os.getenv("PORT", "5000"))


@app.route("/")
def index():
    return "Hello"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
