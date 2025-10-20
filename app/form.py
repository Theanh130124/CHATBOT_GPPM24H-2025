from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError, InputRequired
from flask_wtf.file import FileAllowed
from app.dao import dao_authen

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired()],
                           render_kw={"placeholder": "Tên đăng nhập"})
    password = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "Mật khẩu"})
    SubmitFieldLogin = SubmitField("Đăng nhập")



class RegisterForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[
        DataRequired(message='Tên đăng nhập là bắt buộc'),
        Length(min=3, max=50, message='Tên đăng nhập phải từ 3-50 ký tự')
    ])

    email = StringField('Email', validators=[
        DataRequired(message='Email là bắt buộc'),
        Email(message='Email không hợp lệ')
    ])

    password = PasswordField('Mật khẩu', validators=[
        DataRequired(message='Mật khẩu là bắt buộc'),
        Length(min=6, message='Mật khẩu phải có ít nhất 6 ký tự'),
        EqualTo('confirm_password', message='Mật khẩu xác nhận không khớp')
    ])

    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[
        DataRequired(message='Xác nhận mật khẩu là bắt buộc')
    ])

    first_name = StringField('Họ', validators=[
        DataRequired(message='Họ là bắt buộc'),
        Length(max=50, message='Họ không được vượt quá 50 ký tự')
    ])

    last_name = StringField('Tên', validators=[
        DataRequired(message='Tên là bắt buộc'),
        Length(max=50, message='Tên không được vượt quá 50 ký tự')
    ])

    phone_number = StringField('Số điện thoại', validators=[
        DataRequired(message='Số điện thoại là bắt buộc'),
        Length(min=10, max=10, message='Số điện thoại phải từ 10 số')
    ])

    address = StringField('Địa chỉ', validators=[
        DataRequired(message='Địa chỉ là bắt buộc'),
        Length(max=200, message='Địa chỉ không được vượt quá 200 ký tự')
    ])

    date_of_birth = DateField('Ngày sinh', validators=[
        DataRequired(message='Ngày sinh là bắt buộc')
    ])

    gender = SelectField('Giới tính', choices=[
        ('MALE', 'Nam'),
        ('FEMALE', 'Nữ'),
        ('OTHER', 'Khác')
    ], validators=[DataRequired(message='Giới tính là bắt buộc')])

    submit = SubmitField('Đăng ký')

    def validate_username(self, username):
        """Custom validation cho username"""
        if dao_authen.check_username_exists(username.data):
            raise ValidationError('Tên đăng nhập đã tồn tại')

    def validate_email(self, email):
        """Custom validation cho email"""
        if dao_authen.check_email_exists(email.data):
            raise ValidationError('Email đã tồn tại')

    def validate_phone_number(self, phone_number):
        """Custom validation cho số điện thoại"""
        # Kiểm tra định dạng số điện thoại Việt Nam
        if not phone_number.data.isdigit():
            raise ValidationError('Số điện thoại chỉ được chứa số')

        if dao_authen.check_phone_exists(phone_number.data):
            raise ValidationError('Số điện thoại đã tồn tại')

class ProfileForm(FlaskForm):
    """Form để cập nhật thông tin cá nhân"""
    first_name = StringField('Tên', validators=[
        DataRequired(message="Tên không được để trống"),
        Length(min=2, max=100, message="Tên phải từ 2-100 ký tự")
    ])
    
    last_name = StringField('Họ', validators=[
        DataRequired(message="Họ không được để trống"),
        Length(min=2, max=100, message="Họ phải từ 2-100 ký tự")
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message="Email không được để trống"),
        Email(message="Email không hợp lệ")
    ])
    
    phone_number = StringField('Số điện thoại', validators=[
        DataRequired(message="Số điện thoại không được để trống"),
        Length(min=10, max=20, message="Số điện thoại không hợp lệ")
    ])
    
    address = StringField('Địa chỉ', validators=[
        DataRequired(message="Địa chỉ không được để trống"),
        Length(min=5, max=255, message="Địa chỉ phải từ 5-255 ký tự")
    ])
    
    date_of_birth = DateField('Ngày sinh', validators=[Optional()], format='%Y-%m-%d')
    
    gender = SelectField('Giới tính', choices=[
        ('MALE', 'Nam'),
        ('FEMALE', 'Nữ'),
        ('OTHER', 'Khác')
    ], validators=[Optional()])
    
    avatar = FileField('Ảnh đại diện', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ chấp nhận ảnh (jpg, jpeg, png, gif)')
    ])
    
    submit = SubmitField('Cập nhật thông tin')


class ChangePasswordForm(FlaskForm):
    """Form để đổi mật khẩu"""
    current_password = PasswordField('Mật khẩu hiện tại', validators=[
        DataRequired(message="Mật khẩu hiện tại không được để trống")
    ])
    
    new_password = PasswordField('Mật khẩu mới', validators=[
        DataRequired(message="Mật khẩu mới không được để trống"),
        Length(min=6, max=100, message="Mật khẩu phải từ 6-100 ký tự")
    ])
    
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[
        DataRequired(message="Xác nhận mật khẩu không được để trống"),
        EqualTo('new_password', message="Mật khẩu xác nhận không khớp")
    ])
    
    submit = SubmitField('Đổi mật khẩu')
