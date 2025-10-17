from datetime import datetime
from app.extensions import db
from flask_login import UserMixin

import enum





class BaseModel(db.Model):
    __abstract__ = True  # Không tạo bảng riêng

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
    DOCTOR = "USER"
    ADMIN = "ADMIN"

class User(BaseModel,UserMixin):
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
    #Thêm backref nữa truy vấn ngược.
    symptom = db.relationship('Symptom',backref='user', cascade='all, delete')


#Triệu chứng + Câu hỏi ng dùng
class Symptom(BaseModel):
    __tablename__ = 'symptom'

    symptom_id = db.Column(db.Integer, primary_key=True)
    description_text = db.Column(db.Text, nullable=False)

    #Khóa ngoại
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.user_id', ondelete='CASCADE'),
        nullable=True #Tài khoản khách nên được trống
    )

#Ảnh của nguoi dung gửi
class SkinImage(BaseModel):
    __tablename__ = 'skinimage'

    skinimage_id = db.Column(db.Integer, primary_key=True)

    #Khóa ngoại
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.user_id', ondelete='CASCADE'),
        nullable=True #Tài khoản khách nên được trống
    )
    symptom_id = db.Column(
        db.Integer,
        db.ForeignKey('symptom.symptom_id', ondelete='CASCADE'),
        nullable=True #Tài khoản khách nên được trống
    )
    image_path = db.Column(db.String(255), nullable=False)


#Kết quả phân loại từ CV
class CVPrediction(db.Model):
    __tablename__ = 'cvprediction'
    cvprediction_id = db.Column(db.Integer, primary_key=True)
    skinimage_id = db.Column(
        db.Integer,
        db.ForeignKey('skinimage.skinimage_id', ondelete='CASCADE'),
        nullable=False
    )
    #Độ tin cậy -> gần với accuracy
    confidence = db.Column(db.Float, nullable=False)

class ChatMemory(BaseModel):
    __tablename__ = 'chatmemory'
    chatmemory_id = db.Column(db.Integer, primary_key=True)


    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.user_id', ondelete='CASCADE'),
        nullable=True #Tài khoản khách nên được trống
    )
    input_text = db.Column(db.Text, nullable=False)
    cv_label = db.Column(db.String(100), nullable=True)
    retrieved_text = db.Column(db.Text, nullable=True)
    response_text = db.Column(db.Text, nullable=True)