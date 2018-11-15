#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed

class MethodForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    short_desc = TextAreaField('Short Description', validators={DataRequired()})
    target = StringField('Target', validators=[DataRequired()])
    description = TextAreaField('Descrpition', validators=[DataRequired()])
    consumables = TextAreaField('Consumables')
    timing_id = IntegerField('Timing')
    presentation = StringField('Presentation')
    images = TextAreaField('Images')
    music = TextAreaField('Music')
    video = TextAreaField('Video')
    literature = TextAreaField('Literature')
    category = IntegerField('Category')
    tags = StringField('Tags')
    submit = SubmitField('Сохранить')


class UpdateMethodForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    method_label_image = FileField('Загрузите заглавное изображение для этой методики (jpg или png)', validators=[FileAllowed(['jpg', 'png'])])
    short_desc = TextAreaField('Short Description', validators={DataRequired()})
    target = StringField('Target', validators=[DataRequired()])
    description = TextAreaField('Descrition', validators=[DataRequired()])
    consumables = TextAreaField('Consumables')
    timing_id = IntegerField('Timing', default=1)
    presentation = StringField('Presentation')
    images = TextAreaField('Images')
    music = TextAreaField('Music')
    video = TextAreaField('Video')
    literature = TextAreaField('Literature')
    category = IntegerField('Category', default=1)
    tags = StringField('Tags')
    submit = SubmitField('Сохранить')
