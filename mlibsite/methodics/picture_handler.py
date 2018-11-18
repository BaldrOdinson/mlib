#! /usr/bin/env python
# -*- coding: utf-8 -*-
# pictures uploading
import os, requests
from PIL import Image
from flask import url_for, current_app
from time import time
from mlibsite.methodics.text_formater import text_from_list


def add_method_pic(pic_upload, method_id, curr_pic):
    '''
    Меняем заглавную картинку для методики с той что уснатовленна по умолчанию.
    Сохраняем ее в static\methodics_pics\method_ava\method_{method.id}
    размером указанным в output_size
    '''

    filename = pic_upload.filename
    timestamp = str(time()*1000).split('.')[0]
    ext_type = filename.split('.')[-1]
    storage_filename = 'method_'+str(method_id)+'_'+timestamp+'.'+ext_type # Переименовываем картинку под текущюю методику
    curr_folder_path = os.path.join('static', 'methodics_pics', 'method_ava') # Расставляем слеши в зависимости от OS

    filepath = os.path.join(current_app.root_path, curr_folder_path, storage_filename)
    print(f'file path for pict save (filepath): {filepath}\ncurr_folder_path: {curr_folder_path}')

    output_size = (200, 200)
    # print(f'file path for pict update (pic_upload): {pic_upload}')
    pic = Image.open(pic_upload)
    pic.thumbnail(output_size)
    pic.save(filepath, 'PNG')
    # удаляем старый файл
    curr_filepath = os.path.join(current_app.root_path, curr_folder_path, curr_pic)
    if curr_pic != 'defailt_method.png':
        os.remove(curr_filepath)
    return storage_filename


def thumbnail_for_net_pic(img_url, method_id):
    """
    Создаем превьюшки и делаем лист с путями к ним
    """
    output_size = (300, 200)
    storage_filename = ''
    curr_folder_path = os.path.join('static', 'methodics_pics', 'method_images')
    directory = os.path.join(current_app.root_path, curr_folder_path, 'method_'+str(method_id))
    if not os.path.exists(directory):
        os.makedirs(directory)
    # ссылки
    images_data = []
    # пути к превьюшкам
    thumb_list=[]
    # битые ссылки
    wrong_links=[]
    img_curr_no=1
    timestamp = str(time()*1000).split('.')[0]
    old_thimbs = os.listdir(directory)
    for url in img_url:
        storage_filename = 'method_'+str(method_id)+'_img'+str(img_curr_no)+'_'+timestamp+'.png'
        thumb_filepath = 'methodics_pics/method_images/method_'+str(method_id)+'/'+storage_filename
        filepath = os.path.join(current_app.root_path, curr_folder_path, 'method_'+str(method_id), storage_filename)
        try:
            r = requests.get(url)
            with open('net_img.jpg', 'wb') as net_img:
                net_img.write(r.content)
            with Image.open('net_img.jpg') as curr_image:
                curr_image.thumbnail(output_size)
                curr_image.save(filepath, "PNG")
                thumb_list.append(thumb_filepath)
                images_data.append(url)
                # print(thumb_filepath)
            img_curr_no+=1
            os.remove('net_img.jpg')
        except:
            wrong_links.append(url)
    for old_file in old_thimbs:
        curr_filepath = os.path.join(current_app.root_path, curr_folder_path, 'method_'+str(method_id), old_file)
        os.remove(curr_filepath)
    # Преобразуем лист images_data с корректными ссылками в строку
    images_data_str = text_from_list(images_data)
    return thumb_list, wrong_links, images_data_str

def thumbnail_list(img_url, method_id):
    """
    Просто составляем лист с путями к превьюшкам
    """
    curr_folder_path = os.path.join('static', 'methodics_pics', 'method_images')
    directory = os.path.join(current_app.root_path, curr_folder_path, 'method_'+str(method_id))
    thumb_list=[]
    thumb_file_list = os.listdir(directory)
    thumb_file_list.sort()
    for thumb in thumb_file_list:
        thumb_filepath = 'methodics_pics/method_images/method_'+str(method_id)+'/'+thumb
        thumb_list.append(thumb_filepath)
    return thumb_list


def img_tupal(link, thumb):
    """
    Создаем лист кортежей из url и пути к превьюшке для передачи форме
    """
    images_list=[]
    for i in range(len(link)):
        images_list.append((link[i], thumb[i]))
    return images_list
