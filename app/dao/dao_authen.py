import hashlib
from app.models import User, RoleEnum
from flask_login import current_user


def get_info_by_id(id):
    return User.query.get(id)


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()
    return user if user and user.is_active else None

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


# Phần cho validate
def check_username_exists(username):
    return User.query.filter_by(username=username).first() is not None


def check_password_md5(user, password):
    if user and user.password:  # Đảm bảo user tồn tại và có trường password
        hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()
        return hashed_password == user.password
    return False

def check_email_exists(email):
    return User.query.filter_by(email=email).first() is not None

def check_phone_exists(phone_number):
    return User.query.filter_by(phone_number=phone_number).first() is not None