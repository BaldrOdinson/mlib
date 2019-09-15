#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_babel import Babel

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'

############################################################
# DATABASE SETUP
############################################################
basedir = os.path.abspath(os.path.dirname(__file__))
# строка для postgresql
app.congig.from_pyfile('db_config.cfg')
# app.config['SQLALCHEMY_DATABASE_URI']='postgresql://mlib:mlib1@localhost/mlib'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CSRF_ENABLED'] = True
app.config['USER_ENABLE_EMAIL'] = True
app.config['USER_ENABLE_CONFIRM_EMAIL'] = True
app.config['USER_APP_NAME'] = 'M-LIB'  # For using in mail
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_FORGOT_PASSWORD_ENDPOINT'] = 'core.index'
app.config['USER_AFTER_RESET_PASSWORD_ENDPOINT'] = 'user.login'
app.config['USER_AFTER_LOGOUT_ENDPOINT'] = 'core.index'
# Mail settings
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)
Migrate(app, db)
mail = Mail(app)
# translation
app.config['BABEL_DEFAULT_LOCALE'] = 'ru'
babel = Babel(app)

# Use the browser's language preferences to select an available translation
@babel.localeselector
def get_locale():
    translations = [str(translation) for translation in babel.list_translations()]
    # return request.accept_languages.best_match(translations)
    return 'ru'


############################################################
# BLUEPRINTS REGISTRATION
############################################################
from mlibsite.core.views import core
from mlibsite.error_pages.handlers import error_pages
from mlibsite.users.views import users
from mlibsite.methodics.views import methodics
from mlibsite.timing.views import timing
from mlibsite.projects.views import projects
from mlibsite.courses.views import courses
from mlibsite.students.views import students
from mlibsite.comments.views import comments
app.register_blueprint(core)
app.register_blueprint(error_pages)
app.register_blueprint(users)
app.register_blueprint(methodics)
app.register_blueprint(timing)
app.register_blueprint(projects)
app.register_blueprint(courses)
app.register_blueprint(students)
app.register_blueprint(comments)
