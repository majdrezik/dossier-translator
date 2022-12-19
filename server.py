from flask import Flask, render_template, request, jsonify, redirect, g
import os
from os import environ
from flask_sqlalchemy import SQLAlchemy
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import fitz
from deep_translator import GoogleTranslator
from fpdf import FPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

template_dir = os.path.abspath('templates/')
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder=template_dir)
# app.config['DB_USERNAME'] = environ.get('DB_USERNAME')
# app.config['DB_PASSWORD'] = environ.get('DB_PASSWORD')
os.environ['DB_USERNAME'] = "majd"
os.environ['DB_PASSWORD'] = "majd"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = "mongodb://" + os.getenv('DB_USERNAME') + ":" + os.getenv(
    'DB_USERNAME') + "@ac-sq9li2w-shard-00-00.xexprlu.mongodb.net:27017,ac-sq9li2w-shard-00-01.xexprlu.mongodb.net: 27017,ac-sq9li2w-shard-00-02.xexprlu.mongodb.net:27017/?ssl=true&replicaSet=atlas-9z9y2w-shard-0&authSource=admin&retryWrites=true&w=majority"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# FLASK_APP=server.py flask run


# Use LocalProxy to read the global db instance with just `db`
# def get_db():
#     """
#     Configuration method to return db instance
#     """
#     db = getattr(g, "_database", None)
#     if db is None:
#         db = g._database = PyMongo(current_app).db
#     return db
# db = LocalProxy(get_db)


@app.route("/")
def login():
    return render_template('login_page.html')


@app.route("/login", methods=['POST'])
def auth():
    req = request.get_json()
    # This is the query that was stored in the JSON within the browser
    print('query : ', req)
    print(type(req))
    print('------------------------')
    # this converts the json query to a python dictionary
    reqToProcess = json.loads(req)
    print(reqToProcess)
    print('username: ', reqToProcess['username'])
    print('password: ', reqToProcess['password'])
    resp = jsonify(success=True)
    return resp


@app.route("/signup")
def signup():
    return render_template('signup.html')


@app.route("/signupUser")
def signup_user():
    return render_template('signup_user.html')


@app.route("/signupTester")
def signup_tester():
    return render_template('signup_tester.html')


@app.route("/user_homepage")
def user_homepage():
    return render_template('upload_file.html')


@app.route("/tester_homepage")
def tester_homepage():
    return "hello tester"


@app.route("/archivepage")
def archivepage():
    return render_template('Archive.html')


@app.route("/exportpage")
def exportpage():
    return render_template('Export_page.html')


@app.route('/test', methods=['GET'])
def test():
    langs_dict = GoogleTranslator.get_supported_languages('self')
    return 'hi'


@app.route("/send_translation_to_tester")
def send_to_tester():
    return render_template('tester_check_translation.html')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    def __repr__(self):
        return f'<Student {self.firstname}>'


# def read_file(input_file):
def read_file():
    with fitz.open("test/test.pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    input_file = text
    return input_file
    # print(input_file)


def send_to_translation(input_file, language_from, language_to):
    source_language = 'auto' if language_from == '' else language_from
    # translator.detect
    translate = GoogleTranslator(
        source=source_language, target=language_to).translate

    return translate(input_file)


def write_translation_to_txt_file(input_file, path):
    with open(path, 'w') as f:
        f.write(input_file.replace('. ', '.\n'))


# def write_translation_to_pdf(output):
#     my_canvas = canvas.Canvas("test/output.pdf", pagesize=letter)
#     my_canvas.setLineWidth(3)
#     my_canvas.setFont('Helvetica', 12)
#     # for x in output:
#     #     my_canvas.drawString(30, 750, x)
#     my_canvas.drawText(output)
#     my_canvas.save()
    # pdf = FPDF()
    # # Add a page
    # pdf.add_page()
    # pdf.set_font("Arial", size=15)

    # # open the text file in read mode
    # f = open("test/output.txt", "r")  # , encoding="utf-8")
    # for x in f:
    #     pdf.cell(200, 10, txt=x, ln=1, align='C')
    # pdf.output("test/output.pdf")


@app.route("/translate_file")
def translate_file():
    # read_file(input_file)
    input_file = read_file()
    print(input_file)
    write_translation_to_txt_file(input_file, 'test/original.txt')
    print("############################")
    print("translating...")
    print("############################")
    translation = send_to_translation(input_file, 'english', 'italian')
    print("############################")
    print("translation done...")
    print("############################")
    print(translation)
    write_translation_to_txt_file(translation, 'test/translated.txt')
    # write_translation_to_pdf(output)
    send_to_tester()
    return 'ok'


if __name__ == "__main__":
    app.run()
