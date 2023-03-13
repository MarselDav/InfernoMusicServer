import configparser
import os
import random
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, jsonify, request, render_template, make_response, redirect, json, send_file
from flask_login import LoginManager, login_user, logout_user, login_required
from pytube import YouTube
from youtubesearchpython import VideosSearch

from content import text_content
from data import db_session
from data.users import Users
from data.usersmusic import UsersMusic
from flask_forms import UploadVideoForm
from password_check import hashing, password_strength_check, check_password

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPER_PUPER_MEGA_SECRET_KEY'

login_manager = LoginManager()
login_manager.init_app(app)

download_path = "static/app/"
app_info_ini = "static/appinfo.ini"

youtube_url_watch = "https://www.youtube.com/watch?v="

sender_email = "marsel.corporation.usa@gmail.com"
email_password = "axhpncxcqhzngjhq"

code_len = 6

canGoToVerification = False
canSendAnother = False
start_time = None  # время в которое был отправлен код
verifyTimeDelay = 5

currentVerifyCode = None

currentUserInfo = None  # информации о текущем пользователе, который хочет зарегистрироваться


@login_manager.user_loader
def load_user(user_id):  # авторизироваться
    db_sess = db_session.create_session()
    return db_sess.query(Users).get(user_id)


@app.route("/logout")
@login_required
def logout():  # выйти из аккаунта
    logout_user()
    return redirect("/")


def get_code() -> str:
    code = ""
    for i in range(code_len):
        code += str(int(random.uniform(0, 10)))
    return code


def get_music_url(music_id):
    # print(YouTube(youtube_url_watch + music_id).streams.get_highest_resolution().url)
    return YouTube(youtube_url_watch + music_id).streams.get_audio_only().url
    # return YouTube(youtube_url_watch + music_id).streams.first().url


def send_message(name, receiver_email):
    global currentVerifyCode

    message = MIMEMultipart("alternative")
    message["Subject"] = "Verification Code"
    message["From"] = sender_email
    message["To"] = receiver_email

    code = get_code()
    currentVerifyCode = code

    text = f"""\
    InfernoMusic
    Hey {name}
    Please verify your InfernoMusic account.
    Enter this verification code:
    {code}"""
    html = f"""\
    <html>
      <body>
        <div style="font-family: arial; margin: 0 auto; border-radius: 10px;
        background-color: ghostwhite; width: 50%; box-shadow: 4px 4px 8px 4px rgba(34, 60, 80, 0.2);">
            <h1 align="center">InfernoMusic</h1>
            <h2 align="center" style="color: red;">Hey {name}</h2>
            <h3 align="center">Please verify your InfernoMusic account</h3>
            <p align="center">Enter this verification code:</p>
            <p style="text-align:center; background:#faf9fa;
            border:1px solid;border-style:solid;
            border-color:#dad8de;
            padding-bottom:5px;padding-left:5px;
            padding-right:5px;padding-top:5px">{code}</p>
        </div>
      </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, email_password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )


def check_in_db(email):
    db_sess = db_session.create_session()
    info = db_sess.query(Users).filter(Users.email == email).first()
    return info


def get_username(email):
    db_sess = db_session.create_session()
    username = db_sess.query(Users).filter(Users.email == email).first().name
    return username


def registration_new_account(name, email, password):
    user = Users()
    user.name = name
    user.email = email
    user.hashed_password = hashing(password)
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()

    user = db_sess.query(Users).filter(Users.email == email).first()
    login_user(user)


def check_email(email, error_language) -> (bool, str):
    if "@" in email and check_in_db(email) is None:
        return True, ""
    return False, text_content[error_language]["email_taken"]


@app.route("/registration/", defaults={"language": "Russian"}, methods=["GET", "POST"])
@app.route("/registration/<language>", methods=["GET", "POST"])
def registartion_form(language):
    global canGoToVerification, currentUserInfo
    errors = {"password_error": "",
              "password_confirm_error": "",
              "username_error": "",
              "email_error": "",
              }
    input_values = {"username": "",
                    "password": "",
                    "passwordConfirm": "",
                    "email": "",
                    }
    res = make_response(
        render_template("Registration.html",
                        title="Регистрация аккаунта",
                        content=text_content[language],
                        errors=errors,
                        input_values=input_values,
                        ))

    if request.method == "POST":
        input_values = {"username": request.form["username"],
                        "password": request.form["password"],
                        "passwordConfirm": request.form["passwordConfirm"],
                        "email": request.form["email"],
                        }

        if len(input_values["username"]) == 0:
            errors["username_error"] = text_content[language]["username_error"]

        if len(input_values["password"]) == 0:
            errors["password_error"] = text_content[language]["password_error"]

        if len(input_values["passwordConfirm"]) == 0:
            errors["password_confirm_error"] = text_content[language]["password_confirm_error_empty"]

        if input_values["password"] != input_values["passwordConfirm"]:
            errors["password_confirm_error"] = text_content[language]["password_confirm_error_wrong"]
            # делаем пустыми, потому что были введены неверно
            input_values["passwordConfirm"] = ""

        if not (password_strength_check(input_values["password"], language)[0]) and len(input_values["password"]) != 0:
            errors["password_error"] = password_strength_check(input_values["password"], language)[1]
            # делаем пустыми, потому что пароль не надежный и нужно ввести его заново
            input_values["password"] = ""
            input_values["passwordConfirm"] = ""

        if not (check_email(input_values["email"], language)[0]):
            errors["email_error"] = check_email(input_values["email"], language)[1]
            input_values["email"] = ""

        if "".join(errors.values()) == "":
            currentUserInfo = input_values
            canGoToVerification = True
            send_message(input_values["username"], input_values["email"])
            return redirect(f"/verification/{language}")

        res = make_response(
            render_template("Registration.html",
                            title="Регистрация аккаунта",
                            content=text_content[language],
                            errors=errors,
                            input_values=input_values,
                            ))
    return res


@app.route("/verification/<language>", methods=["GET", "POST"])
def verification(language):
    global canGoToVerification, currentUserInfo, currentVerifyCode
    error = ""
    if request.method == "POST":
        if currentVerifyCode == (
                request.form["1"] + request.form["2"] + request.form["3"] + request.form["4"] + request.form["5"] +
                request.form["6"]):
            registration_new_account(currentUserInfo["username"], currentUserInfo["email"], currentUserInfo["password"])
            return redirect("/")
        else:
            error = text_content[language]["verify_error"]
            canGoToVerification = True
    if canGoToVerification:
        canGoToVerification = False
        return make_response(
            render_template("Verification.html", email=currentUserInfo["email"], content=text_content[language],
                            error=error))


def authorizate_user(email, password):
    if check_password(email, password):
        username = get_username(email)

        # авторизовать пользователя и запомнить
        db_sess = db_session.create_session()
        user = db_sess.query(Users).filter(Users.email == email).first()
        login_user(user, remember=True)

        json_result = {"result": True, "username": username, "email": email}
    else:
        json_result = {"result": False, "username": " ", "email": " "}
    return json_result


@app.route("/login/", defaults={"language": "Russian"}, methods=["GET", "POST"])
@app.route("/login/<language>", methods=["GET", "POST"])
def logInPage(language):
    input_values = {"email": "",
                    "password": "",
                    }
    res = make_response(
        render_template("Login.html",
                        content=text_content[language],
                        input_values=input_values,
                        error=""))
    if request.method == "POST":
        input_values = {"email": request.form["email"],
                        "password": request.form["password"],
                        }
        result = authorizate_user(input_values["email"], input_values["password"])
        if not result["result"]:
            res = make_response(
                render_template("Login.html",
                                content=text_content[language],
                                input_values=input_values,
                                error=text_content[language]["login_error"]))
        else:
            return redirect("/")

    return res


@app.route("/upload/", defaults={"language": "Russian"}, methods=["GET", "POST"])
@app.route("/upload/<language>", methods=["GET", "POST"])
def uploadApp(language):
    form = UploadVideoForm()
    if form.validate_on_submit():
        form.file.data.save(download_path + "InfernoMusic.exe")

        app_config = configparser.ConfigParser()
        app_config.read(app_info_ini)
        app_config.set("INFO", "version", form.version.data)
        app_config.set("INFO", "description", form.description.data)

        with open(app_info_ini, 'w') as f:
            app_config.write(f)

        return redirect("/")

    return render_template("UploadVersion.html", form=form, content=text_content[language])


@app.route("/authorization", methods=["GET", "POST"])
def authorization():
    authorization_json = request.get_json()
    return json.dumps(authorizate_user(authorization_json["email"], authorization_json["password"]))


@app.route("/add_music", methods=["POST"])
def add_music():
    addmusicJson = request.get_json()
    usersmusic = UsersMusic()

    usersmusic.email = addmusicJson["email"]
    usersmusic.music_id = addmusicJson["id"]
    usersmusic.music_name = addmusicJson["name"]
    usersmusic.music_cover = addmusicJson["cover"]
    usersmusic.music_duration = addmusicJson["duration"]

    db_sess = db_session.create_session()
    db_sess.add(usersmusic)
    db_sess.commit()


@app.route("/delete_music", methods=["POST"])
def delete_music():
    deletemusicJson = request.get_json()

    db_sess = db_session.create_session()
    db_sess.query(UsersMusic).filter(UsersMusic.email == deletemusicJson["email"],
                                     UsersMusic.music_id == deletemusicJson["id"]).delete()
    db_sess.commit()


@app.route("/getMyMusic", methods=["POST", "GET"])
def getMyMusic():
    music_dict = {}
    if request.method == "POST":
        userInfo = request.get_json()
        db_sess = db_session.create_session()
        result = db_sess.query(UsersMusic).filter(UsersMusic.email == userInfo["email"]).all()
        for music in result:
            music_dict[music.music_id] = {"cover_url": music.music_cover + ".jpg",
                                          "music_name": music.music_name,
                                          "duration": music.music_duration, "url": "", "isLiked": True}
    return jsonify(music_dict)


@app.route("/search", methods=["GET", "POST"])
def searchmusic():
    searchJson = request.get_json()
    req = VideosSearch(searchJson["query"], limit=int(searchJson["limit"]))
    result = req.result()["result"]
    music_list = {}
    for music in result:
        duration = music["duration"]
        if duration is None:
            duration = "0:0"

        db_sess = db_session.create_session()
        if db_sess.query(UsersMusic).filter(UsersMusic.music_id == music["id"]).first() is None:
            isLiked = False
        else:
            isLiked = True

        music_list[music["id"]] = {"cover_url": music["thumbnails"][0]["url"] + ".jpg", "music_name": music["title"],
                                   "duration": duration, "url": "", "isLiked": isLiked}
        # video_list[video["id"]] = [video["thumbnails"][0]["url"] + ".jpg", video["title"], duration, "_"]

        # print(get_music_url(video["id"]))
    return jsonify(music_list)


@app.route("/getMusicUrl/<music_id>", methods=["GET", "POST"])
def getMusicUrl(music_id):
    music_url = get_music_url(music_id)
    print(music_url)
    video_list = {"url": music_url}
    return jsonify(video_list)


@app.route("/", methods=["GET", "POST"])
def mainpage():
    if request.method == "POST":
        if len(os.listdir(download_path)) != 0:
            return send_file(download_path + "InfernoMusic.exe", mimetype='exe')

    app_config = configparser.ConfigParser()
    app_config.read(app_info_ini)
    try:
        description = app_config.get("INFO", "description")
        version = app_config.get("INFO", "version")
    except configparser.NoOptionError:
        description = ""
        version = ""

    return make_response(
        render_template("MainPage.html", description=description, version=version))


def main():
    db_session.global_init("db/database.db")
    port = int(os.environ.get("PORT", 5000))
    # serve(app, host='0.0.0.0', port=port)
    app.run(host='0.0.0.0', port=port)
    # app.run(host="127.0.0.1", port=5000)

    # app.run(debug=True, port=os.getenv("PORT", default=5000))


if __name__ == '__main__':
    main()
