#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask import current_app


def add_attachment(attach, student_id, student_attachment):
    """
    Сохраняем прикрепленный к курсу файл
    """
    filename = attach.filename

    # Путь для сохранения прикрепленного файла
    curr_folder_path = os.path.join('static', 'student_attachments')
    # Создаем дирректорию для проекта, если такой нет
    directory = os.path.join(current_app.root_path, curr_folder_path, 'student_'+str(student_id))
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(current_app.root_path, directory, filename)
    attach.save(filepath)
    return filename
