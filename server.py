from flask import Flask, render_template, request, jsonify, make_response
import os
from os import environ
import json
import PyPDF2
# from deep_translator import GoogleTranslator
# from fpdf import FPDF
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# import sqlite3
from sqlite3 import Error
import mysql.connector
from jinja2 import Environment, FileSystemLoader
from mysql.connector import Error

# con = sqlite3.connect("dossier.db")
# conn = None
does_testers_table_exist = False
does_users_table_exist = False

template_dir = os.path.abspath('templates/')
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder=template_dir)


# FLASK_APP=server.py flask run

'''

docker run -it --name doss_app_container\
-v $PWD:/dossier-translator \
-p 5000:5000 \
doss_app

'''


environment = Environment(loader=FileSystemLoader("templates/"))

# delete


# @app.route("/tester_homepage")
# def test_jinja():
#     return render_template("waiting_documents.html", tester=json.loads('{"majd": "rezik"}'))


class User:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age


def create_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            # password="root",
            # database="doss_app",
            port="3306",
            autocommit=True
        )
        return conn
    except Error as e:
        print("Error while connecting to MySQL", e)
        print(e)
    return conn


@app.route("/",  methods=['GET', 'POST'])
def login():
    # create_connection()
    return render_template('login_page.html')


@app.route("/auth0", methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        print("_POST_ is executed")

        username = request.form['username']
        password = request.form['password']

        table = "testers" if (
            (get_user_position(username)).__eq__('tester')
        ) else "users"
        print("table:" + table)
        if (are_credentials_valid(table, username, password)):
            if (table.__eq__("testers")):
                current_user = json.loads(
                    get_tester_by_name_as_json(username))
                # return render_template('waiting_documents.html', tester=json.loads(get_tester_by_name_as_json(username)))
                print("current user: ")
                print(current_user)
                print(type(current_user))

                return jsonify(
                    username=username,
                    email=current_user["email"],
                    age=current_user["age"],
                    password=password,
                    redirect_path="/tester_homepage"
                )

            else:  # user
                current_user = json.loads(
                    get_user_by_name_as_json(username))
                print("current user: ")
                print(current_user)
                print(type(current_user))

                print("Sent back to client...")
                print(current_user["email"])
                print(current_user["age"])

                return jsonify(
                    username=username,
                    email=current_user["email"],
                    age=current_user["age"],
                    password=password,
                    redirect_path="/user_homepage"
                )

                # return make_response(
                #     jsonify(
                #         data
                #     ), 200
                # )
            # return jsonify(redirect_path=redirect_path)
        else:
            print('#########!!!!!!!!!!!!!!!!!#########')
            print('wrong credentials, please check...')
            print('#########!!!!!!!!!!!!!!!!!#########')
            return jsonify(result="Check credentials", redirect_path="/", errors="wrong credentials, please try again...")
    else:
        print("oops, got here in GET return")
        return render_template('login_page.html')  # GET


def get_user_by_name_as_json(username):
    try:
        cursor = conn.cursor(dictionary=True)  # to return a dictionary
        user_query = "SELECT * FROM doss_sc.users where username=%s"
        result_user = cursor.execute(user_query, (username,))
        user = cursor.fetchone()
        if (user == None):
            print("no user with username: " + username + " exists in db")
        print(f"user as JSON: {json.dumps(user)} ")
        # conn.close()
        cursor.close()
        return json.dumps(user)
    except Exception as e:
        print("Error occurred: %s" % e)
      # converts return value to JSON


def get_tester_by_name_as_json(username):
    try:
        cursor = conn.cursor(dictionary=True)  # to return a dictionary
        tester_query = "SELECT * FROM doss_sc.testers where username=%s"
        result_user = cursor.execute(tester_query, (username,))
        tester = cursor.fetchone()
        if (tester == None):
            print("no tester with username: " + username)
        print(f"tester as JSON: {json.dumps(tester)} ")
        cursor.close()
        return json.dumps(tester)  # converts return value to JSON
    except Exception as e:
        print("Error occurred: %s" % e)


def get_user_position(username):
    try:
        print("called get_user_position for " + username)
        position = 'user'
        cursor = conn.cursor()
        sql_user = "SELECT * FROM doss_sc.users where username=%s"
        result_user = cursor.execute(sql_user, (username,))
        row = cursor.fetchone()
        if (row != None):
            print('position: user')
        else:
            sql_tester = "SELECT * FROM doss_sc.testers where username=%s"
            result_tester = cursor.execute(sql_tester, (username,))
            row = cursor.fetchone()
            if (row == None):
                position = None
            else:
                print('position: tester')
                position = 'tester'
        cursor.close()
        return position
    except Exception as e:
        print("Error occurred: %s" % e)


def are_credentials_valid(table, username, password):
    try:
        print("called are_credentials_valid")
        print(conn)
        cursor = conn.cursor()
        sql = "SELECT * FROM doss_sc." + table + " where username=%s and password=%s"
        print(sql)
        result = cursor.execute(sql, (username, password,))
        row = cursor.fetchone()
        cursor.close()
        return False if row == None else True
    except Exception as e:
        print("Error occurred: %s" % e)


@ app.route("/signup")
def signup():
    return render_template('signup.html')


@ app.route("/signupUser", methods=['GET', 'POST'])
def signup_user():
    return render_template('signup_user.html')


@ app.route("/attempt_signup_user", methods=['GET', 'POST'])
def attempt_signup_user_controller():
    print("##################")
    print("called attempt_signup_user_controller")
    if request.method == 'POST':
        print("post")
        req = request.get_json()
        print("GOT here to attempt_signup_user.server on route /attempt_signup_user")
        print('query : ', req)
        print(type(req))
        # reqToProcess = json.loads(req)
        print(req)
        # loading fields...
        print("loading fields...")
        username = req['username']
        email = req['email']
        age = req['age']
        password = req['password']
        print('username: ', username)
        print('email: ', email)
        print('age: ', age)
        print('password: ', password)

        # if no user in db has this username, register this user.
        if (check_user_already_exist(username, 'users') == False):
            register_user(username, email, age, password)
            return jsonify(
                username=username,
                email=email,
                age=age,
                password=password,
                redirect_path="/"
            )
        else:
            # error 403 - Already Exists
            return 'User Already Exists', 403
    print("Finished attempt_signup_user.SERVER")


def check_user_already_exist(username, table):
    try:
        cursor = conn.cursor(dictionary=True)  # to return a dictionary
        user_query = "SELECT * FROM doss_sc." + table + " where username=%s"
        print(user_query)
        result_user = cursor.execute(user_query, (username,))
        user = cursor.fetchone()
        if (user == None):
            print("no user with username: " + username + " exists in db")
            cursor.close()
            return False  # No user in db with this username = {username}
        cursor.close()
        return True  # There is already a user with username = {username}
    except Exception as e:
        print("Error occurred: %s" % e)
# files/users/majd@gmail.com


def register_user(username, email, age, password):
    try:
        cursor = conn.cursor(dictionary=True)  # to return a dictionary
        sql = "INSERT INTO doss_sc.users (username, email, age, password, files_path) VALUES (%s, %s, %s, %s, %s)"
        val = (username, email, age, password,
               create_directory_for_files("users", username, email))
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print("Error occurred: %s" % e)


def create_directory_for_files(user_type, username, email):
    return 'files/'+user_type+'/'+username


@app.route("/signupTester", methods=['GET', 'POST'])
def signup_tester():
    return render_template('signup_tester.html')


@ app.route("/attempt_signup_tester", methods=['GET', 'POST'])
def attempt_signup_tester_controller():
    print("##################")
    print("called attempt_signup_tester_controller")
    if request.method == 'POST':
        print("post")
        req = request.get_json()
        print("GOT here to attempt_signup_tester_controller.server on route /attempt_signup_tester")
        print('query : ', req)
        print(type(req))
        # reqToProcess = json.loads(req)
        print(req)
        # loading fields...

        print("loading fields...")
        username = req['username']
        email = req['email']
        age = req['age']
        password = req['password']
        languages = req['languages']

        print('username: ', username)
        print('email: ', email)
        print('age: ', age)
        print('password: ', password)
        print('languages: ', languages)

        # if no user in db has this username, register this user.
        if (check_user_already_exist(username, "testers") == False):
            register_tester(username, email, age, password, languages)
            return jsonify(
                redirect_path="/"
            )
        else:
            # error 403 - Already Exists
            return 'User Already Exists', 403
    print("Finished attempt_signup_user.SERVER")


def register_tester(username, email, age, password, languages):
    try:
        cursor = conn.cursor(dictionary=True)  # to return a dictionary
        sql = "INSERT INTO doss_sc.testers (username, email, age, password, files_path , languages) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (username, email, age, password,
               create_directory_for_files("users", username, email), languages)
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        return True

    except Exception as e:
        print("Error occurred: %s" % e)


def create_users_table_if_doesnt_exist():
    print("checking users table...")
    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                            id integer PRIMARY KEY NOT NULL AUTO_INCREMENT,
                                            name text NOT NULL,
                                            email text,
                                            age integer,
                                            password text,
                                            type text,
                                            files_path text
                                        ); """
    if does_users_table_exist is False:
        if conn is not None:
            # create projects table
            print("creating users table...")
            create_table(conn, sql_create_users_table)
            does_users_table_exist = True
        else:
            print("Error! cannot create the database connection.")
    return does_users_table_exist


@ app.route("/user_homepage",  methods=['GET', 'POST'])
def user_homepage_controller():
    return render_template('upload_file.html')


@ app.route("/tester_homepage")
def tester_homepage():
    return render_template('waiting_documents.html')


@ app.route("/archivepage")
def archivepage():
    return render_template('Archive.html')


@ app.route("/exportpage")
def exportpage():
    return render_template('Export_page.html')


@ app.route("/testerchecktranslation")
def checkingpage():
    return render_template('tester_check_translation.html')


@ app.route('/test', methods=['GET'])
def test():
    langs_dict = GoogleTranslator.get_supported_languages('self')
    return 'hi'


@ app.route("/send_translation_to_tester")
def send_to_tester():
    return render_template('tester_check_translation.html')


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     firstname = db.Column(db.String(100), nullable=False)
#     lastname = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(80), unique=True, nullable=False)
#     age = db.Column(db.Integer)
#     created_at = db.Column(db.DateTime(timezone=True),
#                            server_default=func.now())

#     def __repr__(self):
#         return f'<Student {self.firstname}>'


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


@ app.route("/translate_file")
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


def main():
    print("###########################")
    print("###########################")
    print('start main')
    print("###########################")
    print("###########################")
    port = int(os.environ.get('PORT', 8080))
    # main()
    global conn
    print('creating connection')
    conn = create_connection()
    print('connection established')
    app.run(debug=True, host='0.0.0.0', port=port)
    # conn.close()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')


main()
# conn.close()
