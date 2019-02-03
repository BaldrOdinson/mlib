#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, session, request, redirect, Blueprint, current_app, Markup, abort, send_file
from flask_login import current_user, login_required
from mlibsite import db
from mlibsite.models import Projects, Term, Courses, UserRole, User
from mlibsite.methodics.text_formater import text_format_for_html, date_translate, text_for_markup, text_for_links_markup
from mlibsite.projects.forms import AddProjectForm, UpdateProjectForm, AddTermForm, UpdateTermForm
from mlibsite.projects.picture_handler import add_project_pic, add_term_pic
from mlibsite.projects.files_saver import add_attachment
from datetime import datetime
import json, os, shutil

projects = Blueprint('projects', __name__, template_folder='templates/projects')

##### PROJECTS LIST  #####
@projects.route('/projects_list')
def projects_list():
    '''
    Показываем список существующих проектов
    '''
    # pagination
    per_page=9
    page = request.args.get('page', 1, type=int)
    short_desc_html_list_dict = {}
    projects = Projects.query.order_by(Projects.change_date.desc()).paginate(page=page, per_page=per_page)
    projects_whole = Projects.query.order_by(Projects.change_date.desc())[page*per_page-per_page:page*per_page]
    for project in projects_whole:
        short_desc_html_list_dict[project.id] = text_format_for_html(project.short_desc)
    return render_template('projects_list.html',
                            short_desc_dict=short_desc_html_list_dict,
                            projects=projects,
                            date_translate=date_translate)

##### ADD PROJECT #####
@projects.route('/project', methods=['GET', 'POST'])
@login_required
def create_project():
    """
    Создаем новый проект
    """
    form = AddProjectForm()

    if form.validate_on_submit():
        project = Projects(author_id=current_user.id,
                           name=form.name.data,
                           short_desc=form.short_desc.data)

        db.session.add(project)
        db.session.commit()
        flash('Проект создан', 'success')
        project = Projects.query.filter_by(author_id=current_user.id, name=form.name.data).first()
        return redirect(url_for('projects.update_project', project_id=project.id))
    # Первая загрузка
    return render_template('create_project.html', form=form)


###### UPDATE PROJECT ######
@projects.route('/project_<int:project_id>/project_update', methods=['GET', 'POST'])
@login_required
def update_project(project_id):
    """
    Редактируем и дополняем существующюю запись для проекта project_id
    """
    project = Projects.query.get_or_404(project_id)
    form = UpdateProjectForm()

    session['project_id'] = project.id
    session.pop('method_id', None)

    # Смотрим роли пользователей по проекту
    project_admins = UserRole.query.filter(UserRole.item_type==2, UserRole.item_id==project.id, UserRole.role_type==1).all()
    print(f'project_admins: {list(project.user_id for project in project_admins)}')
    project_moders = db.session.query(UserRole.user_id).filter(UserRole.item_type==2, UserRole.item_id==project.id, UserRole.role_type==2).all()
    print(f'project_moders: {project_moders}')
    # print(f'project_moders: {list(project.user_id for project in project_moders)}')
    project_readers = db.session.query(UserRole.user_id).filter(UserRole.item_type==2, UserRole.item_id==project.id, UserRole.role_type==3).all()
    print(f'project_readers: {project_readers}')


    # Берем из базы пользователей с какими нибудь правами по проекту
    users_role_dict = {}
    roles = UserRole.query.filter(UserRole.item_type==2, UserRole.item_id==project.id).all()
    if roles:
        for role in roles:
            user = User.query.filter_by(id=role.user_id).first()
            user_role = role.role_type
            users_role_dict[user.id] = (user.username, user_role, role.id)
    print(f'users_role_dict: {users_role_dict}')

    if form.validate_on_submit():
        # Если загружается картинка для Проекта
        if form.label_image.data:
            project_id = project.id
            pic = add_project_pic(form.label_image.data, project_id, project.label_image)
            project.label_image = pic
        # Если загружается дополнительный файл
        # формируем общий список, переводим в форма JSON и сохраняем в базу
        if form.attach.data:
            project_id = project.id
            if project.attach:
                attachments_files_list = json.loads(project.attach)
            else:
                attachments_files_list = []
            attachment_filename = add_attachment(form.attach.data, project_id, project.attach)
            attachments_files_list.append(attachment_filename)
            json_attachments = json.dumps(attachments_files_list)
            project.attach = json_attachments

        project.name = form.name.data
        project.change_date = datetime.utcnow()
        project.short_desc = form.short_desc.data
        project.description = form.description.data
        project.contacts_info = form.contacts_info.data
        project.moders_list = form.moders_list.data
        project.address = form.address.data
        project.note = form.note.data
        project.web_links = form.web_links.data

        db.session.commit()
        return redirect(url_for('projects.project_view', project_id=project.id))
    # Первоначальное открытие формы на редактирование
    elif request.method == 'GET':

        form.name.data = project.name
        form.short_desc.data = project.short_desc
        form.description.data = project.description
        form.moders_list.data = project.moders_list
        form.contacts_info.data = project.contacts_info
        form.moders_list.data = project.moders_list
        form.address.data = project.address
        form.note.data = project.note
        form.web_links.data = project.web_links

    label_image = url_for('static', filename = 'projects_pics/project_ava/'+project.label_image)
    # Формируем список с прикрепленными файлами
    attachments = []
    if project.attach:
        for attachment in json.loads(project.attach):
            attachments.append(attachment)
    # Если форма заполненна с ошибками, а валидаторам плевать (например расширения файлов)
    # print(f'form errors: {form.errors}')
    if form.errors:
        flash_text = 'Форма методики заполнена неверно. <br>'
        for error in form.errors:
            # print(form.errors[error])
            flash_text += form.errors[error][0]
        flash_text += 'К сожалению, последние изменения не сохранены. '
        flash(Markup(flash_text), 'negative')
    return render_template('update_project.html',
                            label_image=label_image,
                            project_id = project.id,
                            form=form,
                            attachments=attachments,
                            users_role_dict = users_role_dict)


###### PROJECT (VIEW) ######
@projects.route('/project_<int:project_id>')  # <int: - для того чтобы номер методики точно был integer
def project_view(project_id):
    # Получаем из базы метод, тайминг занятия, этапы занятия
    project = Projects.query.get_or_404(project_id)
    # Формируем список модераторов
    moder_stat = False
    if project.moders_list:
        moders_list = text_format_for_html(project.moders_list)
        if current_user.id in moders_list:
            moder_stat = True
    # print(f'Moder: {moder_stat}\nModers_list: {moders_list}\nUser_id: {current_user.id}')

    # разделяем преформатированный текст на строки, так как переносы не обрабатываются
    description_html=Markup(text_for_markup(project.description))
    short_desc_html=Markup(text_for_markup(project.short_desc))
    contacts_info_html=Markup(text_for_markup(project.contacts_info))
    address_html=Markup(text_for_markup(project.address))
    note_html=Markup(text_for_markup(project.note))
    web_links_html=Markup(text_for_links_markup(project.web_links))
    # Формируем список с файлами презентаций, достаем из базы список в JSON и переводим его в нормальный
    attachments = []
    if project.attach:
        for attachment in json.loads(project.attach):
            attachments.append(attachment)
    return render_template('project.html',
                            project = project,
                            description=description_html,
                            short_desc=short_desc_html,
                            contacts_info = contacts_info_html,
                            address = address_html,
                            note = note_html,
                            web_links = web_links_html,
                            attachments = attachments,
                            moder_stat = moder_stat,
                            label_image=project.label_image,
                            date_translate=date_translate)


###### DELETE PROJECT ######
@projects.route('/project_<int:project_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_project(project_id):
    project = Projects.query.get_or_404(project_id)
    # Формируем список модераторов
    moder_stat = False
    if project.moders_list:
        moders_list = text_format_for_html(project.moders_list)
        if current_user.id in moders_list:
            moder_stat = True
    if ((project.author_id != current_user) and (current_user.username != 'Administrator') and not moder_stat):
        abort(403)
    # Удаляем заглавную картинку для проекта
    if project.label_image != 'default_project.png':
        del_project_ava = os.path.join(current_app.root_path, os.path.join('static', 'projects_pics', 'project_ava', project.label_image))
        os.remove(del_project_ava)
    # Удаляем прикрепленные файлы
    if project.attach:
        for attachment in json.loads(project.attach):
            filename = attachment
            curr_folder_path = os.path.join('static', 'project_attachments')
            directory = os.path.join(current_app.root_path, curr_folder_path, 'project_'+str(project_id))
            shutil.rmtree(directory, ignore_errors=True)
    # Удалние проекта, после того как разобрались с констреинтами
    db.session.delete(project)
    db.session.commit()
    flash('Проект удален', 'success')
    return redirect(url_for('projects.projects_list'))


##### DOWNLOAD ATTACHMENT #####
@projects.route('/project_<int:project_id>/download')
def download_attachment(project_id):
    """
    Скачиваем прикрепленный файл для выбранного проекта
    """
    attachment = request.args.get('attachment')
    filename = attachment
    curr_folder_path = os.path.join('static', 'project_attachments')
    directory = os.path.join(current_app.root_path, curr_folder_path, 'project_'+str(project_id))
    filepath = os.path.join(directory, filename)
    return send_file(filepath, attachment_filename=filename, as_attachment=True)

##### DELETE ATTACHMENT #####
@projects.route('/project_<int:project_id>/attachment_delete')
def delete_attachment(project_id):
    """
    Удаляем прикрепленный файл для выбранного проекта
    """
    project = Projects.query.get_or_404(project_id)
    # Формируем список модераторов
    moder_stat = False
    if project.moders_list:
        moders_list = text_format_for_html(project.moders_list)
        if current_user.id in moders_list:
            moder_stat = True
    attachment = request.args.get('attachment')
    if ((project.author_id != current_user) and (current_user.username != 'Administrator') and not moder_stat):
        abort(403)
    filename = attachment
    curr_folder_path = os.path.join('static', 'project_attachments')
    directory = os.path.join(current_app.root_path, curr_folder_path, 'project_'+str(project_id))
    curr_filepath = os.path.join(current_app.root_path, directory, filename)
    os.remove(curr_filepath)
    if len(os.listdir(directory)) == 0:
        shutil.rmtree(directory, ignore_errors=True)
        project.attach = None
        db.session.commit()
    else:
        if project.attach:
            attachments = json.loads(project.attach)
            attachments.remove(filename)
            project.attach = json.dumps(attachments)
            db.session.commit()
    flash('Прикрепленный к проекту файл удален', 'warning')
    # filepath = os.path.join(directory, filename)
    return redirect(url_for('projects.update_project', project_id=project_id))


####################### TERM ######################

##### TERM LIST  #####
@projects.route('/project_<int:project_id>/term')
def term_list(project_id):
    '''
    Показываем список периодов занятий в проекте (семестры, четверти, смены)
    '''
    project = Projects.query.get_or_404(project_id)
    # pagination
    # Максимальное количество элементов на странице
    per_page=15
    page = request.args.get('page', 1, type=int)
    description_html_list_dict = {}
    term_set = Term.query.filter_by(project_id=project.id).order_by(Term.start_date.desc()).paginate(page=page, per_page=per_page)
    term_whole = Term.query.filter_by(project_id=project.id).order_by(Term.start_date.desc())[page*per_page-per_page:page*per_page]
    for term in term_whole:
        # description_html_list_dict[term.id] = text_format_for_html(term.description)
        description_html_list_dict[term.id] = Markup(text_for_markup(term.description))
    return render_template('projects_term.html',
                            description_dict=description_html_list_dict,
                            term_set=term_set,
                            project_name = project.name,
                            project_id = project.id,
                            label_image = project.label_image,
                            date_translate=date_translate)

##### ADD TERM #####
@projects.route('/project_<int:project_id>/add_term', methods=['GET', 'POST'])
@login_required
def create_term(project_id):
    """
    Создаем новый период занятий для проекта
    """
    project = Projects.query.get_or_404(project_id)
    form = AddTermForm()

    if form.validate_on_submit():
        term = Term(project_id=project.id,
                    name=form.name.data,
                    description=form.description.data,
                    start_date=form.start_date.data,
                    finish_date=form.finish_date.data)

        db.session.add(term)
        db.session.commit()
        flash('Период деятельности проекта создан', 'success')
        term = Term.query.filter_by(project_id=project.id, name=form.name.data).first()
        return redirect(url_for('projects.update_term', term_id=term.id))
    # Первая загрузка
    return render_template('create_term.html',
                                form=form,
                                project_name=project.name,
                                project_id=project.id)


###### UPDATE TERM ######
@projects.route('/update_term_<int:term_id>', methods=['GET', 'POST'])
@login_required
def update_term(term_id):
    """
    Изменяем созданный период. Добавляется изменение картинки
    """
    term = Term.query.get_or_404(term_id)
    project = Projects.query.get_or_404(term.project_id)
    form = UpdateTermForm()

    if form.validate_on_submit():
        # Если загружается картинка для Периода
        print(f'Новая каритнка: {form.label_image.data}')
        if form.label_image.data:
            project_id = term.project_id
            pic = add_term_pic(form.label_image.data, term_id, term.label_image)
            term.label_image = pic

        term.name = form.name.data
        term.description = form.description.data
        term.start_date = form.start_date.data
        term.finish_date = form.finish_date.data

        db.session.commit()
        return redirect(url_for('projects.term_view', term_id=term.id))
    # первоначальная загрузка
    elif request.method == 'GET':
        form.name.data = term.name
        form.description.data = term.description
        form.start_date.data = term.start_date
        form.finish_date.data = term.finish_date

    label_image = url_for('static', filename = 'projects_pics/project_term/'+term.label_image)
    # Если форма заполненна с ошибками, а валидаторам плевать
    if form.errors:
        flash_text = 'Форма методики заполнена неверно. <br>'
        for error in form.errors:
            flash_text += form.errors[error][0]
        flash_text += 'К сожалению, последние изменения не сохранены. '
        flash(Markup(flash_text), 'negative')
    return render_template('update_term.html',
                            label_image=label_image,
                            project_name = project.name,
                            form=form)


###### TERM (VIEW) ######
@projects.route('/term_<int:term_id>')  # <int: - для того чтобы номер методики точно был integer
def term_view(term_id):
    term = Term.query.get_or_404(term_id)
    project = Projects.query.get_or_404(term.project_id)
    # COURSES with pagination
    per_page=10
    page = request.args.get('page', 1, type=int)
    description_html_dict = {}
    tutors_html_dict = {}
    courses = Courses.query.filter_by(term_id=term.id).order_by(Courses.start_date.desc()).paginate(page=page, per_page=per_page)
    courses_whole = Courses.query.filter_by(term_id=term.id).order_by(Courses.start_date.desc())[page*per_page-per_page:page*per_page]
    for course in courses_whole:
        description_html_dict[course.id] = Markup(text_for_markup(course.description))
        tutors_html_dict[course.id] = Markup(text_for_markup(course.tutors))

    # разделяем преформатированный текст на строки, так как переносы не обрабатываются
    description_html=Markup(text_for_markup(term.description))
    return render_template('term.html',
                            term = term,
                            project = project,
                            description = description_html,
                            date_translate=date_translate,
                            courses = courses,
                            courses_description = description_html_dict,
                            courses_tutors=tutors_html_dict)


###### DELETE TERM ######
@projects.route('/term_<int:term_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_term(term_id):
    term = Term.query.get_or_404(term_id)
    project = Projects.query.get_or_404(term.project_id)
    # Формируем список модераторов
    moder_stat = False
    if project.moders_list:
        moders_list = text_format_for_html(project.moders_list)
        if current_user.id in moders_list:
            moder_stat = True
    if ((project.author_id != current_user) and (current_user.username != 'Administrator') and not moder_stat):
        abort(403)
    # Удаляем заглавную картинку для проекта
    if term.label_image != 'default_term.png':
        del_project_term = os.path.join(current_app.root_path, os.path.join('static', 'projects_pics', 'project_term', term.label_image))
        os.remove(del_project_term)
    # Удалние проекта, после того как разобрались с констреинтами
    db.session.delete(term)
    db.session.commit()
    flash('Период проект удален', 'success')
    return redirect(url_for('projects.term_list', project_id=project.id))
