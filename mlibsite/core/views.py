#! /usr/bin/env python
# -*- coding: utf-8 -*-
from mlibsite.models import Methodics
from flask import render_template, request, Blueprint
from mlibsite.methodics.text_formater import text_format_for_html, date_translate, get_html_category_list

core = Blueprint('core', __name__, template_folder='templates/core')

@core.route('/')
def index():
    # pagination
    per_page=9
    page = request.args.get('page', 1, type=int)
    short_desc_html_list_dict = {}
    # methodics = Methodics.query.order_by(Methodics.publish_date.desc()).paginate(page=page, per_page=per_page)
    methodics = Methodics.query.order_by(Methodics.change_date.desc()).paginate(page=page, per_page=per_page)
    methodics_whole = Methodics.query.order_by(Methodics.change_date.desc())[page*per_page-per_page:page*per_page]
    for method in methodics_whole:
        short_desc_html_list_dict[method.id] = text_format_for_html(method.short_desc)
    html_category_list = get_html_category_list()
    return render_template('index.html',
                            short_desc_dict=short_desc_html_list_dict,
                            methodics=methodics,
                            date_translate=date_translate,
                            html_category_list=html_category_list)


@core.route('/info')
def info():
    return render_template('info.html')
