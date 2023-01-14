from flask import Flask, render_template, request, jsonify, make_response
import os
from os import environ
import json
import PyPDF2
from deep_translator import GoogleTranslator
# from fpdf import FPDF
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# import sqlite3
from sqlite3 import Error
import mysql.connector
from jinja2 import Environment, FileSystemLoader
from mysql.connector import Error
# splitting, merging, cropping, and transforming PDF files
from PyPDF2 import PdfReader
import re
import random
import string
import smtplib
from fileinput import filename
from werkzeug.utils import secure_filename

# con = sqlite3.connect("dossier.db")
conn = None
does_testers_table_exist = False
does_users_table_exist = False

template_dir = os.path.abspath('templates/')
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder=template_dir)
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = "doss_secret"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


# FLASK_APP=server.py flask run

'''

docker run -it --name doss_app_container\
-v $PWD:/dossier-translator \
-p 5000:5000 \
doss_app

'''


environment = Environment(loader=FileSystemLoader("templates/"))
current_logged_user = ["", ""]  # ["username", "table : users/testers"]
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
        global conn
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            # password="root",
            # database="doss_app",
            port="3306",
            autocommit=True,
            buffered=True
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
        global current_logged_user
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

                current_logged_user = [username, "testers"]
                print(f"current_logged_user: {current_logged_user}")
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

                current_logged_user = [username, "users"]
                print(f"current_logged_user: {current_logged_user}")
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
        # global conn
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
        # global conn
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
        # global conn
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
        # global conn
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
                redirect_path="/"
            )
        else:
            # error 403 - Already Exists
            return 'User Already Exists', 403
    print("Finished attempt_signup_user.SERVER")


def check_user_already_exist(username, table):
    try:
        # global conn
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
        # global conn
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
        # global conn
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


# def create_users_table_if_doesnt_exist():
#     print("checking users table...")
#     sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
#                                             id integer PRIMARY KEY NOT NULL AUTO_INCREMENT,
#                                             name text NOT NULL,
#                                             email text,
#                                             age integer,
#                                             password text,
#                                             type text,
#                                             files_path text
#                                         ); """
#     if does_users_table_exist is False:
#         if conn is not None:
#             # create projects table
#             print("creating users table...")
#             create_table(conn, sql_create_users_table)
#             does_users_table_exist = True
#         else:
#             print("Error! cannot create the database connection.")
#     return does_users_table_exist


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
    return render_template('tester_check.html')

################################################################################################
################################################################################################


@app.route('/uploader', methods=['GET', 'POST'])
def get_file_from_user_and_send_to_tester():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            resp = jsonify({'message': 'No file in the request'})
            resp.status_code = 400
            return resp
        files = request.files.getlist('files[]')

        language_from = request.form['language_from']
        language_to = request.form['language_to']
        print("language_from: " + language_from)
        print("language_to: " + language_to)
        errors = {}
        success = False

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'

        if success and errors:
            errors['message'] = 'File(s) successfully uploaded'
            resp = jsonify(errors)
            resp.status_code = 206
            return resp
        if success:
            resp = jsonify({'message': 'Files successfully uploaded'})
            resp.status_code = 201
            print('file uploaded successfully')
            file_path = app.config['UPLOAD_FOLDER'] + '/' + filename
            translate_file(file_path, language_from,
                           language_to)
            return resp
        else:
            resp = jsonify(errors)
            resp.status_code = 400
            return resp


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

################################################################################################
################################################################################################


@ app.route('/load_tester_homepage', methods=['GET'])
def load_tester_homepage_controller():
    if request.method == 'GET':
        try:
            cursor = conn.cursor(dictionary=True)  # to return a dictionary
            sql = "SELECT * FROM doss_sc.testers where username=%s"
            print(sql)
            username = current_logged_user[0]
            cursor.execute(sql, (username,))
            tester = cursor.fetchone()
            waiting_files = tester.get('num_files_waiting'),
            files_path = tester.get('files')
            cursor.close()
            return jsonify(
                username=username,
                waiting_files=waiting_files,
                files_path=files_path
            )
        except Exception as e:
            print("Error occurred: %s" % e)


@app.route('/')
def upload_form():
    return render_template('index.html')


@ app.route('/test', methods=['GET'])
def test():
    langs_dict = GoogleTranslator.get_supported_languages('self')
    return 'hi'


@ app.route("/send_translation_to_tester", methods=['GET', 'POST'])
def send_to_tester(input_file_path, translation_path, language_from, language_to):

    can_tester_help, tester_username = assign_file_to_tester(
        language_from, language_to)

    if (can_tester_help == False):
        return "No tester can assest with your testing now..."

    tester_files_updated = tester_get_current_files(
        language_from, tester_username, input_file_path)

    tester_update_files(tester_username, tester_files_updated)


def tester_get_current_files(language_from, tester_username, input_file_path):
    try:
        cursor = conn.cursor(dictionary=True)  # to return a dictionary
        query = "SELECT * FROM doss_sc.testers where username=%s"
        print(query)
        cursor.execute(query, (tester_username,))
        tester = cursor.fetchone()
        print(tester)
        tester_name = tester.get('username')
        tester_files = tester.get('files')

        print("tester_name: " + tester_name)
        print("tester_files: " + tester_files)

        if tester_files is None or tester_files == "":
            tester_files_updated = input_file_path
        else:
            tester_files_updated = tester_files + ',' + input_file_path
        cursor.close()
        print(f"successfully fetched files of tester {tester_name}")
        return tester_files_updated
    except Exception as e:
        print("Error occurred in tester_get_current_files: %s" % e)


def tester_update_files(tester_name, tester_files_updated):
    try:
        cursor = conn.cursor(dictionary=True)
        query = f'''
            UPDATE doss_sc.testers SET files = '{tester_files_updated}' WHERE username = '{tester_name}'
            '''
        print(query)
        cursor.execute(query)
        print(f"successfully updated files for tester {tester_name}")
        conn.commit()
        cursor.close()
    except Exception as e:
        print("Error occurred in tester_update_files: %s" % e)


def assign_file_to_tester(language_from, language_to):
    try:
        # global conn
        cursor = conn.cursor(dictionary=True)  # to return a dictionary
        soreted_languages = [language_from, language_to]
        soreted_languages.sort()
        for language in soreted_languages:
            print(language)

        query = f"""SELECT username, num_files_waiting FROM ( /* selecting username */
            SELECT username, num_files_waiting, languages AS languages2 /* selecting num_files_waiting */
            FROM doss_sc.testers /* FROM doss_sc.testers */
            ) /* end */
            AS testers /*AS testers*/
            WHERE languages2 LIKE '%{soreted_languages[0]}%{soreted_languages[1]}%' /*compare languages*/
            ORDER BY num_files_waiting ASC /*ASC*/
        """

        print("assigning file to tester...")
        print(query)
        result_user = cursor.execute(query)
        tester = cursor.fetchone()
        if (tester == None):
            print("No tester can assest with your testing now...")
            cursor.close()
            return False  # No user in db with this username = {username}
        print("tester : ")
        print(tester)
        print("tester username : ")
        print(tester.get('username'))
        # cursor.close()
        tester_username = tester.get('username')
        files_waitin = tester.get('num_files_waiting')
        print("waiting documents before update: ")
        print(files_waitin)
        print("closing cursor in assign_file_to_tester")
        cursor.close()
        print("closed cursor in assign_file_to_tester")
        update_tester_count_for_waiting_documents(
            tester_username, files_waitin)
        return True, tester_username
    except Exception as e:
        print("Error occurred in assign_file_to_tester: %s" % e)


def update_tester_count_for_waiting_documents(username, files_waitin):
    try:
        print("update_tester_count_for_waiting_documents")
        # global conn
        cursor = conn.cursor(dictionary=True)
        print(conn)
        print(cursor)
        print(username)
        print("called update_tester_count_for_waiting_documents")

        addition = 1  # "num_files_waiting + 1"
        addition_in_query = f'{addition:+}'
        # query = "UPDATE doss_sc.testers SET num_files_waiting = num_files_waiting + 1 WHERE username ='" + username + "'"

        query = f'''
        UPDATE doss_sc.testers SET num_files_waiting = num_files_waiting {addition_in_query} WHERE username = '{username}'
        '''
        # query = f'''
        # UPDATE doss_sc.testers SET num_files_waiting = num_files_waiting {addition_in_query} WHERE username = '{username}'
        # '''

        print("query to update_tester_count_for_waiting_documents")
        print(query)
        cursor.execute(query)
        conn.commit()
        print(f"successfully updated count for tester {username}")
        print("waiting documents after update: " + str(files_waitin + 1))
        cursor.close()
    except Exception as e:
        print("Error occurred in update_tester_count_for_waiting_documents: %s" % e)


def return_input_files_path(username, table):
    new_dir = "./files/input_files/" + table + "/" + username
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    letters = string.ascii_letters
    rabdom_id = ''.join(random.choice(letters) for i in range(10))
    return new_dir + "/" + username + "_" + rabdom_id + ".txt"


def return_translated_files_path(username, table):
    new_dir = "./files/translated_files/" + table + "/" + username
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    letters = string.ascii_letters
    rabdom_id = ''.join(random.choice(letters) for i in range(10))
    return new_dir + "/" + username + "_" + rabdom_id + ".txt"


def read_input_pdf_convert_to_text(input_file):
    global current_logged_user
    reader = PdfReader(input_file)
    number_of_pages = len(reader.pages)
    page = reader.pages[0]
    text = page.extract_text()
    print(text)
    # files/users/tester3
    input_file_path = return_input_files_path(
        current_logged_user[0], current_logged_user[1]
    )

    with open(input_file_path, 'a+') as f:
        for page in reader.pages:   # write the whole text (all pages)
            # write each item on a new line
            f.write("%s\n\n" % page.extract_text())

    return input_file_path, reader   # return the files location and the reader


def send_to_translation(reader, language_from, language_to):
    # source_language = 'auto' if language_from == '' else language_from
    # translator.detect
    number_of_pages = len(reader.pages)

    translate = GoogleTranslator(
        source=language_from, target=language_to).translate

    translation = []
    print(f"number_of_pages in reader: {number_of_pages}")

    for page in reader.pages:
        translation.append(
            translate(
                page.extract_text()
            )
        )

    return translation


def write_array_of_translations_to_txt_file(translation, path):
    with open(path, 'a+') as f:
        for page in translation:
            f.write(page.replace('. ', '.\n'))


@ app.route("/translate_file", methods=['GET', 'POST'])
def translate_file(file, language_from, language_to):

    # def translate_file():
    # input_file_path, reader = read_input_pdf_convert_to_text(file)
    global current_logged_user
    input_file_path, reader = read_input_pdf_convert_to_text(file)

    print("file path: " + input_file_path)
    print("############################")
    print("sending to translation...")
    print("############################")

    # return array of pages translated
    # translation = send_to_translation(reader, 'english', 'hebrew')
    translation = send_to_translation(
        reader, language_from.lower(), language_to.lower())     # THE RIGHT ONE

    print("############################")
    print("translation done...")
    print("############################")
    print(translation)
    # current_logged_user = ["", ""]  # ["username", "table : users/testers"]
    translation_path = return_translated_files_path(
        current_logged_user[0], current_logged_user[1])
    write_array_of_translations_to_txt_file(
        translation, translation_path)
    # write_translation_to_pdf(output)
    # send_to_tester(input_file_path, translation_path,
    #                language_from, language_to)
    send_to_tester(input_file_path, translation_path,
                   language_from, language_to)
    return 'ok'


@ app.route("/send_email", methods=['GET', 'POST'])
def send_email_controller(receiver_email, message):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "dossier.translator@gmail.com"  # new gmail
    # receiver_email = "your@gmail.com"  # Enter receiver address
    password = "anrwqajkaglfllpl"
    forgot_password_message = """\
    Subject: Restore your password

    This message is sent from Python."""

    notify_on_done_message = """\
    Subject: Your file is done

    Your file is now ready and can be easily fetched via the app on Archive page."""

    message_to_send = forgot_password_message if message == 0 else notify_on_done_message

    # sender = 'from@example.com'
    # receivers = [receiver_email]

    # message = """From: From Person <from@example.com>
    # To: To Person <to@example.com>
    # Subject: SMTP email example

    # This is a test message.
    # """
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    # smtpObj = smtplib.SMTP("localhost")
    # start TLS for security
    smtpObj.starttls()
    # Authentication
    smtpObj.login(sender_email, password)
    # sending the mail
    smtpObj.sendmail(sender_email, receiver_email, message_to_send)
    # terminating the session
    smtpObj.quit()

    print("Successfully sent email to: " + receiver_email)


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
