from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.security import check_password_hash
from models import User  # Models.py 가져옴

class SellingForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    keyword = StringField('keyword', validators=[DataRequired()])
    price = IntegerField('price', validators=[DataRequired()])
    contact = StringField('contact', validators=[DataRequired()])
    picture = FileField(validators=[FileRequired(), FileAllowed(['jpg', 'png'], '이미지만 업로드 가능합니다')])
    detail = TextAreaField('detail', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    userid = StringField('userid', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), EqualTo('password_2')])  # 비밀번호 확인
    password_2 = PasswordField('password_2', validators=[DataRequired()])


class LoginForm(FlaskForm):
    class UserPassword(object):
        def __init__(self, message=None):
            self.message = message

        def __call__(self, form, field):
            userid = form['userid'].data
            password = field.data

            error = None
            usertable = User.query.filter_by(userid=userid).first()
            if not usertable:
                error = '존재하지 않는 사용자입니다.'
            elif not check_password_hash(usertable.password, password):
                error = '비밀번호가 올바르지 않습니다.'
            flash(error)

    userid = StringField('userid', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), UserPassword()])
