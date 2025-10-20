from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.dao import dao_post
import cloudinary.uploader
from flask import current_app

# Danh sách bài viết
@login_required
def post_list():
    posts = dao_post.get_all_posts()
    return render_template("post_list.html", posts=posts)

# Chi tiết bài viết
@login_required
def post_detail(post_id):
    post = dao_post.get_post_by_id(post_id)
    comments = dao_post.get_comments_by_post(post_id)
    like_count = dao_post.count_likes(post_id)
    user_liked = dao_post.user_liked_post(post_id, current_user.user_id)
    return render_template(
        "post_detail.html",
        post=post,
        comments=comments,
        like_count=like_count,
        user_liked=user_liked
    )

# Tạo bài viết
@login_required
def create_post():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        image_file = request.files.get("image")

        image_url = None
        if image_file and image_file.filename != "":
            try:
                upload_result = cloudinary.uploader.upload(
                    image_file,
                    folder="posts/",  # Thư mục trên Cloudinary
                    public_id=None,   # để Cloudinary tự tạo ID duy nhất
                    overwrite=True,
                    resource_type="image"
                )
                image_url = upload_result.get("secure_url")
            except Exception as e:
                flash(f"Lỗi khi upload ảnh: {e}", "danger")

        dao_post.create_post(current_user.user_id, title, content, image_url)
        flash("Đăng bài thành công!", "success")
        return redirect(url_for("post_list"))

    return render_template("create_post.html")

# Thêm bình luận
@login_required
def add_comment(post_id):
    if request.method == "POST":
        content = request.form.get("content")
        dao_post.add_comment(post_id, current_user.user_id, content)
        flash("Bình luận đã được gửi!", "info")
    return redirect(url_for("post_detail", post_id=post_id))

# Like / Unlike bài viết
@login_required
def toggle_like(post_id):
    liked = dao_post.toggle_like(post_id, current_user.user_id)
    msg = "Đã thích bài viết!" if liked else "Bỏ thích bài viết!"
    flash(msg, "success")
    return redirect(url_for("post_detail", post_id=post_id))
