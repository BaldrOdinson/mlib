#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, ValidationError
from flask_wtf.file import FileField, FileAllowed


class AddProjectForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    short_desc = TextAreaField('Краткое описание проекта', validators={DataRequired()})
    submit = SubmitField('Сохранить')


class UpdateProjectForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    short_desc = TextAreaField('Краткое описание проекта', validators={DataRequired()})
    description = TextAreaField('Полное описание')
    label_image = FileField('Для изменения заглавного изображения<br>этого проекта (jpg или png)', validators=[FileAllowed(['jpg', 'png'], 'Формат файла аватара должен быть <strong>JPG</strong> или <strong>PNG</strong>. Проверьте расширение загружаемого файла. <br>')])
    moders_list = TextAreaField('Роли пользователей')
    contacts_info = TextAreaField('Контакты')
    address = TextAreaField('Адрес')
    note = TextAreaField('Примечание')
    web_links = TextAreaField('Ссылки')
    attach = FileField('Для загрузки дополнительного файла (pdf, pptx, docx, txt, jpg или png)', validators=[FileAllowed(['pdf', 'pptx', 'docx', 'txt', 'jpg', 'png'], 'Файл должен быть разрешенного формата. <br>Проверьте загружаемый файл. <br>')])
    submit = SubmitField('Сохранить')


class AddTermForm(FlaskForm):
    name = StringField('Название периода', validators=[DataRequired()])
    description = TextAreaField('Описание периода')
    start_date = DateField('Дата начала', format='%Y-%m-%d')
    finish_date = DateField('Дата завершения', format='%Y-%m-%d')
    submit = SubmitField('Сохранить')


class UpdateTermForm(FlaskForm):
    name = StringField('Название периода', validators=[DataRequired()])
    description = TextAreaField('Описание периода')
    start_date = DateField('Дата начала')
    finish_date = DateField('Дата завершения')
    label_image = FileField('Для изменения заглавного изображения<br>этого периода (jpg или png)', validators=[FileAllowed(['jpg', 'png'], 'Формат файла аватара должен быть <strong>JPG</strong> или <strong>PNG</strong>. Проверьте расширение загружаемого файла. <br>')])
    submit = SubmitField('Сохранить')
