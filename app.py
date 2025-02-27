from random import randint
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_bootstrap import Bootstrap
from secrets import token_hex

app = Flask(__name__)
app.secret_key = token_hex()  # a random session secret key
app.config["WTF_CSRF_TIME_LIMIT"] = None
Bootstrap(app)  # to use bootstrap in html pages


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def data():
    data = [randint(1, 100) for _ in range(7)]
    data2 = [randint(1, 100) for _ in range(7)]
    labels = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    return jsonify({"data": data, "data2": data2, "labels": labels})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
