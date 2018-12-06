#! /usr/bin/env python
# -*- coding: utf-8 -*-
# related to forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
# related to users
from flask_user import current_user
from mlibsite.models import User


class UpdateUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Имя пользователя (никнейм)', validators=[DataRequired()])
    first_name = StringField('Имя')
    last_name = StringField('Фамилия')
    phone_num = StringField('Номер телефона')
    address = StringField('Адрес')
    curr_job_place = StringField('Место работы')
    picture = FileField('Загрузите картинку/аватар для своего профиля (jpg или png)', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Сохранить')

    def check_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Указанный вами email уже зарегистрирован.')

    def check_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Выбранное вами имя пользователя занято.')
