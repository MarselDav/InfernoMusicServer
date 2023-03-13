import bcrypt

from data import db_session
from data.users import Users
from content import text_content


def hashing(string):  # хэширование пароля
    return bcrypt.hashpw(string.encode(), bcrypt.gensalt()).decode()


def comparison(string, hash_string):  # сравнение пароля с захэшированым
    return bcrypt.checkpw(string.encode(), hash_string)


def check_password(email, password):  # сравнить пароль с паролем от этого аккаунта
    db_sess = db_session.create_session()
    hashed_password = db_sess.query(Users).filter(Users.email == email).first().hashed_password.encode()
    return comparison(password, hashed_password)


def password_strength_check(password, error_language) -> (bool, str):  # проверка надежности пароля
    if len(password) < 8 or len(password) >= 16:
        return False, text_content[error_language]["password_len"]
    if password.lower() == password:
        return False, text_content[error_language]["password_case"]
    return True, ""
