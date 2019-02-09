#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, ValidationError, Email, Optional
from flask_wtf.file import FileField, FileAllowed


class CommonSearchStudentForm(FlaskForm):
    first_name = StringField('Имя')
    last_name = StringField('Фамилия')
    age = StringField('Возраст')
    phone_num = StringField('Номер телефона')
    email = StringField('Email', validators=[Optional(), Email()])
    address = StringField('Адрес')
    submit = SubmitField('Найти')


class CommonSearchMethodForm(FlaskForm):
    author = StringField('Автор методики в системе')
    title = StringField('Название')
    short_desc = TextAreaField('Краткое описание')
    target = StringField('Цель')
    consumables = TextAreaField('Необходимые материалы')
    category = IntegerField('Категория')
    tags = StringField('Теги')
    submit = SubmitField('Найти')


class CommonSearchProjectForm(FlaskForm):
    name = StringField('Название')
    short_desc = TextAreaField('Краткое описание')
    contacts = StringField('Контакты')
    address = StringField('Адрес')
    web_links = StringField('Ссылки')
    submit = SubmitField('Найти')
