from app import app , login
from flask_login import current_user
from app.dao import dao_authen
from app import controllers
from app.extensions import db



# Hàm này luôn truyền các info vào -> .html nao cung co
@app.context_processor
def common_attr():
    if current_user.is_authenticated:
        user = dao_authen.get_info_by_id(current_user.user_id)
        return {
            'user': user,
        }
    return {}

#Chi Flask lay user
@login.user_loader
def user_load(user_id):
    return dao_authen.get_info_by_id(user_id)




if __name__ == '__main__':


    with app.app_context():
        db.create_all()   # Tạo tất cả bảng trong database

    app.run(host="localhost", port=5000, debug=True)