#! /usr/bin/env python
# -*- coding: utf-8 -*-
# video uploading
import os, requests
from flask import url_for, current_app
from time import time
from mlibsite.methodics.text_formater import text_from_list
import youtube_dl

def check_video_links(video_html_links):
    """
    Берем все предложенные ссылки на видео,
    выбираем те что ведут на youtube
    и пытаемся получить info  про видео по ссылке
    Если info не получено, ссылку бракуем.
    Остальные, успешно прошедшие проверку (т.е. на которые получено info), публикуем.
    """
    wrong = []
    video_data = []
    for link in video_html_links:
        print(f'Link in check_video_link: {link}')
        if link[:4] == 'http':
            if 'https://www.youtube.com/' in link:
                # Проверяем что ссылка на видео живая
                ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
                try:
                    with ydl:
                        result = ydl.extract_info(link, download=False) # We just want to extract the info
                        link = link.replace('watch?v=', 'embed/')
                        if link[:-1] == '\n':
                            video_data.append(link[:-1])
                        else:
                            video_data.append(link)
                # except youtube_dl.utils.DownloadError:
                except:
                    wrong.append(link)
            else:
                wrong.append(link)
        else:
            wrong.append(link)
    video_data_str = text_from_list(video_data)
    print(video_data_str)
    return wrong, video_data_str
