#! /usr/bin/env python
# -*- coding: utf-8 -*-
from mlibsite.methodics.text_formater import text_from_list

def take_music_url(music_list):
    music_url_list = []
    for link in music_list:
        if 'iframe' in link and 'src="' in link:
            link_start_pos = link.index('src="')
            # Добываем ширину и высоту плагина
            width_start_pos = link.index('width')
            width = ''
            for char in link[width_start_pos+6:]:
                if char in ['0','1','2','3','4','5','6','7','8','9', '%', 'p', 'x']:
                    width += char
                else:
                    break
            height_start_pos = link.index('height')
            height = ''
            for char in link[height_start_pos+7:]:
                if char in ['0','1','2','3','4','5','6','7','8','9', '%', 'p', 'x']:
                    height += char
                else:
                    break
            # Добываем url
            music_url = ''
            for char in link[link_start_pos+5:]:
                if char != '"':
                    music_url += char
                else:
                    break
            styled_music_url = (width, height, music_url)
            music_url_list.append(styled_music_url)
        else:
            print(f'Bad link for music: {link}')
    return music_url_list

def check_music_link(music_html_links, method_id):
    wrong_music_links = []
    music_data = []
    for link in music_html_links:
        if '<iframe' in link and 'src="https://music.yandex.ru/iframe/' in link:
            music_data.append(link)
        else:
            wrong_music_links.append(link)
    # Превращаем лист с правильными ссылками в строку для корректного сохранения в базе
    music_data_str = text_from_list(music_data)
    return wrong_music_links, music_data_str


if __name__ == '__main__':
    music_list = ['<iframe frameborder="0" style="border:none;width:600px;height:100px;" width="600" height="100" src="https://music.yandex.ru/iframe/#track/33850962/4144207/">Слушайте <a href="https://music.yandex.ru/album/4144207/track/33850962">I am Yours</a> — <a href="https://music.yandex.ru/artist/38138">Jason Mraz</a> на Яндекс.Музыке</iframe>']
    music_url_list = take_music_url(music_list)
    print(f'FINALY: music_url_list = {music_url_list}')
