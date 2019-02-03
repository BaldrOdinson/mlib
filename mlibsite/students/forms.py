#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, ValidationError, Email, Optional
from flask_wtf.file import FileField, FileAllowed


class AddStudentsGroupForm(FlaskForm):
    description = TextAreaField('Описание/название группы', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class UpdateStudentsGroupForm(FlaskForm):
    description = TextAreaField('Описание/название группы', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class AddStudentForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    age = StringField('Возраст')
    submit = SubmitField('Сохранить')


class UpdateStudentForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    age = StringField('Возраст')
    birthday = DateField('Дата рождения', format='%Y-%m-%d', validators=[Optional(),])
    sex = SelectField('Пол', choices=[('', ''), ('m', 'Мужской'), ('f', 'Женский')])
    phone_num = StringField('Номер телефона')
    email = StringField('Email', validators=[Optional(), Email()])
    address = StringField('Адрес')
    note = TextAreaField('Примечание')
    avatar = FileField('Загрузите картинку/аватар<br>для этого профиля (jpg или png)', validators=[FileAllowed(['jpg', 'png'])])
    document_type = StringField('Тип документа')
    document_number = StringField('Номер документа')
    attach = FileField('Для загрузки дополнительного файла (pdf, pptx, docx, txt, jpg)', validators=[FileAllowed(['pdf', 'pptx', 'docx', 'txt', 'jpg'], 'Файл должен быть разрешенного формата. <br>Проверьте загружаемый файл. <br>')])
    submit = SubmitField('Сохранить')


class SearchStudentForm(FlaskForm):
    first_name = StringField('Имя')
    last_name = StringField('Фамилия')
    age = StringField('Возраст')
    # birthday = DateField('Дата рождения', format='%Y-%m-%d', validators=[Optional(),])
    phone_num = StringField('Номер телефона')
    email = StringField('Email', validators=[Optional(), Email()])
    address = StringField('Адрес')
    submit = SubmitField('Найти')
