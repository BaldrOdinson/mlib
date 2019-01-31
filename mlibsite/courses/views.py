#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, session, request, redirect, Blueprint, current_app, Markup, abort, send_file
from flask_login import current_user, login_required
from mlibsite import db
from mlibsite.models import Methodics, Courses, Lessons, Term, Projects, StudentsGroup, Learning_groups, Students
from mlibsite.methodics.text_formater import text_format_for_html, date_translate, text_for_markup
from mlibsite.courses.forms import AddCourseForm, UpdateCourseForm, AddLessonForm, UpdateLessonForm
from mlibsite.courses.picture_handler import add_course_pic
from mlibsite.courses.files_saver import add_attachment, add_lesson_attachment
from datetime import datetime
import json, os, shutil

courses = Blueprint('courses', __name__, template_folder='templates/courses')


##### ADD COURSE #####
@courses.route('/term_<int:term_id>/create_course', methods=['GET', 'POST'])
@login_required
def create_course(term_id):
    """
    Создаем новый курс для определенного периода выбранного проекта
    """
    term = term = Term.query.get_or_404(term_id)
    project = Projects.query.get_or_404(term.project_id)

    form = AddCourseForm()

    if form.validate_on_submit():
        course = Courses(project_id=project.id,
                        term_id = term.id,
                        name=form.name.data,
                        description=form.description.data,
                        start_date = form.start_date.data,
                        finish_date = form.finish_date.data)

        db.session.add(course)
        db.session.commit()
        flash('Курс занятий создан', 'success')
        course = Courses.query.filter_by(term_id=term_id, name=form.name.data).first()
        return redirect(url_for('courses.update_course', course_id=course.id))
    # Первая загрузка
    return render_template('create_course.html',
                            form=form,
                            term_name = term.name,
                            project_name = project.name,
                            project=project,
                            term=term)


###### UPDATE COURSE ######
@courses.route('/update_course_<int:course_id>', methods=['GET', 'POST'])
@login_required
def update_course(course_id):
    """
    Изменяем созданный курс занятий. Добавляем информацию, файлы, указываем методику
    """
    course = Courses.query.get_or_404(course_id)
    term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)
    form = UpdateCourseForm()

    if form.validate_on_submit():
        # Если загружается картинка для Курса
        if form.label_image.data:
            project_id = project.id
            pic = add_course_pic(form.label_image.data, course.id, course.label_image)
            course.label_image = pic
        # Если загружается дополнительный файл
        # формируем общий список, переводим в форма JSON и сохраняем в базу
        if form.attach.data:
            project_id = project.id
            if course.attach:
                attachments_files_list = json.loads(project.attach)
            else:
                attachments_files_list = []
            attachment_filename = add_attachment(form.attach.data, course.id, project_id, term.id, course.attach)
            attachments_files_list.append(attachment_filename)
            json_attachments = json.dumps(attachments_files_list)
            course.attach = json_attachments

        course.name = form.name.data
        course.description = form.description.data
        course.start_date = form.start_date.data
        course.finish_date = form.finish_date.data
        course.contacts_info = form.contacts_info.data
        course.address = form.address.data
        course.tutors = form.tutors.data
        course.web_links = form.web_links.data
        course.note = form.note.data

        db.session.commit()
        return redirect(url_for('courses.course_view', course_id=course.id))
    # первоначальная загрузка
    elif request.method == 'GET':
        form.name.data = course.name
        form.description.data = course.description
        form.start_date.data = course.start_date
        form.finish_date.data = course.finish_date
        form.contacts_info.data = course.contacts_info
        form.address.data = course.address
        form.tutors.data = course.tutors
        form.web_links.data = course.web_links
        form.note.data = course.note

    label_image = url_for('static', filename = 'projects_pics/project_courses/'+course.label_image)
    # Формируем список с прикрепленными файлами
    attachments = []
    if course.attach:
        for attachment in json.loads(course.attach):
            attachments.append(attachment)
    # Если форма заполненна с ошибками, а валидаторам плевать
    if form.errors:
        flash_text = 'Форма курса заполнена неверно. <br>'
        print(f'form errors: {form.errors}')
        for error in form.errors:
            flash_text += form.errors[error][0]
        flash_text += '<br>К сожалению, последние изменения не сохранены. '
        flash(Markup(flash_text), 'negative')
    return render_template('update_course.html',
                            label_image=label_image,
                            project_name = project.name,
                            term_name = term.name,
                            form=form,
                            project=project,
                            term=term,
                            course=course,
                            attachments=attachments)


###### COURSE (VIEW) ######
@courses.route('/course_<int:course_id>')  # <int: - для того чтобы номер методики точно был integer
def course_view(course_id):
    course = Courses.query.get_or_404(course_id)
    term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)
    course_schedule = Lessons.query.filter_by(course_id=course.id).order_by(Lessons.lesson_date).all()
    if course.students_group_id:
        students_group = StudentsGroup.query.get(course.students_group_id)
        student_group_desc=students_group.description
    else:
        student_group_desc=''
    # Формируем список модераторов
    moder_stat = False
    if project.moders_list:
        moders_list = text_format_for_html(project.moders_list)
        if current_user.id in moders_list:
            moder_stat = True
    # разделяем преформатированный текст на строки, так как переносы не обрабатываются
    description_html=Markup(text_for_markup(course.description))
    contacts_info_html=Markup(text_for_markup(course.contacts_info))
    address_html=Markup(text_for_markup(course.address))
    tutors_html=Markup(text_for_markup(course.tutors))
    web_links_html=Markup(text_for_markup(course.web_links))
    note_html=Markup(text_for_markup(course.note))
    # Формируем список с файлами презентаций, достаем из базы список в JSON и переводим его в нормальный
    attachments = []
    if course.attach:
        for attachment in json.loads(course.attach):
            attachments.append(attachment)
    # формируем список группы
    students_group_list = []
    if course.students_group_id:
        students_group = StudentsGroup.query.get_or_404(course.students_group_id)
        learning_group = Learning_groups.query.filter_by(group_id=course.students_group_id)
        for student in learning_group:
            students_group_list.append(Students.query.filter_by(id=student.student_id).first())
    # формируем словарь с привязанными к занятим методиками
    methods_dict = {}
    if course_schedule:
        # students_group = StudentsGroup.query.get_or_404(course.students_group_id)
        # learning_group = Learning_groups.query.filter_by(group_id=course.students_group_id)
        for lesson in course_schedule:
            method_id = lesson.method_id
            method = Methodics.query.filter_by(id=method_id).first()
            methods_dict['method_id'] = method
    return render_template('course.html',
                            term = term,
                            project = project,
                            course = course,
                            course_schedule=course_schedule,
                            methods_dict=methods_dict,
                            attachments = attachments,
                            moder_stat = moder_stat,
                            description = description_html,
                            contacts_info = contacts_info_html,
                            address = address_html,
                            note = note_html,
                            web_links = web_links_html,
                            tutors = tutors_html,
                            date_translate=date_translate,
                            students_group_desc=student_group_desc,
                            students_group_list=students_group_list,
                            len=len,
                            zip=zip)


###### DELETE COURSE ######
@courses.route('/course_<int:course_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_course(course_id):
    course = Courses.query.get_or_404(course_id)
    term = Term.query.get_or_404(course.term_id)
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
    if course.label_image != 'default_course.png':
        del_course_ava = os.path.join(current_app.root_path, os.path.join('static', 'projects_pics', 'project_courses', course.label_image))
        os.remove(del_course_ava)
    # Удаляем прикрепленные файлы
    if course.attach:
        for attachment in json.loads(course.attach):
            filename = attachment
            curr_folder_path = os.path.join('static', 'project_attachments', 'project_'+str(project.id), 'term_'+str(term.id))
            directory = os.path.join(current_app.root_path, curr_folder_path, 'course_'+str(course_id))
            shutil.rmtree(directory, ignore_errors=True)
    # Удалние проекта, после того как разобрались с констреинтами
    db.session.delete(course)
    db.session.commit()
    flash('Курс удален', 'success')
    return redirect(url_for('projects.term_view', term_id=term.id))


##### DOWNLOAD COURSE ATTACHMENT #####
@courses.route('/course_<int:course_id>/download')
def download_attachment(course_id):
    """
    Скачиваем прикрепленный файл для выбранного курса
    """
    course = Courses.query.get_or_404(course_id)
    term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)
    attachment = request.args.get('attachment')
    filename = attachment
    curr_folder_path = os.path.join('static', 'project_attachments', 'project_'+str(project.id), 'term_'+str(term.id))
    directory = os.path.join(current_app.root_path, curr_folder_path, 'course_'+str(course_id))
    filepath = os.path.join(directory, filename)
    return send_file(filepath, attachment_filename=filename, as_attachment=True)

##### DELETE COURSE ATTACHMENT #####
@courses.route('/course_<int:course_id>/attachment_delete')
def delete_attachment(course_id):
    """
    Удаляем прикрепленный файл для выбранного проекта
    """
    course = Courses.query.get_or_404(course_id)
    term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)
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
    curr_folder_path = os.path.join('static', 'project_attachments', 'project_'+str(project.id), 'term_'+str(term.id))
    directory = os.path.join(current_app.root_path, curr_folder_path, 'course_'+str(course_id))
    curr_filepath = os.path.join(current_app.root_path, directory, filename)
    os.remove(curr_filepath)
    if len(os.listdir(directory)) == 0:
        shutil.rmtree(directory, ignore_errors=True)
        course.attach = None
        db.session.commit()
    else:
        if course.attach:
            attachments = json.loads(course.attach)
            attachments.remove(filename)
            course.attach = json.dumps(attachments)
            db.session.commit()
    flash('Прикрепленный к курсу  файл удален', 'warning')
    # filepath = os.path.join(directory, filename)
    return redirect(url_for('courses.update_course', course_id=course_id))

######################## LESSONS ########################
#########################################################

##### ADD LESSON #####
@courses.route('/course_<int:course_id>/create_lesson', methods=['GET', 'POST'])
@login_required
def create_lesson(course_id):
    """
    Создаем новое занятие для выбранного курса
    """
    course = Courses.query.get_or_404(course_id)
    term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)

    form = AddLessonForm()

    if form.validate_on_submit():
        lesson = Lessons(course_id=course.id,
                        description=form.description.data,
                        lesson_date = form.lesson_date.data,
                        start_time = form.start_time.data,
                        finish_time = form.finish_time.data)

        db.session.add(lesson)
        db.session.commit()
        flash('Занятие создано', 'success')
        lesson = Lessons.query.filter_by(course_id=course_id, description=form.description.data).first()
        return redirect(url_for('courses.update_lesson', lesson_id=lesson.id))
    # Первая загрузка
    return render_template('create_lesson.html',
                            form=form,
                            course = course,
                            project = project,
                            term=term)


###### UPDATE LESSON ######
@courses.route('/update_lesson_<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def update_lesson(lesson_id):
    """
    Редактируем и дополняем информацию по занятию
    """
    lesson = Lessons.query.get_or_404(lesson_id)
    course = Courses.query.get_or_404(lesson.course_id)
    term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)
    session['lesson_id'] = lesson.id

    form = UpdateLessonForm()

    if form.validate_on_submit():

        # Если загружается дополнительный файл
        # формируем общий список, переводим в форма JSON и сохраняем в базу
        if form.attach.data:
            project_id = project.id
            if course.attach:
                attachments_files_list = json.loads(project.attach)
            else:
                attachments_files_list = []
            attachment_filename = add_lesson_attachment(form.attach.data, lesson.id, course.id, project.id, term.id, lesson.attach)
            attachments_files_list.append(attachment_filename)
            json_attachments = json.dumps(attachments_files_list)
            lesson.attach = json_attachments

        lesson.description = form.description.data
        lesson.lesson_date = form.lesson_date.data
        lesson.start_time = form.start_time.data
        lesson.finish_time = form.finish_time.data
        lesson.method_id = form.method_id.data
        lesson.tutors = form.tutors.data
        lesson.absent_students_list = form.absent_students_list.data
        lesson.web_links = form.web_links.data
        lesson.note = form.note.data

        db.session.commit()
        return redirect(url_for('courses.lesson_view', lesson_id=lesson.id))
    # первоначальная загрузка
    elif request.method == 'GET':
        form.description.data = lesson.description
        form.lesson_date.data = lesson.lesson_date
        form.start_time.data = lesson.start_time
        form.finish_time.data = lesson.finish_time
        form.method_id.data = lesson.method_id
        form.tutors.data = lesson.tutors
        form.absent_students_list.data = lesson.absent_students_list
        form.web_links.data = lesson.web_links
        form.note.data = lesson.note

    label_image = url_for('static', filename = 'projects_pics/default_lesson.png')
    # Берем выбранную для занятия методику
    if lesson.method_id:
        method = Methodics.query.get_or_404(lesson.method_id)
    else:
        method=''
    # Формируем список с прикрепленными файлами
    attachments = []
    if lesson.attach:
        for attachment in json.loads(lesson.attach):
            attachments.append(attachment)
    # Если форма заполненна с ошибками, а валидаторам плевать
    if form.errors:
        flash_text = 'Форма курса заполнена неверно. <br>'
        print(f'form errors: {form.errors}')
        for error in form.errors:
            flash_text += form.errors[error][0]
        flash_text += '<br>К сожалению, последние изменения не сохранены. '
        flash(Markup(flash_text), 'negative')
    return render_template('update_lesson.html',
                            label_image=label_image,
                            form=form,
                            project=project,
                            term=term,
                            course=course,
                            lesson=lesson,
                            method=method,
                            attachments=attachments)


###### LESSON (VIEW) ######
@courses.route('/lesson_<int:lesson_id>')  # <int: - для того чтобы номер методики точно был integer
def lesson_view(lesson_id):
    lesson = Lessons.query.get_or_404(lesson_id)
    course = Courses.query.get_or_404(lesson.course_id)
    term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)
    if lesson.method_id:
        method = Methodics.query.get_or_404(lesson.method_id)
    else:
        method=''
    # Формируем список модераторов
    moder_stat = False
    if project.moders_list:
        moders_list = text_format_for_html(project.moders_list)
        if current_user.id in moders_list:
            moder_stat = True
    # разделяем преформатированный текст на строки, так как переносы не обрабатываются
    description_html=Markup(text_for_markup(lesson.description))
    tutors_html=Markup(text_for_markup(lesson.tutors))
    web_links_html=Markup(text_for_markup(lesson.web_links))
    note_html=Markup(text_for_markup(lesson.note))
    # Формируем список с файлами презентаций, достаем из базы список в JSON и переводим его в нормальный
    attachments = []
    if lesson.attach:
        for attachment in json.loads(lesson.attach):
            attachments.append(attachment)

    return render_template('lesson.html',
                            term = term,
                            project = project,
                            course = course,
                            lesson=lesson,
                            method=method,
                            attachments = attachments,
                            moder_stat = moder_stat,
                            description = description_html,
                            note = note_html,
                            web_links = web_links_html,
                            tutors = tutors_html,
                            date_translate=date_translate)


###### DELETE LESSON ######
@courses.route('/lesson_<int:lesson_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_lesson(lesson_id):
    lesson = Lessons.query.get_or_404(lesson_id)
    course = Courses.query.get_or_404(lesson.course_id)
    term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)
    # Формируем список модераторов
    moder_stat = False
    if project.moders_list:
        moders_list = text_format_for_html(project.moders_list)
        if current_user.id in moders_list:
            moder_stat = True
    if ((project.author_id != current_user) and (current_user.username != 'Administrator') and not moder_stat):
        abort(403)
    # Удаляем прикрепленные файлы
    if lesson.attach:
        for attachment in json.loads(lesson.attach):
            filename = attachment
            curr_folder_path = os.path.join('static', 'project_attachments',
                                                    'project_'+str(project.id),
                                                    'term_'+str(term.id),
                                                    'course_'+str(course.id))
            directory = os.path.join(current_app.root_path, curr_folder_path, 'lesson_'+str(lesson_id))
            shutil.rmtree(directory, ignore_errors=True)
        # Удаляем пустые папки
            curr_folder = os.path.join(current_app.root_path, 'static', 'project_attachments',
                                                    'project_'+str(project.id),
                                                    'term_'+str(term.id),
                                                    'course_'+str(course.id))
            if len(os.listdir(curr_folder)) == 0:
                shutil.rmtree(curr_folder, ignore_errors=True)
                curr_folder = os.path.join(current_app.root_path, 'static', 'project_attachments',
                                                        'project_'+str(project.id),
                                                        'term_'+str(term.id))
                if len(os.listdir(curr_folder)) == 0:
                    shutil.rmtree(curr_folder, ignore_errors=True)
                    curr_folder = os.path.join(current_app.root_path, 'static', 'project_attachments',
                                                            'project_'+str(project.id))
                    if len(os.listdir(curr_folder)) == 0:
                        shutil.rmtree(curr_folder, ignore_errors=True)
    # Удалние проекта, после того как разобрались с констреинтами
    db.session.delete(lesson)
    db.session.commit()
    flash('Занятие удалено', 'success')
    return redirect(url_for('courses.course_view', course_id=course.id))


##### UPDATE SCHEDULE #####
@courses.route('/course_<int:course_id>/update_schedule', methods=['GET', 'POST'])
@login_required
def update_schedule(course_id):
    """
    Редактируем расписание занятий проекта
    """
    course = Courses.query.get_or_404(course_id)
    term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)
    course_schedule = Lessons.query.filter_by(course_id=course.id).order_by(Lessons.lesson_date).all()
    # формируем словарь с привязанными к занятим методиками
    methods_dict = {}
    if course_schedule:
        # students_group = StudentsGroup.query.get_or_404(course.students_group_id)
        # learning_group = Learning_groups.query.filter_by(group_id=course.students_group_id)
        for lesson in course_schedule:
            method_id = lesson.method_id
            method = Methodics.query.filter_by(id=method_id).first()
            methods_dict['method_id'] = method
    return render_template('course_schedule.html',
                            course_schedule=course_schedule,
                            course=course,
                            term=term,
                            project=project,
                            methods_dict=methods_dict,
                            date_translate=date_translate,
                            len=len,
                            zip=zip)


##### DOWNLOAD LESSON ATTACHMENT #####
@courses.route('/lesson_<int:lesson_id>/download')
def download_lesson_attachment(lesson_id):
    """
    Скачиваем прикрепленный файл для выбранного занятия
    """
    lesson = Lessons.query.get_or_404(lesson_id)
    course = Courses.query.get_or_404(lesson.course_id)
    term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)
    # получаем имя файла из аргументов запроса
    attachment = request.args.get('attachment')
    filename = attachment
    curr_folder_path = os.path.join('static', 'project_attachments',
                                            'project_'+str(project.id),
                                            'term_'+str(term.id),
                                            'course_'+str(course.id))
    directory = os.path.join(current_app.root_path, curr_folder_path, 'lesson_'+str(lesson_id))
    filepath = os.path.join(directory, filename)
    return send_file(filepath, attachment_filename=filename, as_attachment=True)

##### DELETE LESSON ATTACHMENT #####
@courses.route('/lesson_<int:lesson_id>/attachment_delete')
def delete_lesson_attachment(lesson_id):
    """
    Удаляем прикрепленный файл для выбранного занятия
    """
    lesson = Lessons.query.get_or_404(lesson_id)
    course = Courses.query.get_or_404(lesson.course_id)
    term = Term.query.get_or_404(course.term_id)
    project = Projects.query.get_or_404(term.project_id)
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
    curr_folder_path = os.path.join('static', 'project_attachments',
                                            'project_'+str(project.id),
                                            'term_'+str(term.id),
                                            'course_'+str(course.id))
    directory = os.path.join(current_app.root_path, curr_folder_path, 'lesson_'+str(lesson_id))
    curr_filepath = os.path.join(current_app.root_path, directory, filename)
    os.remove(curr_filepath)
    if len(os.listdir(directory)) == 0:
        shutil.rmtree(directory, ignore_errors=True)
        lesson.attach = None
        db.session.commit()
    else:
        if lesson.attach:
            attachments = json.loads(lesson.attach)
            attachments.remove(filename)
            lesson.attach = json.dumps(attachments)
            db.session.commit()
    flash('Прикрепленный к занятию файл удален', 'warning')
    # filepath = os.path.join(directory, filename)
    return redirect(url_for('courses.update_lesson', lesson_id=lesson_id))
