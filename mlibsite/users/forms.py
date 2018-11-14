# related to forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
# related to users
from flask_login import current_user
from mlibsite.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Имя пользователя (никнейм)', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), EqualTo('pass_confirm', message='Passwords must match!')])
    pass_confirm = PasswordField('Подтверждение пароля', validators=[DataRequired()])
    first_name = StringField('Имя')
    last_name = StringField('Фамилия')
    phone_num = StringField('Номер телефона')
    address = StringField('Адрес')
    curr_job_place = StringField('Место работы')
    submit = SubmitField('Зарегистрироваться')

    def check_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has been register already!')

    def check_phone_num(self, field):
        if User.query.filter_by(phone_num=field.data).first():
            raise ValidationError('Your phone number has been register already!')

    def check_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Your username has been register already!')


class UpdateUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Имя пользователя (никнейм)', validators=[DataRequired()])
    first_name = StringField('Имя')
    last_name = StringField('Фамилия')
    phone_num = StringField('Номер телефона')
    address = StringField('Адрес')
    curr_job_place = StringField('Место работы')
    picture = FileField('Загрузите картинку для своего профиля (jpg или png)', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Сохранить')

    def check_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has been register already!')

    def check_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Your username has been register already!')
