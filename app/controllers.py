import uuid

from flask import render_template, redirect, request, url_for, session, flash, jsonify
from flask_login import current_user, logout_user, login_required, login_user

from app.models import RoleEnum, User, ChatConversation, ChatMessage
from app import app, flow
from app.form import LoginForm, RegisterForm, ProfileForm, ChangePasswordForm
from app.dao import dao_authen, dao_user
from app.extensions import db

import google.oauth2.id_token
import google.auth.transport.requests
import requests


# ============ HOME & NAVIGATION ============

def index():
    return render_template('index.html')


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


# ============ AUTHENTICATION ============

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


def login_oauth():
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    session["state"] = state
    return redirect(authorization_url)


def oauth_callback():
    if request.args.get("state") != session.get("state"):
        return "State mismatch!", 400

    try:
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        request_session = requests.session()
        token_request = google.auth.transport.requests.Request(session=request_session)

        id_info = google.oauth2.id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=flow.client_config["client_id"],
            clock_skew_in_seconds=10
        )

        email = id_info.get("email")
        name = id_info.get("name")

        user = dao_authen.get_user_by_username(email)
        if not user:
            user = User(
                username=email,
                email=email,
                password="",
                role=RoleEnum.USER,
                first_name=name.split(" ")[0] if name else "Google",
                last_name=" ".join(name.split(" ")[1:]) if name and len(name.split()) > 1 else "User",
                phone_number=f"GG-{uuid.uuid4().hex[:8]}",
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

        if dao_authen.check_username_exists(username):
            validation_errors.append("Tên đăng nhập đã tồn tại!")

        if dao_authen.check_email_exists(email):
            validation_errors.append("Email đã tồn tại!")

        if dao_authen.check_phone_exists(phone_number):
            validation_errors.append("Số điện thoại đã tồn tại!")

        if validation_errors:
            mse = " | ".join(validation_errors)
        else:
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


# ============ CHATBOT ============

@app.route('/chatbot')
@login_required
def chatbot():
    return render_template("chatbot.html")


@app.route('/api/chat/conversations', methods=['GET'])
@login_required
def get_conversations():
    """Get all conversations for the current user"""
    conversations = ChatConversation.query.filter_by(
        user_id=current_user.user_id
    ).order_by(ChatConversation.updated_at.desc()).all()

    return jsonify([{
        'id': conv.conversation_id,
        'title': conv.title,
        'createdAt': conv.created_at.strftime('%d/%m/%Y %H:%M:%S'),
        'updatedAt': conv.updated_at.strftime('%d/%m/%Y %H:%M:%S')
    } for conv in conversations])


@app.route('/api/chat/conversations', methods=['POST'])
@login_required
def create_conversation():
    """Create a new conversation for the current user"""
    data = request.get_json()
    conversation = ChatConversation(
        user_id=current_user.user_id,
        title=data.get('title', 'Cuộc trò chuyện mới')
    )
    db.session.add(conversation)
    db.session.commit()

    return jsonify({
        'id': conversation.conversation_id,
        'title': conversation.title,
        'createdAt': conversation.created_at.strftime('%d/%m/%Y %H:%M:%S'),
        'updatedAt': conversation.updated_at.strftime('%d/%m/%Y %H:%M:%S')
    }), 201


@app.route('/api/chat/conversations/<int:conversation_id>/messages', methods=['GET'])
@login_required
def get_messages(conversation_id):
    """Get all messages in a conversation (only if user owns it)"""
    conversation = ChatConversation.query.filter_by(
        conversation_id=conversation_id,
        user_id=current_user.user_id
    ).first()

    if not conversation:
        return jsonify({'error': 'Conversation not found or access denied'}), 404

    messages = ChatMessage.query.filter_by(
        conversation_id=conversation_id
    ).order_by(ChatMessage.timestamp.asc()).all()

    return jsonify([{
        'id': msg.message_id,
        'content': msg.content,
        'type': msg.message_type,
        'timestamp': msg.timestamp.strftime('%d/%m/%Y %H:%M:%S')
    } for msg in messages])


@app.route('/api/chat/conversations/<int:conversation_id>/messages', methods=['POST'])
@login_required
def add_message(conversation_id):
    """Add a message to a conversation (only if user owns it)"""
    conversation = ChatConversation.query.filter_by(
        conversation_id=conversation_id,
        user_id=current_user.user_id
    ).first()

    if not conversation:
        return jsonify({'error': 'Conversation not found or access denied'}), 404

    data = request.get_json()
    message = ChatMessage(
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        content=data.get('content'),
        message_type=data.get('type', 'user')
    )
    db.session.add(message)
    db.session.commit()

    return jsonify({
        'id': message.message_id,
        'content': message.content,
        'type': message.message_type,
        'timestamp': message.timestamp.strftime('%d/%m/%Y %H:%M:%S')
    }), 201


@app.route('/api/chat/conversations/<int:conversation_id>', methods=['DELETE'])
@login_required
def delete_conversation(conversation_id):
    """Delete a conversation (only if user owns it)"""
    conversation = ChatConversation.query.filter_by(
        conversation_id=conversation_id,
        user_id=current_user.user_id
    ).first()

    if not conversation:
        return jsonify({'error': 'Conversation not found or access denied'}), 404

    db.session.delete(conversation)
    db.session.commit()

    return jsonify({'message': 'Conversation deleted'}), 200


# ============ PROFILE ============

@app.route('/profile')
@login_required
def profile():
    """Display and update user profile"""
    profile_form = ProfileForm()
    password_form = ChangePasswordForm()

    if profile_form.validate_on_submit() and request.method == 'POST' and 'profile_submit' in request.form:
        avatar_url = current_user.avatar

        if profile_form.avatar.data:
            avatar_url = current_user.avatar

        success, message = dao_user.update_user_profile(
            user_id=current_user.user_id,
            first_name=profile_form.first_name.data,
            last_name=profile_form.last_name.data,
            email=profile_form.email.data,
            phone_number=profile_form.phone_number.data,
            address=profile_form.address.data,
            date_of_birth=profile_form.date_of_birth.data,
            gender=profile_form.gender.data if profile_form.gender.data else None,
            avatar_url=avatar_url
        )

        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')

    elif password_form.validate_on_submit() and request.method == 'POST' and 'password_submit' in request.form:
        success, message = dao_user.change_password(
            user_id=current_user.user_id,
            old_password=password_form.current_password.data,
            new_password=password_form.new_password.data
        )

        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')

    if request.method == 'GET':
        profile_form.first_name.data = current_user.first_name
        profile_form.last_name.data = current_user.last_name
        profile_form.email.data = current_user.email
        profile_form.phone_number.data = current_user.phone_number
        profile_form.address.data = current_user.address
        profile_form.date_of_birth.data = current_user.date_of_birth
        profile_form.gender.data = current_user.gender.value if current_user.gender else 'OTHER'

    return render_template('profile.html', profile_form=profile_form, password_form=password_form)


# ============ OTHER PAGES ============

@app.route('/about')
def about():
    return render_template('about.html')
