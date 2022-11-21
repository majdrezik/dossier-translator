from flask import Flask, render_template
import os


template_dir = os.path.abspath('templates/')
app = Flask(__name__, template_folder=template_dir)

# FLASK_APP=login.py flask run


@app.route("/")
def hello_world():
    return "hello world!"


@app.route("/login")
def login():
    return render_template('login_page.html')


if __name__ == "__main__":
    app.run()
