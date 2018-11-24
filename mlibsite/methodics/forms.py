#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed

class MethodForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    short_desc = TextAreaField('Короткое описание', validators={DataRequired()})
    target = StringField('Цель', validators=[DataRequired()])
    description = TextAreaField('Полное описание', validators=[DataRequired()])
    consumables = TextAreaField('Используемые материалы')
    timing_id = IntegerField('Ход занятия')
    presentation = StringField('Презентация')
    images = TextAreaField('Картинки')
    music = TextAreaField('Музыка')
    video = TextAreaField('Видео')
    literature = TextAreaField('Тематическая литература')
    category = IntegerField('Категория')
    tags = StringField('Теги')
    submit = SubmitField('Сохранить')


class UpdateMethodForm(FlaskForm):
    title = StringField('Название методики', validators=[DataRequired()])
    method_label_image = FileField('Для изменения заглавного изображения этой методики<br>(jpg или png)', validators=[FileAllowed(['jpg', 'png'])])
    short_desc = TextAreaField('Короткое описание', validators={DataRequired()})
    target = StringField('Цель', validators=[DataRequired()])
    description = TextAreaField('Полное описание', validators=[DataRequired()])
    consumables = TextAreaField('Используемые материалы')
    timing_id = IntegerField('Длительность занятия ')
    presentation = FileField('Для загрузки файла с презентацией (pdf, pptx)', validators=[FileAllowed(['pdf', 'pptx'])])
    images = TextAreaField('Картинки')
    music = TextAreaField('Музыка')
    video = TextAreaField('Видео')
    literature = TextAreaField('Тематическая литература')
    category = IntegerField('Категория', default=1)
    tags = StringField('Теги')
    submit = SubmitField('Сохранить')
