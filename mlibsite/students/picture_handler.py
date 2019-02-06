#! /usr/bin/env python
# -*- coding: utf-8 -*-
# pictures uploading
import os
from PIL import Image
from flask import current_app
from time import time


def add_student_pic(pic_upload, student_id, curr_pic):
    '''
    Меняем аватар участника с того что уснатовлен по умолчанию.
    Сохраняем его в static/students_pics/students_ava/student_{student_id}
    размером указанным в output_size
    '''

    filename = pic_upload.filename
    timestamp = str(time()*1000).split('.')[0]
    ext_type = filename.split('.')[-1]
    storage_filename = 'student_'+str(student_id)+'_'+timestamp+'.'+ext_type # Переименовываем картинку под текущий проект
    curr_folder_path = os.path.join('static', 'students_pics', 'students_ava') # Расставляем слеши в зависимости от OS

    filepath = os.path.join(current_app.root_path, curr_folder_path, storage_filename)
    print(f'file path for pict save (filepath): {filepath}\ncurr_folder_path: {curr_folder_path}')

    output_size = (400, 400)
    # print(f'file path for pict update (pic_upload): {pic_upload}')
    pic = Image.open(pic_upload)
    pic.thumbnail(output_size)
    pic.save(filepath, 'PNG')
    # удаляем старый файл
    curr_filepath = os.path.join(current_app.root_path, curr_folder_path, curr_pic)
    if curr_pic != 'default_student.png':
        os.remove(curr_filepath)
    return storage_filename
