#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask import current_app


def add_attachment(attach, course_id, project_id, term_id, course_attachment):
    """
    Сохраняем прикрепленный к курсу файл
    """
    filename = attach.filename

    # Путь для сохранения прикрепленного файла
    curr_folder_path = os.path.join('static', 'project_attachments', 'project_'+str(project_id), 'term_'+str(term_id))
    # Создаем дирректорию для проекта, если такой нет
    directory = os.path.join(current_app.root_path, curr_folder_path, 'course_'+str(course_id))
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(current_app.root_path, directory, filename)
    attach.save(filepath)
    return filename


def add_lesson_attachment(attach, lesson_id, course_id, project_id, term_id, lesson_attachment):
    """
    Сохраняем прикрепленный к занятию файл
    """
    filename = attach.filename

    # Путь для сохранения прикрепленного файла
    curr_folder_path = os.path.join('static', 'project_attachments',
                                            'project_'+str(project_id),
                                            'term_'+str(term_id),
                                            'course_'+str(course_id))
    # Создаем дирректорию для проекта, если такой нет
    directory = os.path.join(current_app.root_path, curr_folder_path, 'lesson_'+str(lesson_id))
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(current_app.root_path, directory, filename)
    attach.save(filepath)
    return filename
