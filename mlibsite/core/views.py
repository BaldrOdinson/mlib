#! /usr/bin/env python
# -*- coding: utf-8 -*-
from mlibsite.models import Methodics, Categories
from flask import render_template, request, redirect, url_for, Blueprint, Markup, flash, session
from mlibsite.methodics.text_formater import text_format_for_html, date_translate, get_html_category_list, text_for_links_markup
from mlibsite.core.forms import CommonSearchMethodForm, CommonSearchStudentForm, CommonSearchProjectForm
from sqlalchemy import or_

core = Blueprint('core', __name__, template_folder='templates/core')

@core.route('/')
def index():
    # pagination
    per_page=9
    page = request.args.get('page', 1, type=int)
    short_desc_html_list_dict = {}
    # methodics = Methodics.query.order_by(Methodics.publish_date.desc()).paginate(page=page, per_page=per_page)
    methodics = Methodics.query.order_by(Methodics.change_date.desc()).paginate(page=page, per_page=per_page)
    methodics_whole = Methodics.query.order_by(Methodics.change_date.desc())[page*per_page-per_page:page*per_page]
    for method in methodics_whole:
        short_desc_html_list_dict[method.id] = text_format_for_html(method.short_desc)
    html_category_list = get_html_category_list()
    return render_template('index.html',
                            short_desc_dict=short_desc_html_list_dict,
                            methodics=methodics,
                            date_translate=date_translate,
                            html_category_list=html_category_list)


@core.route('/info')
def info():
    return render_template('info.html')


#################
##### ПОИСК #####
@core.route('/search', methods=['GET', 'POST'])
def mlib_search():

    session.pop('lesson_id', None)
    session.pop('course_id', None)
    session.pop('method_id', None)

    method_form = CommonSearchMethodForm()
    # Достаем категорию для поиска
    html_category_list = get_html_category_list()
    all_cat_num = Methodics.query.order_by(Methodics.change_date.desc()).count()
    html_category_list.insert(0, (0, Markup('Любая категория'), all_cat_num))

    project_form = CommonSearchProjectForm()

    student_form = CommonSearchStudentForm()

    # print(f'request form: {request.form}')
    # не проверяем форму method если в полученной есть поле first_name или web_links
    if ('first_name' not in request.form) and ('web_links' not in request.form):
        if method_form.validate_on_submit():
            # Берем все категории, у каторых выбранный id в id или parrent_cat (родительской категории)
            selected_category = int(request.form.get('form_category'))
            if selected_category != 0:
                req_category = Categories.query.filter_by(id=int(selected_category)).first()
                categories = Categories.query.filter(or_(Categories.id == selected_category, Categories.parrent_cat == selected_category))
                categories_ids = [req_category.id]
                # строим список со всеми выбранныйми id, затем по нему формируем SQL sequences
                for cat in categories:
                    categories_ids.append(cat.id)
            else:
                categories_ids = [0]
            # Формируем параметры поиска на основе указанных пользователем
            selected_methods_dict = {}
            if method_form.author.data:
                selected_methods_dict['author'] = '%'+method_form.author.data+'%'
            else: selected_methods_dict['author'] = '%'
            if method_form.title.data:
                selected_methods_dict['title'] = '%'+method_form.title.data+'%'
            else: selected_methods_dict['title'] = '%'
            if method_form.short_desc.data:
                selected_methods_dict['short_desc'] = '%'+method_form.short_desc.data+'%'
            else: selected_methods_dict['short_desc'] = '%'
            if method_form.target.data:
                selected_methods_dict['target'] = '%'+method_form.target.data+'%'
            else: selected_methods_dict['target'] = '%'
            if method_form.consumables.data:
                selected_methods_dict['consumables'] = '%'+method_form.consumables.data+'%'
            else: selected_methods_dict['consumables'] = '%'
            selected_methods_dict['category'] =  categories_ids
            if method_form.tags.data:
                selected_methods_dict['tags'] = '%'+method_form.tags.data+'%'
            else: selected_methods_dict['tags'] = '%'

            # print(f'selected_methods_dict: {selected_methods_dict}')
            session['selected_methods_dict'] = selected_methods_dict
            return redirect(url_for('methodics.selected_methods_list'))

    # не проверяем форму project если в полученной есть поле first_name
    if 'first_name' not in request.form:
        if project_form.validate_on_submit():
            # Формируем параметры поиска на основе указанных пользователем
            selected_projects_dict = {}
            if project_form.name.data:
                selected_projects_dict['name'] = '%'+project_form.name.data+'%'
            else: selected_projects_dict['name'] = '%'
            if project_form.short_desc.data:
                selected_projects_dict['short_desc'] = '%'+project_form.short_desc.data+'%'
            else: selected_projects_dict['short_desc'] = '%'
            if project_form.contacts.data:
                selected_projects_dict['contacts'] = project_form.contacts.data
            else: selected_projects_dict['contacts'] = '%'
            if project_form.address.data:
                selected_projects_dict['address'] = '%'+project_form.address.data+'%'
            else: selected_projects_dict['address'] = '%'
            if project_form.web_links.data:
                selected_projects_dict['web_links'] = '%'+project_form.web_links.data+'%'
            else: selected_projects_dict['web_links'] = '%'

            print(f'selected_projects_dict: {selected_projects_dict}')
            session['selected_projects_dict'] = selected_projects_dict
            return redirect(url_for('projects.selected_projects_list'))


    if student_form.validate_on_submit():
        # Формируем параметры поиска на основе указанных пользователем
        selected_students_dict = {}
        if student_form.first_name.data:
            selected_students_dict['first_name'] = '%'+student_form.first_name.data+'%'
        else: selected_students_dict['first_name'] = '%'
        if student_form.last_name.data:
            selected_students_dict['last_name'] = '%'+student_form.last_name.data+'%'
        else: selected_students_dict['last_name'] = '%'
        if student_form.age.data:
            selected_students_dict['age'] = student_form.age.data
        else: selected_students_dict['age'] = '%'
        if student_form.phone_num.data:
            selected_students_dict['phone_num'] = '%'+student_form.phone_num.data+'%'
        else: selected_students_dict['phone_num'] = '%'
        if student_form.email.data:
            selected_students_dict['email'] = '%'+student_form.email.data+'%'
        else: selected_students_dict['email'] = '%'
        if student_form.address.data:
            selected_students_dict['address'] = '%'+student_form.address.data+'%'
        else: selected_students_dict['address'] = '%'

        print(f'selected_students_dict: {selected_students_dict}')
        session['selected_students_dict'] = selected_students_dict
        return redirect(url_for('students.selected_students_list'))

    # первоначальная загрузка формы поиска
    elif request.method == 'GET':
        pass
    # Если форма заполненна с ошибками, а валидаторам плевать
    for form in [method_form, student_form]:
        if form.errors:
            flash_text = 'Форма поиска участника заполнена неверно. <br>'
            print(f'form errors: {form.errors}')
            for error in form.errors:
                flash_text += form.errors[error][0]
            flash_text += '<br>К сожалению, последние изменения не сохранены. '
            flash(Markup(flash_text), 'negative')

    return render_template('common_search.html',
                                method_form=method_form,
                                student_form=student_form,
                                project_form=project_form,
                                html_category_list=html_category_list)
