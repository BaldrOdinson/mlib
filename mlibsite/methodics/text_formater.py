#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
from babel import dates
from mlibsite import db
from sqlalchemy import text
from flask import Markup
from mlibsite.models import Methodics, Categories
from sqlalchemy import or_


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
    Удаляем перенос строк из списка ссылок в базе и в форме, для сравнения,
    чтобы определить изменилось ли чтото.
    Просто так, без этого предварительного преобразования, сравнение не проходит,
    идимо из-за разных символов переноса строки
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


def create_category_dict():
    '''
    Строим словарь с категориями, где подкатегории вложены в родительские категории
    '''
    # берем все существующие категории из базы
    categories = db.session.execute(text("select * from categories")).fetchall()
    # определяем финальный словарь с деревом категорий
    category_dict = {}
    # Формируем базовый список со всеми полученными из БД категориями
    curr_categoies_list = list(categories)
    # Начинаем с категории у которой такая родительская категория 0
    base_category_parrent = 0

    # sub category
    def sub_cat_add(check_category_list):
        '''
        Для выбранной категории проверяем наличие подкатегорий и вкладываем из в список
        check_category_list: список словарей категорий для проверки
        '''
        for category in check_category_list:
            if type(category) is dict:
                sub_cat_search_list = curr_categoies_list.copy()
                curr_check_category_list = []
                for sub_category in sub_cat_search_list:
                    # Если номер текущей категории указан у кого-то в качестве родительской, его/их и выбираем
                    if sub_category[2] in category.keys():
                        cat_list = []
                        cat_temp_dict = {}
                        cat_list.append(sub_category[1])
                        cat_temp_dict[sub_category[0]] = cat_list
                        # добавляем словарь подкатегории в финальный словарь
                        category[sub_category[2]].append(cat_temp_dict)
                        # удаляем из общего списка категорий
                        curr_categoies_list.pop(curr_categoies_list.index(sub_category))
                        curr_check_category_list = category[sub_category[2]]
                # Запускаем рекурсию на поиск подкатегорий для списка текущей категории
                sub_cat_add(curr_check_category_list)

    # base category
    def add_cat_in_dict(base_category):
        """
        Формируем словарь для корневой категории
        """
        cat_list = curr_categoies_list.copy()
        curr_cat_list = []
        check_category_list = []
        for category in cat_list:
            # если родительская категория (parrent_cat) выбранной категории совпадает с рутовой категорией
            if category[2] == base_category_parrent:
                curr_cat_list.append(category[1])
                # добавляем в словарь категорий
                category_dict[category[0]] = curr_cat_list
                # удаляем из общего списка категорий
                curr_categoies_list.pop(curr_categoies_list.index(category))
                # Формируем список со словарями подкатегорий для проверки на содержание собственных побкатегорий
                check_category_list.append(category_dict)
                sub_cat_add(check_category_list)
    # RUN
    add_cat_in_dict(base_category_parrent)
    # print(f'FINAL Categories dict: {category_dict}')
    return category_dict


def get_html_category_list():
    '''
    Строим списо категорий для передачи в html с необходимыми количествами ведущих табуляций в названиях категорий и подкатегорий
    '''
    # print('run get_html_category_list')
    category_dict=create_category_dict()
    html_category_list = []

    def cat_tree(category_dict, tabs=0):
        # обрабатываем входящий список категорий
        if type(category_dict) is dict:
            category_list = list(category_dict.items())
        else:
            category_list = category_dict
        for category in category_list:
            if type(category) is not dict:
                # Подсчитываем количество методик данной категории
                # Берем все категории, у каторых выбранный id в id или parrent_cat (родительской категории)
                req_category = Categories.query.filter_by(id=category[0]).first()
                categories = Categories.query.filter(or_(Categories.id == category[0], Categories.parrent_cat == category[0]))
                categories_ids = [req_category.id]
                # строим список со всеми выбранныйми id, затем по нему формируем SQL sequences
                for cat in categories:
                    categories_ids.append(cat.id)
                count_methodics = Methodics.query.filter(Methodics.category.in_(categories_ids)).count()
                print(f'count_methodics for category {category[0]}: {count_methodics}')
                # локальная корректировка количества табуляций
                if tabs >= 1:
                # print(f'{"&emsp;"*tabs} {category[0]} {category[1][0]}')
                    html_category_list.append((category[0], Markup(f'{"&emsp;"*(tabs-1)}&bull; {category[1][0]}'), count_methodics))
                else:
                    html_category_list.append((category[0], Markup(f'{"&emsp;"*tabs}&bull; {category[1][0]}'), count_methodics))
                try:
                    tabs += 1
                    # если у категории есть подкатегории запускаем рекурсию
                    cat_tree(category[1][1:], tabs)
                except KeyError:
                    pass
            else:
                try:
                    cat_tree(category, tabs)
                except KeyError:
                    pass
    # RUN
    cat_tree(category_dict)
    return html_category_list


if __name__ == '__main__':
    pass
    # print(f'Categories: {create_category_disc()}')
