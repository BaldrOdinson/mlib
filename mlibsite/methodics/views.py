#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, request, redirect, Blueprint, current_app, send_file, abort, Markup
from flask_login import current_user, login_required
from mlibsite import db
from mlibsite.models import Methodics, MethodTiming, TimingSteps, Categories
from mlibsite.methodics.forms import MethodForm, UpdateMethodForm, AddCategoryForm
from mlibsite.methodics.picture_handler import add_method_pic, thumbnail_for_net_pic, img_tupal, thumbnail_list
from mlibsite.methodics.video_handler import check_video_links
from mlibsite.methodics.files_saver import add_method_presentation
from mlibsite.methodics.music_handler import take_music_url, check_music_link
from datetime import datetime
from mlibsite.methodics.text_formater import text_format_for_html, check_url_list, date_translate, create_category_dict, get_html_category_list, text_format_for_html
from sqlalchemy import or_, text
import os, shutil, json

methodics = Blueprint('methodics', __name__, template_folder='templates/methodics')


# Views

# Create
# Method (view)
# Update
# Delete
# Delete presentation
# Download presentation

###### CREATE ######
@methodics.route('/create', methods=['GET', 'POST'])
@login_required
def create_method():
    form = MethodForm()

    if form.validate_on_submit():
        # Фрмируем Age_range для базовы
        # age_range = form.age_range_from + ':' + form.age_range_till
        method = Methodics(user_id=current_user.id,
                           title=form.title.data,
                           short_desc=form.short_desc.data,
                           target=form.target.data,
                           description=form.description.data,
                           age_from=form.age_range_from.data,
                           age_till=form.age_range_till.data,
                           # consumables=form.consumables.data,
                           # timing_id=form.timing_id.data,
                           # presentation=form.presentation.data,
                           # images=form.images.data,
                           # music=form.music.data,
                           # video=form.video.data,
                           # literature=form.literature.data,
                           category=form.category.data,
                           tags=form.tags.data)

        db.session.add(method)
        db.session.commit()
        flash('Методика добавлена', 'success')
        method = Methodics.query.filter_by(user_id=current_user.id, title=form.title.data).first()
        return redirect(url_for('methodics.update', method_id=method.id))
    # Первая загрузка
    category = Categories.query.get(1)
    # Если форма заполненна с ошибками, а валидаторам плевать (например расширения файлов)
    print(f'form errors: {form.errors}')
    if form.errors:
        flash_text = 'Форма методики заполнена неверно. <br>'
        for error in form.errors:
            # print(form.errors[error])
            flash_text += form.errors[error][0]
        flash_text += 'К сожалению, последние изменения не сохранены. '
        flash(Markup(flash_text), 'negative')
    return render_template('create_method.html', form=form,
                                                category=category.category_name)


###### METHOD (VIEW) ######
@methodics.route('/method_<int:method_id>')  # <int: - для того чтобы номер методики точно был integer
def method(method_id):
    # Получаем из базы метод, тайминг занятия, этапы занятия
    method = Methodics.query.get_or_404(method_id)
    timing = MethodTiming.query.filter_by(method_id=method_id).first()
    steps = db.session.query(TimingSteps).filter_by(method_timing_id=method.timing_id).order_by('id')
    # разделяем преформатированный текст на строки, так как переносы не обрабатываются
    description_html_list=text_format_for_html(method.description)
    short_desc_html_list=text_format_for_html(method.short_desc)
    # создание превьюшек картинок по указанным ссылкам
    # получаем данные из формы, бъем их по строкам, делаем список из путей к превьюшкам и список с сылками
    # затем делаем список кортежей с линком и путём к превьюшке, который отправляем в форму для отображения
    if method.images:
        image_html_links=text_format_for_html(method.images)
        thumb_links=thumbnail_list(image_html_links, method.id)
        images_list=img_tupal(image_html_links, thumb_links)
    else:
        images_list=[]
    # ссылки на музыку
    if method.music:
        music_list = text_format_for_html(method.music)
        music_url_list = take_music_url(music_list)
    else:
        music_url_list=[]
    # формируем ссылку на видео
    if method.video:
        video_html_links=text_format_for_html(method.video)
        print(video_html_links)
    else:
        video_html_links = []
    # Проверяем наличие тайминга
    timing = MethodTiming.query.filter_by(method_id=method_id).first()
    if timing:
        timing_duration = timing.duration
        steps = db.session.query(TimingSteps).filter_by(method_timing_id=timing.id).order_by('id')
        if len(list(steps)) == 0:
            steps = None
    else:
        timing_duration = None
    # Возраст участников
    if method.age_from:
        # age_list = method.age_range.split(':')
        age_list = []
        age_list.append(method.age_from)
        age_list.append(method.age_till)
    else:
        age_list = []
    # Название категории
    category = Categories.query.get(method.category)
    # Test for deleting
    timing_id = db.session.execute(text(f"select timing_id from methodics where id='{method_id}'")).first()[0]
    print(f'Timing ID: {timing_id}')
    # Формируем список с файлами презентаций, достаем из базы список в JSON и переводим его в нормальный
    presentations = []
    if method.presentation:
        for presentation in json.loads(method.presentation):
            presentations.append(presentation)
    return render_template('method.html',
                            title=method.title,
                            date=method.publish_date,
                            description=description_html_list,
                            short_desc=short_desc_html_list,
                            # images_links=image_html_links,
                            # images_thumb_links=thumb_links,
                            presentations = presentations,
                            images_list=images_list,
                            music_list=music_url_list,
                            method_label_image=method.method_label_image,
                            method=method,
                            videos=video_html_links,
                            date_translate=date_translate,
                            timing_duration=timing_duration,
                            steps=steps,
                            category=category.category_name,
                            age_list=age_list)


##### CATEGORY METHODICS #####
# Методики конкретной категории с выводом постранично
@methodics.route('/category_<category>')
def category_methodics(category):
    # print(f'category: {category}')
    per_page=6
    page = request.args.get('page', 1, type=int) # пригодится если страниц дохера, делаем разбивку по страницам
    short_desc_html_list_dict = {}
    # Берем все категории, у каторых выбранный id в id или parrent_cat (родительской категории)
    req_category = Categories.query.filter_by(id=category).first()
    categories = Categories.query.filter(or_(Categories.id == category, Categories.parrent_cat == category))
    categories_ids = [req_category.id]
    # строим список со всеми выбранныйми id, затем по нему формируем SQL sequences
    for cat in categories:
        categories_ids.append(cat.id)
    methodics = Methodics.query.filter(Methodics.category.in_(categories_ids)).order_by(Methodics.change_date.desc()).paginate(page=page, per_page=6)
    methodics_whole = Methodics.query.filter(Methodics.category.in_(categories_ids)).order_by(Methodics.change_date.desc())[page*per_page-per_page:page*per_page]
    for method in methodics_whole:
        short_desc_html_list_dict[method.id] = text_format_for_html(method.short_desc)
    return render_template('category_methodics.html', methodics=methodics,
                                                    category=req_category,
                                                    date_translate=date_translate,
                                                    short_desc_dict=short_desc_html_list_dict)


##### CATEGORY SETUP #####
@methodics.route('/category_setup', methods=['GET', 'POST'])
@login_required
def category_setup():

    form = AddCategoryForm()

    if form.validate_on_submit():
        # parrent_cat = request.args.get('parrent_cat', type=int)
        category = Categories(category_name=form.new_category_name.data,
                                parrent_cat=int(form.parrent_cat.data))

        db.session.add(category)
        db.session.commit()
        html_category_list = get_html_category_list()
        return render_template('category_setup.html',
                                html_category_list=html_category_list,
                                form=form)


    html_category_list = get_html_category_list()
    return render_template('category_setup.html',
                            html_category_list=html_category_list,
                            form=form)

##### DELETE CATEGORY #####
@methodics.route('/category_delete')
@login_required
def delete_category():

    form = AddCategoryForm()

    category_id = request.args.get('category_id', type=int)
    child_categories = Categories.query.filter_by(parrent_cat=category_id)
    for category in child_categories:
        db.session.delete(category)
    category = method = Categories.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    # html_category_list = get_html_category_list()
    return redirect(url_for('methodics.category_setup'))


##### !!!! FOR TEST REASON: METHODICS CATEGORY DICT TEST #####
@methodics.route('/dict_test_<category>')
def dict_category(category):
    page = request.args.get('page', 1, type=int)
    category_dict = create_category_dict()
    req_category = Categories.query.filter_by(id=category).first()
    methodics = Methodics.query.filter_by(category=req_category.id).order_by(Methodics.publish_date.desc()).paginate(page=page, per_page=6)
    return render_template('category_methodics.html', methodics=methodics,
                                                    category=req_category,
                                                    date_translate=date_translate)

###### UPDATE METHOD ######
@methodics.route('/<int:method_id>/update', methods=['GET', 'POST'])
@login_required
def update(method_id):
    method = Methodics.query.get_or_404(method_id)
    if ((method.author != current_user) and (current_user.username != 'Administrator')):
        abort(403)  # Проверяем что изменения вносит автор или админ, иначе 403 (все в сад)
    # для показа названия презентации
    # presentation_filename = method.presentation
    category = Categories.query.get(method.category)

    form = UpdateMethodForm()
    # print(f'form errors:{form.errors}')
    if form.validate_on_submit():
        # Если пытаются изменить заглавную картинку
        if form.method_label_image.data:
            method_id = method.id
            pic = add_method_pic(form.method_label_image.data, method_id, method.method_label_image)
            method.method_label_image = pic

        # Если пытаются загрузить файл с ПРЕЗЕНТАЦИЕЙ формируем общий список, переводим в форма JSON и сохраняем в базу
        if form.presentation.data:
            method_id = method.id
            if method.presentation:
                presentation_files_list = json.loads(method.presentation)
            else:
                presentation_files_list = []
            presentation_filename = add_method_presentation(form.presentation.data, method_id, method.presentation)
            presentation_files_list.append(presentation_filename)
            json_presentations = json.dumps(presentation_files_list)
            method.presentation = json_presentations

        # создание превьюшек КАРТИНОК по указанным ссылкам
        print(f'image processing for method {method.id}')
        images_data = form.images.data
        wrong_links = []
        # Проверяем данные в форме и базе на совпадение, чтобы лишний раз не обрабатывать если ничего не изменилось
        if not check_url_list(form.images.data, method.images):
            image_html_links=text_format_for_html(form.images.data)
            thumb_links, wrong_links, images_data = thumbnail_for_net_pic(image_html_links, method.id)

        # обработка ссылок на Yandex.MUSIC
        print(f'music processing for method {method.id}')
        # print(f'form.music.data: {form.music.data}')
        music_data = form.music.data
        wrong_music_links = []
        if not check_url_list(form.music.data, method.music):
            music_html_links=text_format_for_html(form.music.data)
            wrong_music_links, music_data = check_music_link(music_html_links, method_id)

        # обработка ссылок на ВИДЕО
        print(f'video processing for method {method.id}')
        video_data = form.video.data
        wrong_video_links = []
        if not check_url_list(form.video.data, method.video):
            video_html_links=text_format_for_html(form.video.data)
            wrong_video_links, video_data = check_video_links(video_html_links, method_id)

        # проверка на наличие тайминга
        timing_exist = MethodTiming.query.filter_by(method_id=method_id).first()
        if timing_exist:
            timing_id = timing_exist.id
        else:
            timing_id = None

        # смотрим вбранную категорию
        curr_category = int(request.form.get('form_category'))

        method.change_date = datetime.utcnow()
        method.title = form.title.data
        method.short_desc = form.short_desc.data
        method.target = form.target.data
        method.description = form.description.data
        method.age_from = form.age_range_from.data
        method.age_till = form.age_range_till.data
        method.consumables = form.consumables.data
        method.timing_id = timing_id
        # method.presentation = form.presentation.data
        method.images = images_data
        method.music = music_data
        method.video = video_data
        method.literature = form.literature.data
        method.category = curr_category
        method.tags = form.tags.data

        db.session.commit()

        flash_text = 'Изменения и дополнения сохранены.'
        # или при необходимости показываем ругань на битые ссылки
        if len(wrong_links) == 0 and len(wrong_video_links) == 0 and len(wrong_music_links) == 0:
            flash(flash_text, 'warning')
        else:
            if len(wrong_links) != 0:
                flash_text += '<br>но ссылка на <strong>картинку</strong> (или несколько) не открывается. Проверьте правильность ссылки:<br> '
                for link in wrong_links:
                    flash_text += link + '<br>'
            if len(wrong_video_links) != 0:
                flash_text += '<br>Не обработалась ссылка/ки на <strong>видео</strong>: <br>'
                for link in wrong_video_links:
                    flash_text += link + '<br>'
            if len(wrong_music_links) != 0:
                flash_text += '<br>Cсылка/ки на <strong>музыку</strong> не похожа на HTML-код для Яндекс.музыки, проверьте: <br>'
                for link in wrong_music_links:
                    flash_text += link+ '<br>'
            flash(Markup(flash_text), 'negative')

        return redirect(url_for('methodics.method', method_id=method_id))

    # Первоначальное открытие формы на редактирование
    elif request.method == 'GET':
        # Если задан тайминг, показываем длительность занятия
        timing = MethodTiming.query.filter_by(method_id=method_id).first()
        if timing:
            form.timing_id.data = timing.duration
        else:
            form.timing_id.data = method.timing_id
        # Название категории
        category = Categories.query.get(method.category)

        form.title.data = method.title
        form.short_desc.data = method.short_desc
        form.target.data = method.target
        form.age_range_from.data = method.age_from
        form.age_range_till.data = method.age_till
        form.description.data = method.description
        form.consumables.data = method.consumables
        form.images.data = method.images
        form.music.data = method.music
        form.video.data = method.video
        form.literature.data = method.literature
        form.category.data = category
        form.tags.data = method.tags

    method_label_image = url_for('static', filename = 'methodics_pics/method_ava'+method.method_label_image)
    html_category_list = get_html_category_list()
    # Формируем список с файлами презентаций
    presentations = []
    if method.presentation:
        for presentation in json.loads(method.presentation):
            presentations.append(presentation)
    # Если форма заполненна с ошибками, а валидаторам плевать (например расширения файлов)
    print(f'form errors: {form.errors}')
    if form.errors:
        flash_text = 'Форма методики заполнена неверно. <br>'
        for error in form.errors:
            # print(form.errors[error])
            flash_text += form.errors[error][0]
        flash_text += 'К сожалению, последние изменения не сохранены. '
        flash(Markup(flash_text), 'negative')
    return render_template('update_method.html',
                            method_label_image=method.method_label_image,
                            title='Редактирование методики',
                            method_id = method.id,
                            timing_id = form.timing_id.data,
                            form=form,
                            # curr_presentation = presentation_filename,
                            category=category,
                            html_category_list=html_category_list,
                            presentations=presentations)


###### DELETE METHOD ######
@methodics.route('/<int:method_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_method(method_id):
    method = Methodics.query.get_or_404(method_id)
    if ((method.author != current_user) and (current_user.username != 'Administrator')):
        abort(403)
    # Удалем превьюшки картинок
    del_meth_folder = os.path.join(current_app.root_path, os.path.join('static', 'methodics_pics', 'method_images', 'method_'+str(method_id)))
    shutil.rmtree(del_meth_folder, ignore_errors=True)
    # Удаляем заглавную картинку для методики
    if method.method_label_image != 'default_method.png':
        del_meth_ava = os.path.join(current_app.root_path, os.path.join('static', 'methodics_pics', 'method_ava', method.method_label_image))
        os.remove(del_meth_ava)
    # Удаляем файлы презентации
    if method.presentation:
        for presentation in json.loads(method.presentation):
            filename = presentation
            curr_folder_path = os.path.join('static', 'methodics_presentations')
            directory = os.path.join(current_app.root_path, curr_folder_path, 'method_'+str(method_id))
            shutil.rmtree(directory, ignore_errors=True)
    # Определяем номер тайминга и удаляем его и его шаги
    timing_id = db.session.execute(text(f"select timing_id from methodics where id='{method_id}'")).first()[0]
    if timing_id != None:
        db.session.execute(text(f"delete from timing_steps where method_timing_id='{timing_id}'"))
        db.session.execute(text(f"delete from method_timing where id='{timing_id}'"))
    # Удалние методики, после того как разобрались с констреинтами
    db.session.delete(method)
    db.session.commit()
    flash('Методика удалена', 'success')
    return redirect(url_for('core.index'))


##### DOWNLOAD PRESENTATION #####
@methodics.route('/<int:method_id>/download')
def download_presentation(method_id):
    """
    Скачиваем презентацияю для выбранной методики
    """
    # method = Methodics.query.get_or_404(method_id)
    presentation = request.args.get('presentation')
    filename = presentation
    curr_folder_path = os.path.join('static', 'methodics_presentations')
    directory = os.path.join(current_app.root_path, curr_folder_path, 'method_'+str(method_id))
    filepath = os.path.join(directory, filename)
    return send_file(filepath, attachment_filename=filename, as_attachment=True)


##### DELETE PRESENTATION #####
@methodics.route('/<int:method_id>/presentation_delete')
def delete_presentation(method_id):
    """
    Удаляем презентацияю для выбранной методики вместе с директорией
    """
    method = Methodics.query.get_or_404(method_id)
    presentation = request.args.get('presentation')
    if ((method.author != current_user) and (current_user.username != 'Administrator')):
        abort(403)
    filename = presentation
    curr_folder_path = os.path.join('static', 'methodics_presentations')
    directory = os.path.join(current_app.root_path, curr_folder_path, 'method_'+str(method_id))
    curr_filepath = os.path.join(current_app.root_path, directory, filename)
    os.remove(curr_filepath)
    if len(os.listdir(directory)) == 0:
        shutil.rmtree(directory, ignore_errors=True)
        method.presentation = None
        db.session.commit()
    else:
        if method.presentation:
            presentations = json.loads(method.presentation)
            presentations.remove(filename)
            method.presentation = json.dumps(presentations)
            db.session.commit()
    flash('Файл презентации удален', 'warning')
    # filepath = os.path.join(directory, filename)
    return redirect(url_for('methodics.update', method_id=method_id))
