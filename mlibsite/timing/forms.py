#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, ValidationError, NumberRange
from flask_wtf.file import FileField, FileAllowed

class AddTimingForm(FlaskForm):
    duration = IntegerField('Длительность всего занятия в минутах', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def check_duration_data_type(self, field):
        if not field.data:
            flash('Значение длительности не выглядит как правильное')


class AddTimingStepsForm(FlaskForm):
    step_duration = IntegerField('Длительность этапа в минутах', validators=[DataRequired()])
    step_desc = TextAreaField('Описание этапа', validators=[DataRequired()])
    step_result = TextAreaField('Результат этапа', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def check_duration_data_type(self, field):
        if not field.data:
            flash('Значение длительности не выглядит как правильное')
            # raise ValidationError('Значение длительности не выглядит как привильное значение')
