#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, url_for, flash, request, redirect, Blueprint, current_app
from flask_login import current_user, login_required
from mlibsite import db
from mlibsite.models import Methodics
from mlibsite.methodics.forms import MethodForm, UpdateMethodForm
from mlibsite.methodics.picture_handler import add_method_pic, thumbnail_for_net_pic, img_tupal, thumbnail_list
from datetime import datetime
from mlibsite.methodics.text_formater import text_format_for_html
import os, shutil

methodics = Blueprint('methodics', __name__, template_folder='templates/methodics')


# Views

# Create
# Blog Post (view)
# Update
# Delete

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
                           consumables=form.consumables.data,
                           timing_id=form.timing_id.data,
                           presentation=form.presentation.data,
                           images=form.images.data,
                           music=form.music.data,
                           video=form.video.data,
                           literature=form.literature.data,
                           category=form.category.data,
                           tags=form.tags.data)

        db.session.add(method)
        db.session.commit()
        flash('Методика добавлена')
        return redirect(url_for('core.index'))
    return render_template('create_method.html', form=form)


###### BLOG POST (VIEW) ######
@methodics.route('/method_<int:method_id>')  # <int: - для того чтобы номер методики точно был integer
def method(method_id):
    method = Methodics.query.get_or_404(method_id)
    # разделяем преформатированный текст на строки, так как переносы не обрабатываются
    description_html_list=text_format_for_html(method.description)
    short_desc_html_list=text_format_for_html(method.short_desc)
    # создание превьюшек картинок по указанным ссылкам
    # получаем данные из формы, бъем их по строкам, делаем список из путей к превьюшкам и список с сылками
    # затем делаем список кортежей с линком и путём к превьюшке, который отправляем в форму для отображения
    image_html_links=text_format_for_html(method.images)
    if method.images:
        thumb_links=thumbnail_list(image_html_links, method.id)
        images_list=img_tupal(image_html_links, thumb_links)
    else:
        images_list=[]
        # print(f'images_list: {images_list}')
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
                            method=method)


###### UPDATE ######
@methodics.route('/<int:method_id>/update', methods=['GET', 'POST'])
@login_required
def update(method_id):
    method = Methodics.query.get_or_404(method_id)
    if method.author != current_user: # Проверяем что изменения вносит автор, иначе 403 (все в сад)
        abort(403)

    form = UpdateMethodForm()

    if form.validate_on_submit():
        # Если пытаются изменить заглавную картинку
        if form.method_label_image.data:
            # print(f'Path from form: {form.method_label_image.data}')
            method_id = method.id
            pic = add_method_pic(form.method_label_image.data, method_id, method.method_label_image)
            method.method_label_image = pic

        # создание превьюшек картинок по указанным ссылкам
        images_data = form.images.data
        wrong_links = []
        if form.images.data != method.images:
            image_html_links=text_format_for_html(form.images.data)
            thumb_links, wrong_links, images_data = thumbnail_for_net_pic(image_html_links, method.id)
            # images_list=img_tupal(image_html_links, thumb_links)

        method.change_date = datetime.utcnow()
        method.title = form.title.data
        method.short_desc = form.short_desc.data
        method.target = form.target.data
        method.description = form.description.data
        method.consumables = form.consumables.data
        method.timing_id = form.timing_id.data
        method.presentation = form.presentation.data
        method.images = images_data
        method.music = form.music.data
        method.video = form.video.data
        method.literature = form.literature.data
        method.category = form.category.data
        method.tags = form.tags.data

        db.session.commit()

        flash_text = 'Изменения и дополнения сохранены '
        if len(wrong_links) != 0:
            flash_text += 'но ссылка на картинку (или несколько): -> '
            for link in wrong_links:
                flash_text += link
            flash_text += ' <- не открывается. Проерьте ее.'
        flash(flash_text)
        return redirect(url_for('methodics.method', method_id=method_id))
    elif request.method == 'GET':

        form.title.data = method.title
        form.short_desc.data = method.short_desc
        form.target.data = method.target
        form.description.data = method.description
        form.consumables.data = method.consumables
        form.timing_id.data = method.timing_id
        form.presentation.data = method.presentation
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
                            form=form)


###### DELETE ######
@methodics.route('/<int:method_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_method(method_id):
    method = Methodics.query.get_or_404(method_id)
    if method.author != current_user:
        abort(403)

    db.session.delete(method)
    db.session.commit()
    del_meth_folder = os.path.join(current_app.root_path, os.path.join('static', 'methodics_pics', 'method_images', 'method_'+str(method_id)))
    shutil.rmtree(del_meth_folder, ignore_errors=True)
    flash('Методика удалена')
    return redirect(url_for('core.index'))
