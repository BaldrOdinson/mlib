#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed

class MethodForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    short_desc = TextAreaField('Короткое описание', validators={DataRequired()})
    target = StringField('Цель', validators=[DataRequired()])
    description = TextAreaField('Полное описание', validators=[DataRequired()])
    age_range_from = IntegerField('От', validators=[NumberRange(min=0, max=130, message='Некорректный минимальный возраст.'), DataRequired('Поле минимального возраста участников должно содержать только цифры.')])
    age_range_till = IntegerField('До', validators=[NumberRange(min=0, max=130, message='Некорректный максимальный возраст.'), DataRequired('Поле максимального возраста участников должно содержать только цифры.')])
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

    def check_age_range(self, age_from, age_till):
        if age_from > age_till:
            raise ValidationError('Минимальный возраст не должен быть больше максимального. Проверьте.')


class UpdateMethodForm(FlaskForm):
    title = StringField('Название методики', validators=[DataRequired()])
    method_label_image = FileField('Для изменения заглавного изображения<br>этой методики (jpg или png)', validators=[FileAllowed(['jpg', 'png'], 'Формат файла аватара должен быть <strong>JPG</strong> или <strong>PNG</strong>. Проверьте расширение загружаемого файла.')])
    short_desc = TextAreaField('Короткое описание', validators={DataRequired()})
    target = StringField('Цель', validators=[DataRequired()])
    description = TextAreaField('Полное описание', validators=[DataRequired()])
    age_range_from = IntegerField('От', validators=[NumberRange(min=0, max=130, message='Некорректный минимальный возраст.'), DataRequired('Поле минимального возраста участников должно содержать только цифры.')])
    age_range_till = IntegerField('До', validators=[NumberRange(min=0, max=130, message='Некорректный максимальный возраст.'), DataRequired('Поле максимального возраста участников должно содержать только цифры.')])
    consumables = TextAreaField('Используемые материалы')
    timing_id = IntegerField('Длительность занятия ')
    presentation = FileField('Для загрузки файла с презентацией (pdf, pptx)', validators=[FileAllowed(['pdf', 'pptx', 'docx', 'txt'], 'Презентация должна быть формата <strong>PowerPoint</strong> или <strong>PDF</strong> (расширение файла pptx или pdf). <br>Текст пояснения презентации должен быть в формате Word (docx) или текстовый файл (txt). <br>Проверьте загружаемый файл.')])
    images = TextAreaField('Картинки')
    music = TextAreaField('Музыка')
    video = TextAreaField('Видео')
    literature = TextAreaField('Тематическая литература')
    category = IntegerField('Категория', default=1)
    tags = StringField('Теги')
    submit = SubmitField('Сохранить')

    def check_age_range(self, age_from, age_till):
        if age_from > age_till:
            raise ValidationError('Минимальный возраст не должен быть больше максимального. Проверьте.')


class AddCategoryForm(FlaskForm):
    new_category_name = StringField('Название категории', validators=[DataRequired()])
    parrent_cat = StringField('Родительская категория', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class SearchMethodForm(FlaskForm):
    author = StringField('Автор методики в системе')
    title = StringField('Название')
    # age_from = StringField('Минимальный возраст') #, choices=[zip(range(5, 80), range(5, 80))])
    # age_till = StringField('Максимальный возраст') #, choices=[zip(range(5, 80), range(5, 80))])
    short_desc = TextAreaField('Короткое описание')
    target = StringField('Цель')
    consumables = TextAreaField('Необходимые материалы')
    category = IntegerField('Категория')
    tags = StringField('Теги')
    submit = SubmitField('Найти')
