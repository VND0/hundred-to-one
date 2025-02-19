from flask import Flask, render_template

app = Flask(__name__)
app.config["SECRET_KEY"] = "1"


@app.get("/")
def index():
    return render_template("index.html")


@app.route("/auth")
def authorization():
    return render_template("auth.html")


if __name__ == '__main__':
    app.run(port=8000, host="0.0.0.0")
