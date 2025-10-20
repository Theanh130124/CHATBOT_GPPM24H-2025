from datetime import datetime
from app.extensions import db
from flask_login import UserMixin
import enum


class BaseModel(db.Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )


class GenderEnum(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class RoleEnum(enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class User(BaseModel, UserMixin):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum(GenderEnum))
    role = db.Column(db.Enum(RoleEnum), nullable=False)
    avatar = db.Column(
        db.String(255),
        default="https://res.cloudinary.com/dxiawzgnz/image/upload/v1732632586/pfvvxablnkaeqmmbqeit.png"
    )
    is_active = db.Column(db.Boolean, default=True)

    symptom = db.relationship('Symptom', backref='user', cascade='all, delete')
    skin_images = db.relationship('SkinImage', backref='user', cascade='all, delete')
    conversations = db.relationship('ChatConversation', backref='user', cascade='all, delete')

    def get_id(self):
        return str(self.user_id)


class Symptom(BaseModel):
    __tablename__ = 'symptom'

    symptom_id = db.Column(db.Integer, primary_key=True)
    description_text = db.Column(db.Text, nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.user_id', ondelete='CASCADE'),
        nullable=True
    )

    skin_images = db.relationship('SkinImage', backref='symptom', cascade='all, delete')


class SkinImage(BaseModel):
    __tablename__ = 'skinimage'

    skinimage_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.user_id', ondelete='CASCADE'),
        nullable=True
    )
    symptom_id = db.Column(
        db.Integer,
        db.ForeignKey('symptom.symptom_id', ondelete='CASCADE'),
        nullable=True
    )
    image_path = db.Column(db.String(255), nullable=False)

    cv_predictions = db.relationship('CVPrediction', backref='skin_image', cascade='all, delete')


class CVPrediction(db.Model):
    __tablename__ = 'cvprediction'

    cvprediction_id = db.Column(db.Integer, primary_key=True)
    skinimage_id = db.Column(
        db.Integer,
        db.ForeignKey('skinimage.skinimage_id', ondelete='CASCADE'),
        nullable=False
    )
    confidence = db.Column(db.Float, nullable=False)


class ChatConversation(BaseModel):
    __tablename__ = 'chatconversation'

    conversation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.user_id', ondelete='CASCADE'),
        nullable=False
    )
    title = db.Column(db.String(255), nullable=False, default="Cuộc trò chuyện mới")

    messages = db.relationship('ChatMessage', backref='conversation', cascade='all, delete')


class ChatMessage(BaseModel):
    __tablename__ = 'chatmessage'

    message_id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey('chatconversation.conversation_id', ondelete='CASCADE'),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.user_id', ondelete='CASCADE'),
        nullable=False
    )
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), nullable=False)  # 'user' or 'bot'
    timestamp = db.Column(db.DateTime, default=datetime.now)
