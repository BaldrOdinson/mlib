#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'

############################################################
# DATABASE SETUP
############################################################
basedir = os.path.abspath(os.path.dirname(__file__))
# строка для sqlite
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'data.sqlite')
# строка для postgresql
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://mlib:mlib1@localhost/mlib'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)

############################################################
# LOGIN CONFIGURATIONS
############################################################
login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = 'users.login'



############################################################
# BLUEPRINTS REGISTRATION
############################################################
from mlibsite.core.views import core
from mlibsite.error_pages.handlers import error_pages
from mlibsite.users.views import users
from mlibsite.methodics.views import methodics
app.register_blueprint(core)
app.register_blueprint(error_pages)
app.register_blueprint(users)
app.register_blueprint(methodics)
