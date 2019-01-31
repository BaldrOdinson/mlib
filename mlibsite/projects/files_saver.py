#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
from time import time
from flask import current_app


def add_attachment(attach, project_id, project_attachment):
    """
    Сохраняем презентацию
    """
    filename = attach.filename

    # Путь для сохранения прикрепленного файла
    curr_folder_path = os.path.join('static', 'project_attachments')
    # Создаем дирректорию для проекта, если такой нет
    directory = os.path.join(current_app.root_path, curr_folder_path, 'project_'+str(project_id))
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(current_app.root_path, directory, filename)
    attach.save(filepath)
    return filename
