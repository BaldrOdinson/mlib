#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
from time import time
from flask import current_app


def add_method_presentation(presentation, method_id, method_presentation):
    """
    Сохраняем презентацию
    """
    filename = presentation.filename
    # timestamp = str(time()*1000).split('.')[0]
    # ext_type = filename.split('.')[-1]

    # Путь для сохранения презентации
    curr_folder_path = os.path.join('static', 'methodics_presentations')
    # Создаем дирректорию для презентации, если такой нет
    directory = os.path.join(current_app.root_path, curr_folder_path, 'method_'+str(method_id))
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        old_files = os.listdir(directory)
        for old_file in old_files:
            curr_filepath = os.path.join(current_app.root_path, directory, old_file)
            os.remove(curr_filepath)

    filepath = os.path.join(current_app.root_path, directory, filename)
    presentation.save(filepath)
    return filename
