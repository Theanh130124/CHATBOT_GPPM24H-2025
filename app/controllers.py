import uuid
import datetime
import base64
from flask import render_template, redirect, request, url_for, session, flash, jsonify
from flask_login import current_user, logout_user, login_required, login_user

from app.models import RoleEnum, User, ChatConversation, ChatMessage, Symptom, SkinImage, CVPrediction
from app import app, flow
from app.form import LoginForm, RegisterForm, ProfileForm, ChangePasswordForm
from app.dao import dao_authen, dao_user
from app.extensions import db
from app.rag_chatbot import rag_chatbot
from app.cv_model import cv_model

import google.oauth2.id_token
import google.auth.transport.requests
import requests
import cloudinary.uploader


def _clean_html_tags(text):
    """Remove HTML tags from text"""
    import re
    if not text:
        return text
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

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
            db.session.commit()
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



#---------- RAG - CNN -------------


@app.route('/api/chat/send-message', methods=['POST'])
@login_required
def send_chat_message():
    """Handle chat messages with both text and image"""
    try:
        data = request.get_json()
        message_text = data.get('message', '')
        image_data = data.get('image', None)
        conversation_id = data.get('conversation_id')

        # Validate input
        if not message_text and not image_data:
            return jsonify({'error': 'Message or image is required'}), 400

        # Tìm hoặc tạo conversation
        if conversation_id:
            conversation = ChatConversation.query.filter_by(
                conversation_id=conversation_id,
                user_id=current_user.user_id
            ).first()
            if not conversation:
                return jsonify({'error': 'Conversation not found'}), 404
        else:
            # Tạo conversation mới với title từ message đầu tiên
            title = message_text[:50] + "..." if message_text else "Cuộc trò chuyện mới"
            conversation = ChatConversation(
                user_id=current_user.user_id,
                title=title
            )
            db.session.add(conversation)
            db.session.flush()  # Get the ID without committing

        # Lưu tin nhắn người dùng
        user_message = ChatMessage(
            conversation_id=conversation.conversation_id,
            user_id=current_user.user_id,
            content=message_text,
            message_type='user'
        )
        db.session.add(user_message)
        db.session.flush()

        response_text = ""
        cv_prediction = None
        raw_disease_name = None
        confidence = None

        # Xử lý hình ảnh nếu có
        if image_data:
            try:
                image_bytes = base64.b64decode(image_data.split(',')[1])

                # Dự đoán bằng CNN model
                disease_name, conf, raw_disease_name = cv_model.predict(image_bytes)
                confidence = float(conf) if conf else 0.0

                if disease_name and confidence > 0.5:  # Only show if confidence > 50%
                    cv_prediction = f"Phân tích hình ảnh cho thấy dấu hiệu của: **{disease_name}** (độ tin cậy: {confidence:.1%})."

                    # Lưu hình ảnh và kết quả dự đoán
                    try:
                        upload_result = cloudinary.uploader.upload(
                            image_bytes,
                            folder="skin_images"
                        )

                        symptom = Symptom(
                            user_id=current_user.user_id,
                            description_text=message_text if message_text else f"Phân tích hình ảnh da - {disease_name}"
                        )
                        db.session.add(symptom)
                        db.session.flush()

                        skin_image = SkinImage(
                            user_id=current_user.user_id,
                            symptom_id=symptom.symptom_id,
                            image_path=upload_result['secure_url']
                        )
                        db.session.add(skin_image)
                        db.session.flush()

                        cv_pred = CVPrediction(
                            skinimage_id=skin_image.skinimage_id,
                            confidence=confidence,
                            disease_name=raw_disease_name
                        )
                        db.session.add(cv_pred)

                    except Exception as e:
                        app.logger.error(f"Error saving image data: {e}")
                else:
                    cv_prediction = "Không thể xác định rõ tình trạng da từ hình ảnh. Vui lòng thử lại với hình ảnh rõ hơn hoặc mô tả thêm triệu chứng."

            except Exception as e:
                app.logger.error(f"Image processing error: {e}")
                cv_prediction = "Có lỗi xảy ra khi xử lý hình ảnh. Vui lòng thử lại."

        # Tạo câu hỏi tổng hợp cho RAG
        combined_query = message_text
        if cv_prediction:
            combined_query = f"{message_text}. {cv_prediction}" if message_text else cv_prediction

        # Lấy response từ RAG
        if combined_query.strip():
            try:
                response_text = rag_chatbot.get_rag_response(combined_query, conversation.conversation_id)
            except Exception as e:
                app.logger.error(f"RAG Error: {e}")
                response_text = "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại."
        else:
            response_text = "Xin hãy mô tả vấn đề hoặc gửi hình ảnh để tôi có thể tư vấn."

        # Lưu tin nhắn bot
        bot_message = ChatMessage(
            conversation_id=conversation.conversation_id,
            user_id=current_user.user_id,
            content=response_text,
            message_type='bot'
        )
        db.session.add(bot_message)

        # Cập nhật thời gian conversation
        conversation.updated_at = datetime.datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'conversation_id': conversation.conversation_id,
            'response': response_text,
            'cv_prediction': cv_prediction,
            'disease_name': raw_disease_name,
            'confidence': confidence
        })

    except Exception as e:
        app.logger.error(f"Chat error: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Có lỗi xảy ra khi xử lý tin nhắn'
        }), 500


@app.route('/api/chat/upload-image', methods=['POST'])
@login_required
def upload_chat_image():
    """Upload image for analysis"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file'}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Convert to base64 for frontend preview
        image_bytes = image_file.read()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

        return jsonify({
            'success': True,
            'image_data': f"data:image/jpeg;base64,{image_b64}"
        })

    except Exception as e:
        app.logger.error(f"Image upload error: {e}")
        return jsonify({'error': 'Upload failed'}), 500