
import uuid

from flask import render_template , redirect , request , url_for  , session,flash, jsonify
from flask_login import current_user , logout_user , login_required , login_user

from app.models import RoleEnum , User
from app import app , flow
from form import LoginForm , RegisterForm
from dao import dao_authen , dao_user
from app.extensions import db

import google.oauth2.id_token
import google.auth.transport.requests
import requests

#Trang home
def index():
    return render_template('index.html')

# Navigate cho đăng nhập hoặc chưa
def index_controller():
    if current_user.is_authenticated:
        if current_user.role == RoleEnum.ADMIN:
            return redirect("/admin")
        return redirect("/home")
    return redirect('/login')

@app.route('/home')
@login_required
def home():
    return render_template('index.html')


def login():
    mse = ""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = dao_authen.get_user_by_username(username=username)
        if not user:
            mse = "Tài khoản không tồn tại trong hệ thống"
        else:
            if dao_authen.check_password_md5(user, password):
                login_user(user)
                return redirect(url_for('index_controller'))
            else:
                mse = "Mật khẩu không đúng"

    return render_template('login.html', form=form, mse=mse)

def logout_my_user():
    logout_user()
    return redirect('/login')

#Đăng nhập gg
def login_oauth():
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    session["state"] = state
    return redirect(authorization_url)

def oauth_callback():
    # đảm bảo Google trả về state đúng
    if request.args.get("state") != session.get("state"):
        return "State mismatch!", 400

    try:
        # lấy token từ Google
        flow.fetch_token(authorization_response=request.url)

        credentials = flow.credentials
        request_session = requests.session()
        token_request = google.auth.transport.requests.Request(session=request_session)

        # verify id_token
        id_info = google.oauth2.id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=flow.client_config["client_id"],
            clock_skew_in_seconds=10  # cho phép lệch tối đa 10 giây
        )

        email = id_info.get("email")
        name = id_info.get("name")

        # kiểm tra user trong DB
        user = dao_authen.get_user_by_username(email)
        if not user:
            user = User(
                username=email,
                email=email,
                password="",  # OAuth không dùng mật khẩu
                role=RoleEnum.USER,
                first_name=name.split(" ")[0] if name else "Google",
                last_name=" ".join(name.split(" ")[1:]) if name and len(name.split()) > 1 else "User",
                phone_number=f"GG-{uuid.uuid4().hex[:8]}",  #SĐT giả
                address="Unknown"
            )
            db.session.add(user)
            db.session.flush()
        login_user(user)

        return redirect(url_for("index_controller"))

    except Exception as e:
        app.logger.error(f"OAuth Callback Error: {e}")

        return f"Login failed: {e}", 400


def register():
    form = RegisterForm()
    mse = None

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        phone_number = form.phone_number.data
        address = form.address.data
        date_of_birth = form.date_of_birth.data
        gender = form.gender.data


        validation_errors = []

        # Kiểm tra username đã tồn tại
        if dao_authen.check_username_exists(username):
            validation_errors.append("Tên đăng nhập đã tồn tại!")

        # Kiểm tra email đã tồn tại
        if dao_authen.check_email_exists(email):
            validation_errors.append("Email đã tồn tại!")

        # Kiểm tra số điện thoại đã tồn tại
        if dao_authen.check_phone_exists(phone_number):
            validation_errors.append("Số điện thoại đã tồn tại!")

        # Nếu có lỗi validation, hiển thị tất cả lỗi
        if validation_errors:
            mse = " | ".join(validation_errors)
        else:
            # Tạo user bằng dao_user
            new_user = dao_user.create_user_with_role(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                address=address,
                date_of_birth=date_of_birth,
                gender=gender
            )

            if new_user:
                flash("Đăng ký thành công! Hãy đăng nhập.", "success")
                return redirect(url_for("login"))
            else:
                mse = "Có lỗi xảy ra khi tạo tài khoản. Vui lòng thử lại!"

    return render_template("register.html", form=form, mse=mse)