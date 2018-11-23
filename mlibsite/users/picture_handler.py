#! /usr/bin/env python
# -*- coding: utf-8 -*-
# pictures uploading
import os
from PIL import Image
from flask import url_for, current_app
from time import time

def add_profile_pic(pic_upload, username, profile_image):
    """
    Берем загруженную в формы картинку, изменяем размер, сохраняем по адресу в static
    """

    filename = pic_upload.filename
    timestamp = str(time()*1000).split('.')[0]
    ext_type = filename.split('.')[-1]
    storage_filename = str(username)+'_'+timestamp+'.'+ext_type # Переименовываем картинку под текущего юзера
    folder_path = os.path.join('static', 'profile_pics')

    filepath = os.path.join(current_app.root_path, folder_path, storage_filename)

    output_size = (200, 200)

    pic = Image.open(pic_upload)
    pic.thumbnail(output_size)
    pic.save(filepath, 'PNG')
    # Удаляем старую картинку
    curr_filepath = os.path.join(current_app.root_path, folder_path, profile_image)
    if profile_image != 'default_profile.png':
        os.remove(curr_filepath)

    return storage_filename
