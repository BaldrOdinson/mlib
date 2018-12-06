#! /usr/bin/env python
# -*- coding: utf-8 -*-
from mlibsite import db, app
from flask_user import UserMixin, SQLAlchemyAdapter, UserManager
from datetime import datetime


### Авторы ###
class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password = db.Column(db.String(255), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')
    email = db.Column(db.String(64), unique=True, index=True)
    confirmed_at = db.Column(db.DateTime())
    # addition information
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone_num = db.Column(db.String(64), unique=True, index=True)
    address = db.Column(db.String(254))
    curr_job_place = db.Column(db.String(254))
    karma = db.Column(db.Integer, nullable=False, default=0)
    profile_image = db.Column(db.String(64), nullable=False, default='default_profile.png')
    # Relationships
    posts = db.relationship('Methodics', backref='author', lazy=True)

    def __repr__(self):
        return f'Username {self.username}'


############################################################
# USER CONFIGURATIONS
############################################################
db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)


### Методики ###
class Methodics(db.Model):

    __tablename__ = 'methodics'
    # Юзеры ссылающиеся на эту методику, хз
    users = db.relationship(User)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    publish_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    change_date = db.Column(db.DateTime)
    title = db.Column(db.String(256), nullable=False)
    short_desc = db.Column(db.Text, nullable=False)
    target = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    consumables = db.Column(db.Text)
    timing_id = db.Column(db.Integer)
    method_label_image = db.Column(db.String(64), nullable=False, default='default_method.png')
    presentation = db.Column(db.String(256))
    images = db.Column(db.Text)
    music = db.Column(db.Text)
    video = db.Column(db.Text)
    literature = db.Column(db.Text)
    category = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, default=1)
    tags = db.Column(db.Text)

    def __init__(self, user_id, title, short_desc, target, description,  category, tags):
        self.user_id = user_id
        self.title = title
        self.short_desc = short_desc
        self.target = target
        self.description = description
        self.category = category
        self.tags = tags

    def __repr__(self):
        return f'Post ID: {self.id} -- Date {self.date} -- {self.title}'


### Категории для методик ###
class Categories(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(256), nullable=False)
    parrent_cat = db.Column(db.Integer, nullable=False, default=0)
    # Relationships
    methodics = db.relationship('Methodics', backref='category_methodics', lazy=True)

    def __init__(self, category_name):
        self.category_name = category_name


### Тайминг занятия ###
class MethodTiming(db.Model):
    __tablename__ = 'method_timing'

    id = db.Column(db.Integer, primary_key=True)
    method_id = db.Column(db.Integer, db.ForeignKey('methodics.id'), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    # Relationships
    steps = db.relationship('TimingSteps', backref='steps', lazy=True)

    def __init__(self, method_id, duration):
        self.method_id = method_id
        self.duration = duration


### Этапы занятия ###
class TimingSteps(db.Model):
    __tablename__ = 'timing_steps'

    id = db.Column(db.Integer, primary_key=True)
    method_timing_id = db.Column(db.Integer, db.ForeignKey('method_timing.id'), nullable=False)
    step_duration = db.Column(db.Integer, nullable=False)
    step_desc = db.Column(db.Text, nullable=False)
    step_result = db.Column(db.Text, nullable=False)
    step_label_image = db.Column(db.String(64), nullable=False, default='default_step.png')

    def __init__(self, method_timing_id, step_duration, step_desc, step_result):
        self.method_timing_id = method_timing_id
        self.step_duration = step_duration
        self.step_desc = step_desc
        self.step_result = step_result
