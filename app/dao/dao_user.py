import hashlib
from app.models import User, RoleEnum
from app.extensions import db
from datetime import datetime
from app.dao import dao_authen



def create_user_with_role(username, email, password, first_name, last_name,
                          phone_number, address, date_of_birth=None,
                          gender=None, role=RoleEnum.USER):

    # Kiểm tra trùng
    if dao_authen.check_username_exists(username) or dao_authen.check_email_exists(email) or dao_authen.check_phone_exists(phone_number):
        return None

    hashed_password = hashlib.md5(password.strip().encode("utf-8")).hexdigest()

    user = User(
        username=username,
        email=email,
        password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        address=address,
        date_of_birth=date_of_birth,
        gender=gender,
        role=role,
        is_active=True
    )

    try:
        db.session.add(user)
        db.session.flush()  # để có user_id
        db.session.commit()
        return user

    except Exception as ex:
        db.session.rollback()
        print(f"Lỗi tạo user: {ex}")
        return None