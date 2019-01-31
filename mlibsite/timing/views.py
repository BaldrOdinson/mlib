#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, request, redirect, Blueprint, current_app
from flask_login import current_user, login_required
from mlibsite import db
from mlibsite.models import MethodTiming, TimingSteps, Methodics
from mlibsite.timing.forms import AddTimingForm, AddTimingStepsForm
from mlibsite.methodics.picture_handler import add_method_pic, thumbnail_for_net_pic, img_tupal, thumbnail_list
from datetime import datetime
from mlibsite.methodics.text_formater import text_format_for_html
# import os, shutil
from mlibsite.timing.misc_func import time_left


timing = Blueprint('timing', __name__, template_folder='templates/timing')

# views

# Add timing
# Add step
# Edit timing
# Step update
# Delete step_

###### ADD TIMING ######
@timing.route('/<int:method_id>/timing', methods=['GET', 'POST'])
@login_required
def add_timing(method_id):
    """
    Создаем новый тайминг для методики method_id
    """
    form = AddTimingForm()

    if form.validate_on_submit():
        timing = MethodTiming(method_id=method_id,
                                duration = form.duration.data)
        db.session.add(timing)
        db.session.commit()
        timing = MethodTiming.query.filter_by(method_id=method_id).first()
        method = Methodics.query.get_or_404(method_id)
        method.timing_id = timing.id
        db.session.commit()
        return redirect(url_for('timing.edit_timing', method_id=method_id))

    return render_template('add_timing.html',
                            form=form,
                            method_id=method_id)


##### ADD TIMING STEP #####
@timing.route('/timing_<int:timing_id>/timing_steps', methods=['GET', 'POST'])
@login_required
def add_timing_step(timing_id):
    """
    Создаем новый этап у тайминга timing_id
    """
    form = AddTimingStepsForm()

    if form.validate_on_submit():
        timing_step = TimingSteps(method_timing_id=timing_id,
                                step_duration = form.step_duration.data,
                                step_desc = form.step_desc.data,
                                step_result = form.step_result.data)

        db.session.add(timing_step)
        db.session.commit()
        method = Methodics.query.filter_by(timing_id=timing_id).first()
        return redirect(url_for('timing.edit_timing', method_id=method.id))
    # Если первая загрузка формы поле step_duration не проверяем.
    if (form.step_duration.data == None and
        (form.step_desc.data != None or form.step_result.data != None)):
        form.check_duration_data_type(form.step_duration)
    return render_template('add_timing_step.html', form=form, timing_id=timing_id)


###### EDIT TIMING ######
@timing.route('/<int:method_id>/timing_update', methods=['GET', 'POST'])
@login_required
def edit_timing(method_id):
    """
    Редактируем и дополняем существующий тайминг для методики method_id
    """
    timing = MethodTiming.query.filter_by(method_id=method_id).first()
    method = Methodics.query.get_or_404(method_id)
    # steps = TimingSteps.query.filter_by(method_timing_id=method.timing_id)
    steps = db.session.query(TimingSteps).filter_by(method_timing_id=timing.id).order_by('id')
    timing_left = time_left(steps, timing.duration)
    print(steps)

    form = AddTimingForm()

    if form.validate_on_submit():
        timing.duration = form.duration.data

        db.session.commit()
        return redirect(url_for('methodics.update', method_id=method.id))
    elif request.method == 'GET':
        form.duration.data = timing.duration
    form.check_duration_data_type(form.duration)
    return render_template('update_timing.html',
                                    form=form,
                                    timing_id=timing.id,
                                    method_author=method.author,
                                    method_id=method.id,
                                    steps=steps,
                                    timing_left=timing_left)


##### UPDATE TIMING STEP #####
@timing.route('/step_<int:step_id>/timing_steps_update', methods=['GET', 'POST'])
@login_required
def step_update(step_id):
    """
    Редактируем существующий этап (step_id) тайминга
    """
    form = AddTimingStepsForm()

    # step = TimingSteps.query.get_or_404(step_id)
    step = db.session.query(TimingSteps).filter_by(id=step_id).first()
    timing_id = step.method_timing_id
    if form.validate_on_submit():
        step.step_duration = form.step_duration.data
        step.step_desc = form.step_desc.data
        step.step_result = form.step_result.data

        db.session.commit()
        method = Methodics.query.filter_by(timing_id=timing_id).first()
        return redirect(url_for('timing.edit_timing', method_id=method.id))
    elif request.method == 'GET':
        print(f'duration {step.step_duration}\ndescription {step.step_desc}')
        form.step_duration.data = step.step_duration
        form.step_desc.data = step.step_desc
        form.step_result.data = step.step_result
    form.check_duration_data_type(form.step_duration)
    return render_template('add_timing_step.html', form=form)


###### DELETE TIMING STEP ######
@timing.route('/step_<int:step_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_timing_step(step_id):
    """
    Удаляем этап (step_id) тайминга
    """
    step = TimingSteps.query.get_or_404(step_id)
    timing_id = step.method_timing_id
    method = Methodics.query.filter_by(timing_id=timing_id).first()
    print(f'id {step_id}, step_id {step_id}')
    db.session.delete(step)
    db.session.commit()
    flash('Этап занятия удален', 'warning')
    return redirect(url_for('timing.edit_timing', method_id=method.id))
