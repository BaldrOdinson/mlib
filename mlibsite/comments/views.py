#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, request, session, redirect, Blueprint, current_app, abort, Markup
from flask_login import current_user, login_required
from mlibsite import db
from mlibsite.models import Projects, Methodics, Term, Courses, Lessons, Comments, User
from mlibsite.comments.forms import AddCommentForm, UpdateCommentForm
from mlibsite.comments.comments_processing import select_comments
from mlibsite.users.user_roles import get_roles, user_role
from datetime import datetime
from mlibsite.methodics.text_formater import date_translate, text_for_markup


comments = Blueprint('comments', __name__, template_folder='templates/comments')


###### COMMENTS (VIEW) ######
@comments.route('/<int:item_id>/comments', methods=['GET', 'POST'])  # <int: - для того чтобы номер методики точно был integer
def comments_view(item_id):

    #(1-project, 2-method, 3-course, 4-lesson)
    item_type = request.args.get('item_type', 1, type=int)

    form = AddCommentForm()

    # Получаем текущую страницу
    page = request.args.get('page', 1, type=int)
    # Выбираем настройки комментируемой сущности
    # Комметнарии дла МЕТОДИКИ
    if item_type==1:
        item_type_desc = 'Method'
        method_id = item_id
        method = Methodics.query.get_or_404(method_id)
        comments_dict, authors_dict, paginate_base_comments = select_comments(method.id, item_type=1, page=page)
        if current_user.is_authenticated:
            ##### РОЛЬ ДОСТУПА #####
            # Смотрим роли пользователей по методике
            method_roles = get_roles(item_id=method.id, item_type=1)
            # определяем роль пользователя
            curr_user_role = user_role(method_roles, current_user.id)
        else:
            curr_user_role = ''
        print(f'comments_dict: {comments_dict}\nРоль пользователя: {curr_user_role}')
    # Комметнарии дла ПРОЕКТА
    elif item_type==2:
        item_type_desc = 'Project'
        project_id = item_id
        project = Projects.query.get_or_404(project_id)
        comments_dict, authors_dict, paginate_base_comments = select_comments(project.id, 2, page=page)
        if current_user.is_authenticated:
            ##### РОЛЬ ДОСТУПА #####
            # Смотрим роли пользователей по проекту
            project_roles = get_roles(item_id=project.id, item_type=2)
            # определяем роль пользователя
            curr_user_role = user_role(project_roles, current_user.id)
        else:
            curr_user_role = ''

    # Комметнарии дла КУРСА
    elif item_type==3:
        item_type_desc = 'Course'
        course_id = item_id
        course = Courses.query.get_or_404(course_id)
        term = Term.query.get_or_404(course.term_id)
        project = Projects.query.get_or_404(term.project_id)
        comments_dict, authors_dict, paginate_base_comments = select_comments(course.id, 3, page=page)
        if current_user.is_authenticated:
            ##### РОЛЬ ДОСТУПА #####
            # Смотрим роли пользователей по проекту
            project_roles = get_roles(item_id=project.id, item_type=2)
            # определяем роль пользователя
            curr_user_role = user_role(project_roles, current_user.id)
        else:
            curr_user_role = ''
    # Комметнарии дла ЗАНЯТИЯ
    elif item_type==4:
        item_type_desc = 'Lesson'
        lesson_id = item_id
        lesson = Lessons.query.get_or_404(lesson_id)
        course = Courses.query.get_or_404(lesson.course_id)
        term = Term.query.get_or_404(course.term_id)
        project = Projects.query.get_or_404(term.project_id)
        comments_dict, authors_dict, paginate_base_comments = select_comments(lesson.id, 4, page=page)
        if current_user.is_authenticated:
            ##### РОЛЬ ДОСТУПА #####
            # Смотрим роли пользователей по проекту
            project_roles = get_roles(item_id=project.id, item_type=2)
            # определяем роль пользователя
            curr_user_role = user_role(project_roles, current_user.id)
        else:
            curr_user_role = ''

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            return redirect(url_for('users.login'))
        comment = Comments(body = form.body.data,
                            author_id = current_user.id,
                            parrent_comment=0,
                            item_id=item_id,
                            item_type=item_type,
                            item_type_desc=item_type_desc,
                            disabled=False)

        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен', 'success')
        return redirect(url_for('comments.comments_view', item_id=item_id, item_type=item_type))

    # Первоначальная загрузка
    elif request.method == 'GET':
    # Передаем в html инфу для нужной сущности

        if item_type==1:
            return render_template('items_comments.html',
                                    form=form,
                                    method=method,
                                    paginate_base_comments=paginate_base_comments,
                                    curr_user_role=curr_user_role,
                                    comments_dict=comments_dict,
                                    authors_dict=authors_dict,
                                    curr_time=datetime.now(),
                                    Markup=Markup,
                                    date_translate=date_translate,
                                    str=str,
                                    item_id=item_id,
                                    item_type=item_type,
                                    page=page)
        elif item_type==2:
            return render_template('items_comments.html',
                                    form=form,
                                    project=project,
                                    paginate_base_comments=paginate_base_comments,
                                    curr_user_role=curr_user_role,
                                    comments_dict=comments_dict,
                                    authors_dict=authors_dict,
                                    curr_time=datetime.now(),
                                    Markup=Markup,
                                    date_translate=date_translate,
                                    str=str,
                                    item_id=item_id,
                                    item_type=item_type,
                                    page=page)
        elif item_type==3:
            return render_template('items_comments.html',
                                    form=form,
                                    course=course,
                                    paginate_base_comments=paginate_base_comments,
                                    curr_user_role=curr_user_role,
                                    comments_dict=comments_dict,
                                    authors_dict=authors_dict,
                                    curr_time=datetime.now(),
                                    Markup=Markup,
                                    date_translate=date_translate,
                                    str=str,
                                    item_id=item_id,
                                    item_type=item_type,
                                    page=page)
        elif item_type==4:
            return render_template('items_comments.html',
                                    form=form,
                                    lesson=lesson,
                                    paginate_base_comments=paginate_base_comments,
                                    curr_user_role=curr_user_role,
                                    comments_dict=comments_dict,
                                    authors_dict=authors_dict,
                                    curr_time=datetime.now(),
                                    Markup=Markup,
                                    date_translate=date_translate,
                                    str=str,
                                    item_id=item_id,
                                    item_type=item_type,
                                    page=page)


###### REPLY TO COMMENT ######
@comments.route('/comment_<int:comment_id>/reply', methods=['GET', 'POST'])  # <int: - для того чтобы номер методики точно был integer
@login_required
def reply_to_comment(comment_id):
    comment = Comments.query.get_or_404(comment_id)
    author_id = comment.author_id
    author = User.query.filter_by(id=author_id).first()

    # Получаем текущую страницу
    page = request.args.get('page', 1, type=int)

    form = AddCommentForm()

    if form.validate_on_submit():
        new_comment = Comments(body = form.body.data,
                            author_id = current_user.id,
                            parrent_comment=comment.id,
                            item_id=comment.item_id,
                            item_type=comment.item_type,
                            item_type_desc=comment.item_type_desc,
                            disabled=False)

        db.session.add(new_comment)
        db.session.commit()
        flash('Ответ добавлен', 'success')
        return redirect(url_for('comments.comments_view', item_id=comment.item_id, item_type=comment.item_type, page=page))

    # Первоначальная загрузка
    elif request.method == 'GET':
        return render_template('reply_to_comment.html',
                                form=form,
                                comment=comment,
                                author=author,
                                Markup=Markup,
                                date_translate=date_translate,
                                str=str)


###### EDIT COMMENT ######
@comments.route('/comment_<int:comment_id>/edit', methods=['GET', 'POST'])  # <int: - для того чтобы номер методики точно был integer
@login_required
def edit_comment(comment_id):

    comment = Comments.query.get_or_404(comment_id)
    item_id = comment.item_id
    item_type = comment.item_type

    # Получаем текущую страницу
    page = request.args.get('page', 1, type=int)

    if not ((current_user.username == 'Administrator')
                or ((current_user.id == comment.author_id) and ((datetime.now() - comment.create_date).days < 1))):
        abort(403)

    form = UpdateCommentForm()

    if form.validate_on_submit():
        comment.body = form.body.data
        comment.change_date = datetime.now()

        db.session.commit()

        flash(f'Изменения комментария сохранены.', 'success')
        return redirect(url_for('comments.comments_view', item_id=item_id, item_type=item_type, page=page))

    # Первоначальная загрузка
    elif request.method == 'GET':
        form.body.data = comment.body

        return render_template('update_comment.html',
                                form=form)


###### DELETE (DISABLED) COMMENT ######
@comments.route('/comment_<int:comment_id>/delete', methods=['GET', 'POST'])  # <int: - для того чтобы номер методики точно был integer
@login_required
def delete_comment(comment_id):

    # Получаем текущую страницу
    page = request.args.get('page', 1, type=int)

    comment = Comments.query.get_or_404(comment_id)
    comment.disabled = True
    print(f'Статус коммента: disabled = {comment.disabled}')
    db.session.commit()

    flash('Комментарий со всеми ответами на него удален.', 'success')
    return redirect(url_for('comments.comments_view', item_id=comment.item_id, item_type=comment.item_type, page=page))
