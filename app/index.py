from app import app , login
from flask_login import current_user
from app.dao import dao_authen
from app import controllers
from app.extensions import db
from app.controller import post_controller

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

app.add_url_rule("/", "index_controller", controllers.index_controller)
app.add_url_rule("/home",'home', controllers.home)
app.add_url_rule("/login",'login' ,controllers.login ,methods=['GET', 'POST'])
app.add_url_rule("/logout",'logout_my_user',controllers.logout_my_user , methods=['get'])
app.add_url_rule("/register", "register", controllers.register, methods=['GET', 'POST'])
app.add_url_rule("/oauth" , 'login_oauth', controllers.login_oauth)
app.add_url_rule("/callback" , 'oauth_callback', controllers.oauth_callback)
app.add_url_rule("/chatbot", "chatbot", controllers.chatbot)
app.add_url_rule("/profile", "profile", controllers.profile, methods=['GET', 'POST'])
app.add_url_rule("/about", "about", controllers.about)

#Social
app.add_url_rule("/posts", "post_list", post_controller.post_list)
app.add_url_rule("/posts/<int:post_id>", "post_detail", post_controller.post_detail)
app.add_url_rule("/posts/create", "create_post", post_controller.create_post, methods=["GET", "POST"])
app.add_url_rule("/posts/<int:post_id>/comment", "add_comment", post_controller.add_comment, methods=["POST"])
app.add_url_rule("/posts/<int:post_id>/like", "toggle_like", post_controller.toggle_like, methods=["POST", "GET"])

if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()   # Tạo tất cả bảng trong database
    app.run(host="localhost", port=5050, debug=True)