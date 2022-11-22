from flask import Flask, render_template
import os


template_dir = os.path.abspath('templates/')
app = Flask(__name__, template_folder=template_dir)

# FLASK_APP=server.py flask run


@app.route("/")
def hello_world():
    return "hello world!"


@app.route("/login")
def login():
    return render_template('login_page.html')


@app.route("/signup")
def signup():
    return render_template('signup.html')


@app.route("/signupUser")
def signup_user():
    return render_template('signup_user.html')


@app.route("/signupTester")
def signup_tester():
    return render_template('signup_tester.html')


if __name__ == "__main__":
    app.run()
