from app.extensions import db
from app.models import Post, Comment, Like, Follow
from datetime import datetime

#Post
def create_post(user_id, title, content, image_url=None):
    post = Post(
        user_id=user_id,
        title=title,
        content=content,
        image_url=image_url,
        created_at=datetime.now()
    )
    db.session.add(post)
    db.session.commit()
    return post


def get_all_posts():
    return Post.query.order_by(Post.created_at.desc()).all()


def get_post_by_id(post_id):
    return Post.query.get(post_id)


def delete_post(post_id, user_id):
    post = Post.query.filter_by(post_id=post_id, user_id=user_id).first()
    if post:
        db.session.delete(post)
        db.session.commit()
        return True
    return False

#Comment
def add_comment(post_id, user_id, content):
    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=content,
        created_at=datetime.now()
    )
    db.session.add(comment)
    db.session.commit()
    return comment


def get_comments_by_post(post_id):
    return Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()


#Like
def toggle_like(post_id, user_id):
    like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
    if like:
        db.session.delete(like)  # Bỏ like nếu đã like
        db.session.commit()
        return False
    else:
        like = Like(post_id=post_id, user_id=user_id, created_at=datetime.now())
        db.session.add(like)
        db.session.commit()
        return True


def count_likes(post_id):
    return Like.query.filter_by(post_id=post_id).count()


def user_liked_post(post_id, user_id):
    return Like.query.filter_by(post_id=post_id, user_id=user_id).first() is not None
