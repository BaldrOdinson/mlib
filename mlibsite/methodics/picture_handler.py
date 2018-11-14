# pictures uploading
import os, requests
from PIL import Image
from flask import url_for, current_app


def add_method_pic(pic_upload, method_id):

    filename = pic_upload.filename
    ext_type = filename.split('.')[-1]
    storage_filename = 'method_'+str(method_id)+'.'+ext_type # Переименовываем картинку под текущюю методику

    filepath = os.path.join(current_app.root_path, 'static\methodics_pics\method_ava', storage_filename)

    output_size = (200, 200)

    pic = Image.open(pic_upload)
    pic.thumbnail(output_size)
    pic.save(filepath)

    return storage_filename


def thumbnail_for_net_pic(img_url, method_id):
    """
    Создаем превьюшки и делаем лист с путями к ним
    """
    output_size = (300, 200)
    storage_filename = ''
    directory = os.path.join(current_app.root_path, 'static\methodics_pics\method_images', 'method_'+str(method_id))
    if not os.path.exists(directory):
        os.makedirs(directory)

    thumb_list=[]
    img_curr_no=1
    for url in img_url:
        storage_filename = 'method_'+str(method_id)+'_img'+str(img_curr_no)+'.png'
        thumb_filepath = 'methodics_pics/method_images/method_'+str(method_id)+'/'+storage_filename
        filepath = os.path.join(current_app.root_path, 'static\methodics_pics\method_images\method_'+str(method_id), storage_filename)
        r = requests.get(url)
        with open('net_img.jpg', 'wb') as net_img:
            net_img.write(r.content)
        with Image.open('net_img.jpg') as curr_image:
            curr_image.thumbnail(output_size)
            curr_image.save(filepath, "PNG")
            thumb_list.append(thumb_filepath)
            print(thumb_filepath)
        img_curr_no+=1
        os.remove('net_img.jpg')

    return thumb_list

def thumbnail_list(img_url, method_id):
    """
    Просто составляем лист со путями к превьюшкам
    """
    thumb_list=[]
    img_curr_no=1
    for url in img_url:
        storage_filename = 'method_'+str(method_id)+'_img'+str(img_curr_no)+'.png'
        thumb_filepath = 'methodics_pics/method_images/method_'+str(method_id)+'/'+storage_filename
        thumb_list.append(thumb_filepath)
        img_curr_no+=1
    return thumb_list


def img_tupal(link, thumb):
    """
    Создаем лист кортежей из url и пути к превьюшке
    """
    images_list=[]
    for i in range(len(link)):
        images_list.append((link[i], thumb[i]))
    return images_list
