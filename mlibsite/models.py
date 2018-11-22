#! /usr/bin/env python
# -*- coding: utf-8 -*-
from mlibsite import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

### Авторы ###
class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    phone_num = db.Column(db.String(64), unique=True, index=True)
    address = db.Column(db.String(254))
    curr_job_place = db.Column(db.String(254))
    karma = db.Column(db.Integer, nullable=False, default=0)
    password_hash = db.Column(db.String(128))
    profile_image = db.Column(db.String(64), nullable=False, default='default_profile.png')
    # Relationships
    posts = db.relationship('Methodics', backref='author', lazy=True)

    def __init__(self, username, first_name, last_name, email, phone_num, address, curr_job_place, password):
     self.username = username
     self.first_name = first_name
     self.last_name = last_name
     self.email = email
     self.phone_num = phone_num
     self.address = address
     self.curr_job_place = curr_job_place
     self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'Username {self.username}'


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
    presentation = db.Column(db.String(64))
    images = db.Column(db.Text)
    music = db.Column(db.Text)
    video = db.Column(db.Text)
    literature = db.Column(db.Text)
    category = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, default=1)
    tags = db.Column(db.Text)

    def __init__(self, user_id, title, short_desc, target, description, consumables, timing_id,
                 presentation, images, music, video, literature, category, tags):
        self.user_id = user_id
        self.title = title
        self.short_desc = short_desc
        self.target = target
        self.description = description
        self.consumables = consumables
        self.timing_id = timing_id
        self.presentation = presentation
        self.images = images
        self.music = music
        self.video = video
        self.literature = literature
        self.category = category
        self.tags = tags


    def __repr__(self):
        return f'Post ID: {self.id} -- Date {self.date} -- {self.title}'


### Категории для методик ###
class Categories(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(256), nullable=False)
    parrent_cat = db.Column(db.String(256), nullable=False, default='root')
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
