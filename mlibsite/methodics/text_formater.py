#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask_babel import format_date
from babel import dates

def text_format_for_html(text):
    '''
    Разбиваем полученный из базы текст по строкам, чтобы затем вывести в форме в отдельных <p>
    Иммитация переносов строк, которые иначе проебываются, а <pre> не поддерживает bootstrap styling
    '''
    # print(f'text_format_for_html')
    with open('text_tmp.txt', 'w') as file:
        file.write(text)
    html_text_list=[]
    with open('text_tmp.txt', 'r') as file:
        for line in file.readlines():
            if line != '\n':
                html_text_list.append(line)
    os.remove('text_tmp.txt')
    # print(html_text_list)
    return html_text_list


def text_from_list(data_list):
    """
    Берем каждое значение из списка и объединяем в общий текст
    с переносом после каждого значения
    """
    data_list = list(data_list)
    combined_text = ''
    for item in data_list:
        # combined_text = combined_text + item +'\n'
        combined_text = combined_text + item
    return combined_text

def check_url_list(from_form, from_base):
    '''
    Удаляем перенос строк из списка ссылок в базе и в форме, для сравнения, чтобы определить изменилось ли чтото
    Просто так сравнение не проходит, видимо из-за разных символов переноса строки
    '''
    print('check_url_list matching')
    from_form_list = [url.rstrip() for url in from_form]
    from_form = ''
    for char in from_form_list:
        from_form += char
    if not from_base == None:
        from_base_list = [url.rstrip() for url in from_base]
        from_base = ''
        for char in from_base_list:
            from_base += char
        from_base = ('' + from_base).replace('\n', '')
    else:
        from_base = ''
    # print(f'check result if {from_form == from_base}')
    # print(f'from form:\n {from_form}')
    # print(f'from base:\n {from_base}')
    return from_form == from_base

def date_translate(date):
    return dates.format_date(date, locale='ru_RU')



if __name__ == '__main__':
    text='one\ntwo\nthree'
    text_format_for_html(text)
