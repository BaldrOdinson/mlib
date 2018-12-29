#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed

class MethodForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    short_desc = TextAreaField('Короткое описание', validators={DataRequired()})
    target = StringField('Цель', validators=[DataRequired()])
    description = TextAreaField('Полное описание', validators=[DataRequired()])
    age_range_from = IntegerField('От', validators=[DataRequired()])
    age_range_till = IntegerField('До', validators=[DataRequired()])
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

    def check_age_data_type(self, field):
        if not field.data:
            flash('Значение возраста не выглядит как правильное. Должны быть только цифры.', 'negative')


class UpdateMethodForm(FlaskForm):
    title = StringField('Название методики', validators=[DataRequired()])
    method_label_image = FileField('Для изменения заглавного изображения этой методики<br>(jpg или png)', validators=[FileAllowed(['jpg', 'png'], 'Формат файла аватара должен быть <strong>JPG</strong> или <strong>PNG</strong>. Проверьте расширение загружаемого файла. <br>')])
    short_desc = TextAreaField('Короткое описание', validators={DataRequired()})
    target = StringField('Цель', validators=[DataRequired()])
    description = TextAreaField('Полное описание', validators=[DataRequired()])
    age_range_from = IntegerField('От', validators=[DataRequired()])
    age_range_till = IntegerField('До', validators=[DataRequired()])
    consumables = TextAreaField('Используемые материалы')
    timing_id = IntegerField('Длительность занятия ')
    presentation = FileField('Для загрузки файла с презентацией (pdf, pptx)', validators=[FileAllowed(['pdf', 'pptx'], 'Презентация должна быть формата <strong>PowerPoint</strong> или <strong>PDF</strong> (расширение файла pptx или pdf). Проверьте загружаемый файл. <br>')])
    images = TextAreaField('Картинки')
    music = TextAreaField('Музыка')
    video = TextAreaField('Видео')
    literature = TextAreaField('Тематическая литература')
    category = IntegerField('Категория', default=1)
    tags = StringField('Теги')
    submit = SubmitField('Сохранить')

    def check_age_data_type(self, field):
        if not field.data:
            flash('Значение возраста не выглядит как правильное. Должны быть только цифры. Последние изменения предположительно не сохранились. Проверьте.', 'negative')


class AddCategoryForm(FlaskForm):
    new_category_name = StringField('Название категории', validators=[DataRequired()])
    parrent_cat = StringField('Родительская категория', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
