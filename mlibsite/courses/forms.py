#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, ValidationError
from flask_wtf.file import FileField, FileAllowed


class AddCourseForm(FlaskForm):
    name = StringField('Название курса', validators=[DataRequired()])
    description = TextAreaField('Описание курса')
    start_date = DateField('Дата начала', format='%Y-%m-%d', validators=[DataRequired()])
    finish_date = DateField('Дата завершения', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class UpdateCourseForm(FlaskForm):
    name = StringField('Название курса', validators=[DataRequired()])
    description = TextAreaField('Описание курса')
    label_image = FileField('Для изменения заглавного изображения этого проекта<br>(jpg или png)', validators=[FileAllowed(['jpg', 'png'], 'Формат файла аватара должен быть <strong>JPG</strong> или <strong>PNG</strong>. Проверьте расширение загружаемого файла. <br>')])
    start_date = DateField('Дата начала', format='%Y-%m-%d', validators=[DataRequired()])
    finish_date = DateField('Дата завершения', format='%Y-%m-%d', validators=[DataRequired()])
    contacts_info = TextAreaField('Контакты')
    address = TextAreaField('Адрес')
    tutors = TextAreaField('Преподаватели')
    web_links = TextAreaField('Ссылки')
    note = TextAreaField('Примечание')
    attach = FileField('Для загрузки дополнительного файла (pdf, pptx, docx, txt)', validators=[FileAllowed(['pdf', 'pptx', 'docx', 'txt'], 'Файл должен быть разрешенного формата. <br>Проверьте загружаемый файл. <br>')])
    submit = SubmitField('Сохранить')


class AddLessonForm(FlaskForm):
    description = TextAreaField('Описание занятия')
    lesson_date = DateField('Дата занятия', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('Время начала занятия', format='%H:%M')
    finish_time = TimeField('Время завершения занятия', format='%H:%M')
    submit = SubmitField('Сохранить')


class UpdateLessonForm(FlaskForm):
    description = TextAreaField('Описание занятия')
    lesson_date = DateField('Дата занятия', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('Время начала занятия', format='%H:%M')
    finish_time = TimeField('Время завершения занятия', format='%H:%M')
    method_id = IntegerField('Методика занятия')
    tutors = TextAreaField('Ведущие курса, педагоги')
    absent_students_list = StringField('Отсутствующие участники')
    web_links = TextAreaField('Ссылки')
    note = TextAreaField('Примечание')
    attach = FileField('Для загрузки дополнительного файла (pdf, pptx, docx, txt, jpg)', validators=[FileAllowed(['pdf', 'pptx', 'docx', 'txt', 'jpg'], 'Файл должен быть разрешенного формата. <br>Проверьте загружаемый файл. <br>')])
    submit = SubmitField('Сохранить')
