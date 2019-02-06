#! /usr/bin/env python
# -*- coding: utf-8 -*-
# pictures uploading
import os
from PIL import Image
from flask import current_app
from time import time


def add_course_pic(pic_upload, course_id, curr_pic):
    '''
    Меняем заглавную картинку для проекта с той что уснатовленна по умолчанию.
    Сохраняем ее в static/projects_pics/project_courses/course_{course_id}
    размером указанным в output_size
    '''

    filename = pic_upload.filename
    timestamp = str(time()*1000).split('.')[0]
    ext_type = filename.split('.')[-1]
    storage_filename = 'course_'+str(course_id)+'_'+timestamp+'.'+ext_type # Переименовываем картинку под текущий курс
    curr_folder_path = os.path.join('static', 'projects_pics', 'project_courses') # Расставляем слеши в зависимости от OS

    filepath = os.path.join(current_app.root_path, curr_folder_path, storage_filename)
    print(f'file path for pict save (filepath): {filepath}\ncurr_folder_path: {curr_folder_path}')

    output_size = (400, 400)
    # print(f'file path for pict update (pic_upload): {pic_upload}')
    pic = Image.open(pic_upload)
    pic.thumbnail(output_size)
    pic.save(filepath, 'PNG')
    # удаляем старый файл
    curr_filepath = os.path.join(current_app.root_path, curr_folder_path, curr_pic)
    if curr_pic != 'default_course.png':
        os.remove(curr_filepath)
    return storage_filename
