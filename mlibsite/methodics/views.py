#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, request, redirect, Blueprint, current_app, send_file, abort
from flask_login import current_user, login_required
from mlibsite import db
from mlibsite.models import Methodics, MethodTiming, TimingSteps
from mlibsite.methodics.forms import MethodForm, UpdateMethodForm
from mlibsite.methodics.picture_handler import add_method_pic, thumbnail_for_net_pic, img_tupal, thumbnail_list
from mlibsite.methodics.video_handler import check_video_links
from mlibsite.methodics.files_saver import add_method_presentation
from datetime import datetime
from mlibsite.methodics.text_formater import text_format_for_html, check_url_list
import os, shutil, binascii

methodics = Blueprint('methodics', __name__, template_folder='templates/methodics')


# Views

# Create
# Blog Post (view)
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
        method = Methodics(user_id=current_user.id,
                           title=form.title.data,
                           short_desc=form.short_desc.data,
                           target=form.target.data,
                           description=form.description.data,
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
        return redirect(url_for('core.index'))
    return render_template('create_method.html', form=form)


###### BLOG POST (VIEW) ######
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
    # формируем ссылку на видео
    if method.video:
        video_html_links=text_format_for_html(method.video)
        print(video_html_links)
    else:
        video_html_links = []
    method_label_image = url_for('static', filename = 'methodics_pics/method_ava'+method.method_label_image)
    return render_template('method.html',
                            title=method.title,
                            date=method.publish_date,
                            description=description_html_list,
                            short_desc=short_desc_html_list,
                            # images_links=image_html_links,
                            # images_thumb_links=thumb_links,
                            images_list=images_list,
                            method_label_image=method.method_label_image,
                            method=method,
                            videos=video_html_links)


###### UPDATE ######
@methodics.route('/<int:method_id>/update', methods=['GET', 'POST'])
@login_required
def update(method_id):
    method = Methodics.query.get_or_404(method_id)
    if ((method.author != current_user) and (current_user.username != 'Administrator')):
        abort(403)  # Проверяем что изменения вносит автор или админ, иначе 403 (все в сад)
    # для показа названия презентации
    presentation_filename = method.presentation

    form = UpdateMethodForm()

    if form.validate_on_submit():

        # Если пытаются изменить заглавную картинку
        if form.method_label_image.data:
            method_id = method.id
            pic = add_method_pic(form.method_label_image.data, method_id, method.method_label_image)
            method.method_label_image = pic

        # Если пытаются загрузить файл с презентацией
        if form.presentation.data:
            method_id = method.id
            presentation_filename = add_method_presentation(form.presentation.data, method_id, method.presentation)
            method.presentation = presentation_filename

        # создание превьюшек картинок по указанным ссылкам
        images_data = form.images.data
        wrong_links = []
        # Проверяем данные в форме и базе на совпадение, чтобы лишний раз не обрабатывать если ничего не изменилось
        if not check_url_list(form.images.data, method.images):
            image_html_links=text_format_for_html(form.images.data)
            thumb_links, wrong_links, images_data = thumbnail_for_net_pic(image_html_links, method.id)

        # обработка ссылок на видео
        video_data= form.video.data
        wrong_video_links = []
        if not check_url_list(form.video.data, method.video):
            video_html_links=text_format_for_html(form.video.data)
            wrong_video_links, video_data = check_video_links(video_html_links, method_id)

        method.change_date = datetime.utcnow()
        method.title = form.title.data
        method.short_desc = form.short_desc.data
        method.target = form.target.data
        method.description = form.description.data
        method.consumables = form.consumables.data
        method.timing_id = form.timing_id.data
        # method.presentation = form.presentation.data
        method.images = images_data
        method.music = form.music.data
        method.video = video_data
        method.literature = form.literature.data
        method.category = form.category.data
        method.tags = form.tags.data

        db.session.commit()

        flash_text = 'Изменения и дополнения сохранены. '
        # или при необходимости показываем ругань на битые ссылки
        if len(wrong_links) != 0:
            flash_text += 'но ссылка на картинку (или несколько): -> '
            for link in wrong_links:
                flash_text += link
            flash_text += ' <- не открывается. Проерьте ее. '
            flash(flash_text, 'negative')
        elif len(wrong_video_links) != 0:
            flash_text += 'Но при этом не обработалась ссылка/ки на видео: '
            for link in wrong_video_links:
                flash_text += link
            flash(flash_text, 'negative')
        else:
            flash(flash_text, 'warning')

        return redirect(url_for('methodics.method', method_id=method_id))

    # Первоначальное открытие формы на редактирование
    elif request.method == 'GET':
        # Если задан тайминг, показываем длительность занятия
        timing = MethodTiming.query.filter_by(method_id=method_id).first()
        if timing:
            form.timing_id.data = timing.duration
        else:
            form.timing_id.data = method.timing_id

        form.title.data = method.title
        form.short_desc.data = method.short_desc
        form.target.data = method.target
        form.description.data = method.description
        form.consumables.data = method.consumables
        form.images.data = method.images
        form.music.data = method.music
        form.video.data = method.video
        form.literature.data = method.literature
        form.category.data = method.category
        form.tags.data = method.tags

    method_label_image = url_for('static', filename = 'methodics_pics/method_ava'+method.method_label_image)
    return render_template('update_method.html',
                            method_label_image=method.method_label_image,
                            title='Редактирование методики',
                            method_id = method.id,
                            timing_id = form.timing_id.data,
                            form=form,
                            curr_presentation = presentation_filename)


###### DELETE ######
@methodics.route('/<int:method_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_method(method_id):
    method = Methodics.query.get_or_404(method_id)
    if ((method.author != current_user) and (current_user.username != 'Administrator')):
        abort(403)

    db.session.delete(method)
    db.session.commit()
    del_meth_folder = os.path.join(current_app.root_path, os.path.join('static', 'methodics_pics', 'method_images', 'method_'+str(method_id)))
    shutil.rmtree(del_meth_folder, ignore_errors=True)
    flash('Методика удалена', 'warning')
    return redirect(url_for('core.index'))


##### DOWNLOAD PRESENTATION #####
@methodics.route('/<int:method_id>/download')
def download_presentation(method_id):
    """
    Скачиваем презентацияю для выбранной методики
    """
    method = Methodics.query.get_or_404(method_id)
    filename = method.presentation
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
    if ((method.author != current_user) and (current_user.username != 'Administrator')):
        abort(403)
    filename = method.presentation
    curr_folder_path = os.path.join('static', 'methodics_presentations')
    directory = os.path.join(current_app.root_path, curr_folder_path, 'method_'+str(method_id))
    shutil.rmtree(directory, ignore_errors=True)
    method.presentation = None
    db.session.commit()
    flash('Файл презентации удален', 'warning')
    # filepath = os.path.join(directory, filename)
    return redirect(url_for('methodics.update', method_id=method_id))
