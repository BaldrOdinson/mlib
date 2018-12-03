#! /usr/bin/env python
# -*- coding: utf-8 -*-

#user's views
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_user import current_user, login_required
# from flask_login import logout_user
from mlibsite import db
from mlibsite.models import User, Methodics
from mlibsite.users.forms import UpdateUserForm
from mlibsite.users.picture_handler import add_profile_pic

users = Blueprint('users', __name__, template_folder='templates/users')

# register
# login
# logout
# account (update UserForm)
# user's list of Blog posts

##### REGISTER #####
@users.route('/user/register', methods=['GET', 'POST'])
def register():
    return redirect(url_for('/user/login'))

##### LOGIN ######
@users.route('/user/sign-in', methods=['GET', 'POST'])
@login_required
def login():
    return redirect(url_for('core.index'))


##### LOGOUT #####
@users.route('/user/sign-out')
def logout():
    return redirect(url_for('core.index'))


##### ACCOUNT #####
@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateUserForm()

    if form.validate_on_submit():

        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data, username, current_user.profile_image)
            current_user.profile_image = pic

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone_num = form.phone_num.data
        current_user.address = form.address.data
        current_user.curr_job_place = form.curr_job_place.data

        db.session.commit()
        flash('Информация о пользователе обновлена.', 'success')
        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.phone_num.data = current_user.phone_num
        form.address.data = current_user.address
        form.curr_job_place.data = current_user.curr_job_place

    profile_image = url_for('static', filename = 'profile_pics/'+current_user.profile_image)
    return render_template('account.html', profile_image=profile_image, form=form)


##### Методики конкретного автора с выводом постранично #####
@users.route('/<username>')
def user_methodics(username):
    page = request.args.get('page', 1, type=int) # пригодится если страниц дохера, делаем разбивку по страницам
    user = User.query.filter_by(username=username).first_or_404()
    methodics = Methodics.query.filter_by(author=user).order_by(Methodics.publish_date.desc()).paginate(page=page, per_page=6) # Сортируем по уменьшающейся дате, выводим по 5 постов на страницу
    return render_template('user_methodics.html', methodics=methodics, user=user)
