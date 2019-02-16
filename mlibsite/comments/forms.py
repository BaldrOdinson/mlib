#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed


class AddCommentForm(FlaskForm):
    body = TextAreaField('Ваш комментарий', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class UpdateCommentForm(FlaskForm):
    body = TextAreaField('Ваш комментарий', validators=[DataRequired()])
    submit = SubmitField('Изменить')
