#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, request, redirect, session, Blueprint, current_app, Markup, abort, send_file
from flask_login import current_user, login_required
from mlibsite import db
from mlibsite.models import Courses, Lessons, Term, Projects, Students, StudentsGroup, Learning_groups, UserRole
from mlibsite.methodics.text_formater import text_format_for_html, date_translate, text_for_markup
from mlibsite.students.forms import AddStudentForm, UpdateStudentForm, AddStudentsGroupForm, UpdateStudentsGroupForm, SearchStudentForm
from mlibsite.students.picture_handler import add_student_pic
from mlibsite.students.files_saver import add_attachment
from mlibsite.students.db_query_func import student_projects_info_dict
from mlibsite.users.user_roles import get_roles, user_role
from sqlalchemy import text
import json, os, shutil

students = Blueprint('students', __name__, template_folder='templates/students')


##### ADD STUDENTS GROUP #####
@students.route('/course_<int:course_id>/create_students_group', methods=['GET', 'POST'])
@login_required
def create_students_group(course_id):
    """
    Создаем новую группу участников курса
    """
    course = Courses.query.get_or_404(course_id)
    term = term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)

    ##### РОЛЬ ДОСТУПА #####
    # Смотрим роли пользователей по проекту
    project_roles = get_roles(item_id=project.id, item_type=2)
    # определяем роль пользователя
    curr_user_role = user_role(project_roles, current_user.id)
    # завершаем обработку если у пользователя не хватает прав
    if not ((curr_user_role in ['admin', 'moder'])
                or (current_user.username == 'Administrator')
                or (current_user.id == project.author_id)):
        abort(403)

    form = AddStudentsGroupForm()

    if form.validate_on_submit():
        students_group = StudentsGroup(author_id=current_user.id,
                                        description=form.description.data)

        db.session.add(students_group)
        db.session.commit()
        flash('Новая группа участников создана', 'success')
        students_group = StudentsGroup.query.filter_by(author_id=current_user.id, description=form.description.data).order_by(StudentsGroup.create_date.desc()).first()
        course.students_group_id = students_group.id
        db.session.commit()
        return redirect(url_for('courses.course_view', course_id=course.id))
    # Первая загрузка
    return render_template('create_students_group.html',
                            form=form,
                            course_name=course.name,
                            course_id=course.id,
                            term=term,
                            project=project,
                            course_label_image=course.label_image)


##### RENAME STUDENTS GROUP #####
@students.route('/course_<int:course_id>/rename_students_group', methods=['GET', 'POST'])
@login_required
def rename_students_group(course_id):
    """
    Переименовываем группу участников курса
    """
    course = Courses.query.get_or_404(course_id)
    term = term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)
    students_group = StudentsGroup.query.get_or_404(course.students_group_id)

    ##### РОЛЬ ДОСТУПА #####
    # Смотрим роли пользователей по проекту
    project_roles = get_roles(item_id=project.id, item_type=2)
    # определяем роль пользователя
    curr_user_role = user_role(project_roles, current_user.id)
    # завершаем обработку если у пользователя не хватает прав
    if not ((curr_user_role in ['admin', 'moder'])
                or (current_user.username == 'Administrator')
                or (current_user.id == project.author_id)):
        abort(403)

    form = UpdateStudentsGroupForm()

    if form.validate_on_submit():
        students_group.description = form.description.data

        db.session.commit()
        flash('Группа участников курса переименована', 'success')
        return redirect(url_for('courses.course_view', course_id=course.id))
    # Первая загрузка
    form.description.data = students_group.description
    return render_template('rename_students_group.html',
                            form=form,
                            course_name=course.name,
                            course_id=course.id,
                            term=term,
                            project=project,
                            course_label_image=course.label_image)



##### UPDATE STUDENTS GROUP LIST #####
@students.route('/course_group_<int:course_id>/update_students_group_list', methods=['GET', 'POST'])
@login_required
def update_students_group_list(course_id):
    """
    Изменяем состав группы участников курса
    """
    session['course_id'] = course_id
    course = Courses.query.get_or_404(course_id)
    term = term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)

    ##### РОЛЬ ДОСТУПА #####
    # Смотрим роли пользователей по проекту
    project_roles = get_roles(item_id=project.id, item_type=2)
    # определяем роль пользователя
    curr_user_role = user_role(project_roles, current_user.id)
    # завершаем обработку если у пользователя не хватает прав
    if not ((curr_user_role in ['admin', 'moder'])
                or (current_user.username == 'Administrator')
                or (current_user.id == project.author_id)):
        abort(403)

    students_group = StudentsGroup.query.get_or_404(course.students_group_id)
    students_group_list = []
    learning_group = Learning_groups.query.filter_by(group_id=course.students_group_id)
    for student in learning_group:
        students_group_list.append(Students.query.filter_by(id=student.student_id).first())
    return render_template('students_group_list.html',
                            group_name=students_group.description,
                            group_id=students_group.id,
                            students_group_list=students_group_list,
                            course_id=course.id,
                            course_name=course.name,
                            term=term,
                            project=project,
                            course_label_image=course.label_image,
                            zip=zip,
                            len=len)


##### CREATE STUDENT #####
@students.route('/create_new_student_for_course_<int:course_id>', methods=['GET', 'POST'])
@login_required
def create_student(course_id):
    """
    Создаем запись для нового студента
    """
    course = Courses.query.get_or_404(course_id)
    term = term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)
    student_group = StudentsGroup.query.get_or_404(course.students_group_id)

    ##### РОЛЬ ДОСТУПА #####
    # Смотрим роли пользователей по проекту
    project_roles = get_roles(item_id=project.id, item_type=2)
    # определяем роль пользователя
    curr_user_role = user_role(project_roles, current_user.id)
    # завершаем обработку если у пользователя не хватает прав
    if not ((curr_user_role in ['admin', 'moder'])
                or (current_user.username == 'Administrator')
                or (current_user.id == project.author_id)):
        abort(403)

    form = AddStudentForm()

    if form.validate_on_submit():
        student = Students(first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            age=form.age.data)

        db.session.add(student)
        db.session.commit()
        flash('Новый участник создан', 'success')
        student = Students.query.filter_by(first_name=form.first_name.data, last_name=form.last_name.data).order_by(Students.create_date.desc()).first()
        group_id = course.students_group_id
        add_to_group = Learning_groups(group_id=group_id,
                                        student_id=student.id,
                                        course_id=course.id,
                                        term_id=term.id,
                                        project_id=project.id)
        db.session.add(add_to_group)
        db.session.commit()
        return redirect(url_for('students.update_student', student_id=student.id))
    # Первая загрузка
    # Если форма заполненна с ошибками, а валидаторам плевать (например расширения файлов)
    # print(f'form errors: {form.errors}')
    if form.errors:
        flash_text = 'Форма методики заполнена неверно. <br>'
        for error in form.errors:
            # print(form.errors[error])
            flash_text += form.errors[error][0] + '<br>'
        flash_text += 'К сожалению, последние изменения не сохранены. '
        flash(Markup(flash_text), 'negative')
    return render_template('create_student.html',
                            form=form,
                            term=term,
                            project=project,
                            student_group=student_group.description,
                            student_group_id=student_group.id,
                            course=course)


###### UPDATE STUDENT ######
@students.route('/update_student_<int:student_id>', methods=['GET', 'POST'])
@login_required
def update_student(student_id):
    """
    Изменяем профайл студента
    """
    student = Students.query.get_or_404(student_id)
    student_proj_info_dict = student_projects_info_dict(student_id)

    ##### РОЛЬ ДОСТУПА #####
    # Проверяем есть ли у пользователя хоть в одном проекте участника права подходящие для редактирования
    students_projects=student_proj_info_dict['students_projects']
    allow_flag = False
    for project in students_projects:
        # Смотрим роли пользователей по проекту
        project_roles = get_roles(item_id=project.id, item_type=2)
        # определяем роль пользователя
        curr_user_role = user_role(project_roles, current_user.id)
        # завершаем обработку если у пользователя не хватает прав
        if ((curr_user_role in ['admin', 'moder'])
                    or (current_user.username == 'Administrator')
                    or (current_user.id == project.author_id)):
            allow_flag = True
    if not allow_flag:
        abort(403)

    form = UpdateStudentForm()

    if form.validate_on_submit():
        # Если загружается картинка для участника
        if form.avatar.data:
            student_id = student.id
            pic = add_student_pic(form.avatar.data, student.id, student.avatar)
            student.avatar = pic
        # Если загружается дополнительный файл
        # формируем общий список, переводим в форма JSON и сохраняем в базу
        if form.attach.data:
            student_id = student.id
            if student.attach:
                attachments_files_list = json.loads(student.attach)
            else:
                attachments_files_list = []
            attachment_filename = add_attachment(form.attach.data, student_id, student.attach)
            attachments_files_list.append(attachment_filename)
            json_attachments = json.dumps(attachments_files_list)
            student.attach = json_attachments
        # Формируем словарь типов документов
        if student.document_dict:
            document_dict = json.loads(student.document_dict)
        else:
            document_dict = {}
        document_dict['Тип документа'] = 'Номер документа'
        json_documents = json.dumps(document_dict)
        student.document_dict = json_documents

        student.first_name = form.first_name.data
        student.last_name = form.last_name.data
        student.age = form.age.data
        student.birthday = form.birthday.data
        student.sex = form.sex.data
        student.phone_num = form.phone_num.data
        student.email = form.email.data
        student.address = form.address.data
        student.note = form.note.data

        db.session.commit()
        print(f'session: {session}')
        course_id = session['course_id']
        return redirect(url_for('students.update_students_group_list', course_id=course_id))
    # первоначальная загрузка
    elif request.method == 'GET':
        form.first_name.data = student.first_name
        form.last_name.data = student.last_name
        form.age.data = student.age
        form.birthday.data = student.birthday
        form.sex.data = student.sex
        form.phone_num.data = student.phone_num
        form.email.data = student.email
        form.address.data = student.address
        form.note.data = student.note

    avatar = url_for('static', filename = 'students_pics/students_ava/'+student.avatar)
    # Формируем список с прикрепленными файлами
    attachments = []
    if student.attach:
        for attachment in json.loads(student.attach):
            attachments.append(attachment)
    # Разбираемся о соловарем документов
    document_dict = {}
    if student.document_dict:
        document_dict = json.loads(student.document_dict)
    # Если форма заполненна с ошибками, а валидаторам плевать
    if form.errors:
        flash_text = 'Форма курса заполнена неверно. <br>'
        print(f'form errors: {form.errors}')
        for error in form.errors:
            flash_text += form.errors[error][0]
        flash_text += '<br>К сожалению, последние изменения не сохранены. '
        flash(Markup(flash_text), 'negative')
    return render_template('update_student.html',
                            student = student,
                            students_group=student_proj_info_dict['students_group'],
                            students_courses = student_proj_info_dict['students_courses'],
                            students_terms = student_proj_info_dict['students_terms'],
                            form=form,
                            students_projects=student_proj_info_dict['students_projects'],
                            document_dict = document_dict,
                            zip=zip,
                            attachments=attachments,
                            allow_flag=allow_flag)


###### STUDENT (VIEW) ######
@students.route('/student_<int:student_id>')  # <int: - для того чтобы номер методики точно был integer
def student_view(student_id):
    # Получаем из базы всю инфу свзанную со студентом
    student = Students.query.get_or_404(student_id)
    student_proj_info_dict = student_projects_info_dict(student_id)

    ##### РОЛЬ ДОСТУПА #####
    # Проверяем есть ли у пользователя хоть в одном проекте участника права подходящие для просмотра
    students_projects=student_proj_info_dict['students_projects']
    allow_flag = False
    for project in students_projects:
        # Смотрим роли пользователей по проекту
        project_roles = get_roles(item_id=project.id, item_type=2)
        # определяем роль пользователя
        curr_user_role = user_role(project_roles, current_user.id)
        # завершаем обработку если у пользователя не хватает прав
        if ((curr_user_role in ['admin', 'moder', 'reader'])
                    or (current_user.username == 'Administrator')
                    or (current_user.id == project.author_id)):
            allow_flag = True
    if not allow_flag:
        abort(403)

    # разделяем преформатированный текст на строки, так как переносы не обрабатываются
    address_html=Markup(text_for_markup(student.address))
    note_html=Markup(text_for_markup(student.note))
    # Формируем список с файлами презентаций, достаем из базы список в JSON и переводим его в нормальный
    attachments = []
    if student.attach:
        for attachment in json.loads(student.attach):
            attachments.append(attachment)
    return render_template('student.html',
                            student = student,
                            students_group=student_proj_info_dict['students_group'],
                            students_courses = student_proj_info_dict['students_courses'],
                            students_terms = student_proj_info_dict['students_terms'],
                            students_projects=student_proj_info_dict['students_projects'],
                            attachments = attachments,
                            allow_flag=allow_flag,
                            address = address_html,
                            note = note_html,
                            date_translate=date_translate,
                            zip=zip)


###### SELECT STUDENT ######
@students.route('/select_student', methods=['GET', 'POST'])  # <int: - для того чтобы номер методики точно был integer
def search_student():
    # Опрелеляем номер списка для текущего курса и остальные параметры
    if session['course_id']:
        course_id = session['course_id']
        course = Courses.query.filter_by(id=course_id).first()
        group_id = course.students_group_id
        term_id = course.term_id
        project_id = course.project_id

        term = term = Term.query.get_or_404(term_id)
        project = Projects.query.get_or_404(project_id)
        student_group = StudentsGroup.query.get_or_404(group_id)

    form = SearchStudentForm()

    if form.validate_on_submit():
        # Формируем параметры поиска на основе указанных пользователем
        selected_students_dict = {}
        if form.first_name.data:
            selected_students_dict['first_name'] = '%'+form.first_name.data+'%'
        else: selected_students_dict['first_name'] = '%'
        if form.last_name.data:
            selected_students_dict['last_name'] = '%'+form.last_name.data+'%'
        else: selected_students_dict['last_name'] = '%'
        if form.age.data:
            selected_students_dict['age'] = form.age.data
        else: selected_students_dict['age'] = '%'
        # if form.birthday.data:
        #     selected_students_dict['birthday'] = form.birthday.data
        # else: selected_students_dict['birthday'] = '%'
        if form.phone_num.data:
            selected_students_dict['phone_num'] = '%'+form.phone_num.data+'%'
        else: selected_students_dict['phone_num'] = '%'
        if form.email.data:
            selected_students_dict['email'] = '%'+form.email.data+'%'
        else: selected_students_dict['email'] = '%'
        if form.address.data:
            selected_students_dict['address'] = '%'+form.address.data+'%'
        else: selected_students_dict['address'] = '%'

        print(f'selected_students_dict: {selected_students_dict}')
        session['selected_students_dict'] = selected_students_dict
        return redirect(url_for('students.selected_students_list'))

    # первоначальная загрузка формы поиска
    elif request.method == 'GET':
        pass
    # Если форма заполненна с ошибками, а валидаторам плевать
    if form.errors:
        flash_text = 'Форма курса заполнена неверно. <br>'
        print(f'form errors: {form.errors}')
        for error in form.errors:
            flash_text += form.errors[error][0]
        flash_text += '<br>К сожалению, последние изменения не сохранены. '
        flash(Markup(flash_text), 'negative')
    # Первоначальные поисковые параметры
    if session['course_id']:
        return render_template('search_student.html',
                                project = project,
                                term = term,
                                course=course,
                                form=form)
    else:
        return render_template('search_student.html')


###### SELECTED STUDENTS LIST ######
@students.route('/selected_students')  # <int: - для того чтобы номер методики точно был integer
def selected_students_list():

    ##### РОЛЬ ДОСТУПА #####
    # Проверяем есть ли у пользователя хоть в одном проекте права подходящие для просмотра участников
    user_projects_roles = UserRole.query.filter(UserRole.item_type==2, UserRole.user_id==current_user.id).all()
    users_projects = list(users_project.item_id for users_project in user_projects_roles)
    # созданные пользователем проекты
    created_projects = Projects.query.filter(Projects.author_id==current_user.id).all()
    for project in created_projects:
        # список с номерами всех проектов
        users_projects.append(project.id)
    allow_flag = False
    projects_list = []
    for project_id in users_projects:
        projects_list.append(project_id)
        project = Projects.query.filter_by(id=project_id).first()
        # Смотрим роли пользователей по проекту
        project_roles = get_roles(item_id=project.id, item_type=2)
        # определяем роль пользователя
        curr_user_role = user_role(project_roles, current_user.id)
        # завершаем обработку если у пользователя не хватает прав
        if ((curr_user_role in ['admin', 'moder', 'reader'])
                    or (current_user.username == 'Administrator')
                    or (current_user.id == project.author_id)):
            allow_flag = True
    if not allow_flag:
        abort(403)

    # print('BEGIN of selected_students_list')
    # selected_students = request.args.get('selected_students')
    selected_students_dict = session['selected_students_dict']
    selected_students = Students.query.filter(Students.first_name.ilike(selected_students_dict['first_name']),
                                    Students.last_name.ilike(selected_students_dict['last_name']),
                                    Students.phone_num.like(selected_students_dict['phone_num']),
                                    Students.email.like(selected_students_dict['email']),
                                    Students.address.ilike(selected_students_dict['address']),
                                    Students.age.ilike(selected_students_dict['age']),
                                    # Выбираются только студенты, на просмотр которых есть права
                                    Students.id.in_(list(item.student_id for item in (Learning_groups.query.filter(Learning_groups.project_id.in_(users_projects)).all()))),
                                    ).order_by(Students.id.desc())

    print(f'selected_students: {selected_students}')
    # pagination
    # Максимальное количество элементов на странице
    per_page=15
    page = request.args.get('page', 1, type=int)
    student_set = selected_students.paginate(page=page, per_page=per_page)
    student_whole = selected_students[page*per_page-per_page:page*per_page]
    if session['course_id']:
        course_id = session['course_id']
        course = Courses.query.get_or_404(course_id)
        return render_template('selected_students.html',
                            student_set=student_set,
                            course_id = course_id,
                            course = course,
                            date_translate=date_translate)


###### ADD STUDENT TO GROUP LIST ######
@students.route('/course_<int:course_id>/add_student_<int:student_id>')  # <int: - для того чтобы номер методики точно был integer
def add_student_to_list(course_id, student_id):
    course = Courses.query.get_or_404(course_id)
    term = term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)
    group_id = course.students_group_id
    if Learning_groups.query.filter_by(group_id=group_id, student_id=student_id).all():
        flash('Выбранный участник уже итак в списке. Для добавления выберите кого-то другого.', 'negative')
        return redirect(url_for('students.update_students_group_list', course_id=course.id))
    add_to_group = Learning_groups(group_id=group_id,
                                    student_id=student_id,
                                    course_id=course.id,
                                    term_id=term.id,
                                    project_id=project.id)
    db.session.add(add_to_group)
    db.session.commit()
    return redirect(url_for('students.update_students_group_list', course_id=course.id))


###### DELETE STUDENT ######
@students.route('/student_<int:student_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_student(student_id):
    student = Students.query.get_or_404(student_id)
    student_proj_info_dict = student_projects_info_dict(student_id)
    # Формируем список модераторов
    moder_stat = False
    for project in student_proj_info_dict['students_projects']:
        if project.moders_list:
            moders_list = text_format_for_html(project.moders_list)
            if current_user.id in moders_list or current_user.id == project.author_id:
                moder_stat = True
    if ((current_user.username != 'Administrator') and not moder_stat):
        abort(403)
    # Удаляем заглавную картинку для проекта
    if student.avatar != 'default_student.png':
        del_student_ava = os.path.join(current_app.root_path, os.path.join('static', 'students_pics', 'students_ava', students.avatar))
        os.remove(del_student_ava)
    # Удаляем прикрепленные файлы
    if student.attach:
        for attachment in json.loads(student.attach):
            filename = attachment
            curr_folder_path = os.path.join('static', 'student_attachments')
            directory = os.path.join(current_app.root_path, curr_folder_path, 'student_'+str(student_id))
            shutil.rmtree(directory, ignore_errors=True)
    # Определяем группы студента и удаляем связи
    learning_groups = db.session.execute(text(f"select id from learning_groups where student_id='{student_id}'")).first()[0]
    if learning_groups != None:
        db.session.execute(text(f"delete from learning_groups where student_id='{student_id}'"))
    # Удалние проекта, после того как разобрались с констреинтами
    db.session.delete(student)
    db.session.commit()
    flash('Участник удален', 'success')
    if 'course_id' in session:
        return redirect(url_for('students.update_students_group_list', course_id=session['course_id']))
    else:
        return redirect(url_for('projects.projects_list'))


###### DELETE STUDENT FROM LIST ######
@students.route('/student_<int:student_id>/delete_from_list', methods=['GET', 'POST'])
@login_required
def delete_from_list_student(student_id):
    group_id = request.args.get('group_id')
    course = Courses.query.filter_by(students_group_id=group_id).first()
    db.session.execute(text(f"delete from learning_groups where student_id='{student_id}' and group_id='{group_id}'"))
    db.session.commit()
    return redirect(url_for('students.update_students_group_list', course_id=course.id))


##### DOWNLOAD ATTACHMENT #####
@students.route('/student_<int:student_id>/download_attachment')
def download_attachment(student_id):
    """
    Скачиваем прикрепленный файл для выбранного участника
    """
    attachment = request.args.get('attachment')
    filename = attachment
    curr_folder_path = os.path.join('static', 'student_attachments')
    directory = os.path.join(current_app.root_path, curr_folder_path, 'student_'+str(student_id))
    filepath = os.path.join(directory, filename)
    return send_file(filepath, attachment_filename=filename, as_attachment=True)

##### DELETE ATTACHMENT #####
@students.route('/student_<int:student_id>/attachment_delete')
def delete_attachment(student_id):
    """
    Удаляем прикрепленный файл для выбранного участника
    """
    student = Students.query.get_or_404(student_id)
    student_proj_info_dict = student_projects_info_dict(student_id)
    # Формируем список модераторов
    moder_stat = False
    for project in student_proj_info_dict['students_projects']:
        if project.moders_list:
            moders_list = text_format_for_html(project.moders_list)
            if current_user.id in moders_list or current_user.id == project.author_id:
                moder_stat = True
    attachment = request.args.get('attachment')
    if ((current_user.username != 'Administrator') and not moder_stat):
        abort(403)
    filename = attachment
    curr_folder_path = os.path.join('static', 'student_attachments')
    directory = os.path.join(current_app.root_path, curr_folder_path, 'student_'+str(student_id))
    curr_filepath = os.path.join(current_app.root_path, directory, filename)
    os.remove(curr_filepath)
    if len(os.listdir(directory)) == 0:
        shutil.rmtree(directory, ignore_errors=True)
        student.attach = None
        db.session.commit()
    else:
        if student.attach:
            attachments = json.loads(student.attach)
            attachments.remove(filename)
            student.attach = json.dumps(attachments)
            db.session.commit()
    flash('Прикрепленный к профилю участника файл удален', 'warning')
    return redirect(url_for('student.update_student', student_id=student.id))
