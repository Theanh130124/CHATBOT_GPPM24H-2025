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


def update_user_profile(user_id, first_name, last_name, email, phone_number, 
                       address, date_of_birth=None, gender=None, avatar_url=None):
    """Cập nhật thông tin hồ sơ của user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "Người dùng không tồn tại"
        
        # Kiểm tra email trùng (ngoại trừ email hiện tại)
        if email != user.email and dao_authen.check_email_exists(email):
            return False, "Email đã được sử dụng"
        
        # Kiểm tra phone trùng (ngoại trừ phone hiện tại)
        if phone_number != user.phone_number and dao_authen.check_phone_exists(phone_number):
            return False, "Số điện thoại đã được sử dụng"
        
        # Cập nhật thông tin
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone_number
        user.address = address
        user.date_of_birth = date_of_birth
        if gender:
            user.gender = gender
        if avatar_url:
            user.avatar = avatar_url
        user.updated_at = datetime.now()
        
        db.session.commit()
        return True, "Cập nhật thông tin thành công"
    
    except Exception as ex:
        db.session.rollback()
        print(f"Lỗi cập nhật user: {ex}")
        return False, "Có lỗi xảy ra khi cập nhật"


def change_password(user_id, old_password, new_password):
    """Đổi mật khẩu user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return False, "Người dùng không tồn tại"
        
        # Kiểm tra mật khẩu cũ
        if not dao_authen.check_password_md5(user, old_password):
            return False, "Mật khẩu hiện tại không đúng"
        
        # Cập nhật mật khẩu mới
        hashed_password = hashlib.md5(new_password.strip().encode('utf-8')).hexdigest()
        user.password = hashed_password
        user.updated_at = datetime.now()
        
        db.session.commit()
        return True, "Đổi mật khẩu thành công"
    
    except Exception as ex:
        db.session.rollback()
        print(f"Lỗi đổi mật khẩu: {ex}")
        return False, "Có lỗi xảy ra khi đổi mật khẩu"