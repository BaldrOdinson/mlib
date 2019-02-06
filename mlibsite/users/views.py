#! /usr/bin/env python
# -*- coding: utf-8 -*-

#user's views
from flask import render_template, url_for, flash, session, redirect, request, Blueprint, Markup
from flask_user import current_user, login_required
# from flask_login import logout_user
from mlibsite import db
from mlibsite.models import User, Methodics, Projects, UserRole
from mlibsite.users.forms import UpdateUserForm, SearchUserForm, AddUserRoleForm
from mlibsite.users.picture_handler import add_profile_pic
from mlibsite.methodics.text_formater import date_translate, text_format_for_html
from sqlalchemy import or_

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
    per_page=6
    page = request.args.get('page', 1, type=int) # пригодится если страниц дохера, делаем разбивку по страницам
    short_desc_html_list_dict = {}
    user = User.query.filter_by(username=username).first_or_404()
    methodics = Methodics.query.filter_by(author=user).order_by(Methodics.change_date.desc()).paginate(page=page, per_page=6) # Сортируем по уменьшающейся дате, выводим по 5 постов на страницу
    methodics_whole = Methodics.query.filter_by(author=user).order_by(Methodics.change_date.desc())[page*per_page-per_page:page*per_page]
    for method in methodics_whole:
        short_desc_html_list_dict[method.id] = text_format_for_html(method.short_desc)
    return render_template('user_methodics.html', methodics=methodics,
                                                user=user,
                                                date_translate=date_translate,
                                                short_desc_dict=short_desc_html_list_dict)


###### SEARCH USER ######
@users.route('/search_user', methods=['GET', 'POST'])  # <int: - для того чтобы номер методики точно был integer
@login_required
def search_user():
    # Опрелеляем номер списка для текущего курса и остальные параметры
    if 'project_id' in session:
            project_id = session['project_id']
            project = Projects.query.get_or_404(project_id)
    elif 'method_id' in session:
            method_id = session['method_id']
            method = Methodics.query.get_or_404(method_id)

    form = SearchUserForm()

    if form.validate_on_submit():
        # Формируем параметры поиска на основе указанных пользователем
        selected_users_dict = {}
        if form.email.data:
            selected_users_dict['email'] = '%'+form.email.data+'%'
        else: selected_users_dict['email'] = '%'
        if form.username.data:
            selected_users_dict['username'] = '%'+form.username.data+'%'
        else: selected_users_dict['username'] = '%'
        if form.first_name.data:
            selected_users_dict['first_name'] = '%'+form.first_name.data+'%'
        else: selected_users_dict['first_name'] = '%'
        if form.last_name.data:
            selected_users_dict['last_name'] = '%'+form.last_name.data+'%'
        else: selected_users_dict['last_name'] = '%'
        if form.phone_num.data:
            selected_users_dict['phone_num'] = '%'+form.phone_num.data+'%'
        else: selected_users_dict['phone_num'] = '%'
        if form.address.data:
            selected_users_dict['address'] = '%'+form.address.data+'%'
        else: selected_users_dict['address'] = '%'
        if form.curr_job_place.data:
            selected_users_dict['curr_job_place'] = '%'+form.curr_job_place.data+'%'
        else: selected_users_dict['curr_job_place'] = '%'

        print(f'selected_users_dict: {selected_users_dict}')
        session['selected_users_dict'] = selected_users_dict
        return redirect(url_for('users.selected_users_list'))

    # первоначальная загрузка формы поиска
    elif request.method == 'GET':
        pass
    # Если форма заполненна с ошибками, а валидаторам плевать
    if form.errors:
        flash_text = 'Форма поиска заполнена неверно. <br>'
        print(f'form errors: {form.errors}')
        for error in form.errors:
            flash_text += form.errors[error][0]
        # flash_text += '<br>К сожалению, последние изменения не сохранены. '
        flash(Markup(flash_text), 'negative')
    # Первоначальные поисковые параметры
    if 'project_id' in session:
            return render_template('search_user.html',
                                    project=project,
                                    form=form)
    elif 'method_id' in session:
                return render_template('search_user.html',
                                        method=method,
                                        form=form)
    else:
            return render_template('search_user.html',
                                    form=form)


###### SELECTED USERS LIST ######
@users.route('/selected_users')  # <int: - для того чтобы номер методики точно был integer
@login_required
def selected_users_list():
    selected_users_dict = session['selected_users_dict']
    print(f'selected_users_dict: {selected_users_dict}')

    selected_users = User.query.filter(
                            or_(User.email.ilike(selected_users_dict['email']), (User.email==None)),
                            User.username.ilike(selected_users_dict['username']),
                            or_(User.first_name.ilike(selected_users_dict['first_name']), (User.first_name==None)),
                            or_(User.last_name.ilike(selected_users_dict['last_name']), (User.last_name==None)),
                            or_(User.phone_num.ilike(selected_users_dict['phone_num']), (User.phone_num==None)),
                            or_(User.address.ilike(selected_users_dict['address']), (User.address==None)),
                            or_(User.curr_job_place.ilike(selected_users_dict['curr_job_place']), (User.curr_job_place==None))
                            ).order_by(User.username)

    print(f'selected_users: {selected_users}')
    # pagination
    # Максимальное количество элементов на странице
    per_page=15
    page = request.args.get('page', 1, type=int)
    user_set = selected_users.paginate(page=page, per_page=per_page)
    user_whole = selected_users[page*per_page-per_page:page*per_page]
    if 'project_id' in session:
        project_id = session['project_id']
        project = Projects.query.get_or_404(project_id)
        return render_template('selected_users.html',
                            user_set=user_set,
                            project_id = project_id,
                            project = project,
                            date_translate=date_translate)
    elif 'method_id' in session:
        method_id = session['method_id']
        method = Methodics.query.get_or_404(method_id)
        return render_template('selected_users.html',
                            user_set=user_set,
                            method_id = method_id,
                            method = method,
                            date_translate=date_translate)


##### CREATE USER ROLE #####
@users.route('/user_<int:user_id>/add_role', methods=['GET', 'POST'])
@login_required
def create_user_role(user_id):
    """
    Создаем пользователю новую роль
    """
    user = User.query.get_or_404(user_id)
    # Достаем из реквеста текущие параметры для роли
    item_id = request.args.get('item_id', 1, type=int)
    item_type = request.args.get('item_type', 1, type=int)
    if item_type == 2:
        project = Projects.query.get_or_404(item_id)
        item_type_desc = 'project'
        item_name = project.name
    elif item_type == 1:
        method = Methodics.query.get_or_404(item_id)
        item_type_desc = 'method'
        item_name = method.title
    form = AddUserRoleForm()

    if form.validate_on_submit():
        selected_role_type = int(request.form.get('form_role_type'))
        print(f'selected role: {selected_role_type}')
        if selected_role_type == 1:
            role_type_desc = 'admin'
        elif selected_role_type == 2:
            role_type_desc = 'moder'
        elif selected_role_type == 3:
            role_type_desc = 'full_view'

        # Производим необходимые манипуляции с ролью, создаем или изменяем, проверяем на дубликаты
        same_role = UserRole.query.filter(UserRole.user_id==user_id, UserRole.item_type==item_type, UserRole.item_id==item_id, UserRole.role_type==selected_role_type).first()
        current_role = UserRole.query.filter(UserRole.user_id==user_id, UserRole.item_type==item_type, UserRole.item_id==item_id).first()
        # Если для выбранного пользователя уже есть такая же роль для данного проекта/методики
        if same_role:
            flash('У выбранного пользователя уже есть такая роль. Проверьте указанные вами параметры', 'warning')
        # Если у пользователя уже есть другая роль для данного проекта/методики
        elif current_role:
            current_role.role_type = selected_role_type
            current_role.role_type_desc = role_type_desc
            db.session.commit()
            flash('Роль пользователя изменена', 'success')
        # Если никакой роли нет, то создаем новую запись
        else:
            user_role = UserRole(user_id=user_id,
                        item_id = item_id,
                        item_type = item_type,
                        item_type_desc = item_type_desc,
                        role_type = selected_role_type,
                        role_type_desc = role_type_desc)

            db.session.add(user_role)
            db.session.commit()
            flash('Пользователю добавлена выбранна роль', 'success')
        if item_type == 2:
            return redirect(url_for('projects.update_project', project_id=project.id))
        if item_type == 1:
            return redirect(url_for('methodics.update', method_id=method.id))
    # Первая загрузка
    return render_template('select_role.html',
                                user=user,
                                form=form,
                                item_type_desc=item_type_desc,
                                item_id=item_id,
                                item_name=item_name)


##### DELETE USER ROLE #####
@users.route('/delete_role_<int:role_id>', methods=['GET', 'POST'])
@login_required
def delete_user_role(role_id):
    role = UserRole.query.get_or_404(role_id)
    item_id = request.args.get('item_id', 1, type=int)
    item_type = request.args.get('item_type', 1, type=int)
    db.session.delete(role)
    db.session.commit()
    flash('Роль пользователя удалена', 'success')
    if item_type == 2:
        return redirect(url_for('projects.update_project', project_id=item_id))
    elif item_type == 1:
        return redirect(url_for('methodics.update', method_id=item_id))
