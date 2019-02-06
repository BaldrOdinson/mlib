#! /usr/bin/env python
# -*- coding: utf-8 -*-
from mlibsite import db, app
from flask_user import UserMixin, SQLAlchemyAdapter, UserManager
from flask_login import current_user
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
    methodics = db.relationship('Methodics', backref='author', lazy=True)

    def __repr__(self):
        return f'Username {self.username}'


############################################################
# USER CONFIGURATIONS
############################################################
db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)


### Роли пользователей ###
class UserRole(db.Model):

    __tablename__ = 'user_role'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    item_type = db.Column(db.Integer, nullable=False)
    item_type_desc = db.Column(db.String(256))
    role_type = db.Column(db.Integer, nullable=False)
    role_type_desc = db.Column(db.String(256))
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    change_date = db.Column(db.DateTime)

    def __init__(self, user_id, item_id, item_type, role_type, item_type_desc, role_type_desc):
        self.user_id = user_id
        self.item_id = item_id
        self.item_type = item_type
        self.role_type = role_type
        self.item_type_desc = item_type_desc
        self.role_type_desc = role_type_desc

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
    age_from = db.Column(db.Integer)
    age_till = db.Column(db.Integer)
    short_desc = db.Column(db.Text, nullable=False)
    target = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    consumables = db.Column(db.Text)
    timing_id = db.Column(db.Integer)
    method_label_image = db.Column(db.String(64), nullable=False, default='default_method.png')
    presentation = db.Column(db.Text)
    images = db.Column(db.Text)
    music = db.Column(db.Text)
    video = db.Column(db.Text)
    literature = db.Column(db.Text)
    category = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, default=1)
    tags = db.Column(db.Text)

    def __init__(self, user_id, title, age_from, age_till, short_desc, target, description, category, tags):
        self.user_id = user_id
        self.title = title
        self.age_from = age_from
        self.age_till = age_till
        self.short_desc = short_desc
        self.target = target
        self.description = description
        self.category = category
        self.tags = tags

    def __repr__(self):
        return f'Method ID: {self.id} -- Date {self.date} -- {self.title}'


### Категории для методик ###
class Categories(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(256), nullable=False)
    parrent_cat = db.Column(db.Integer, nullable=False, default=0)
    # Relationships
    methodics = db.relationship('Methodics', backref='category_methodics', lazy=True)

    def __init__(self, category_name, parrent_cat):
        self.category_name = category_name
        self.parrent_cat = parrent_cat


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
    step_seq_number = db.Column(db.String(256))
    step_duration = db.Column(db.Integer, nullable=False)
    step_desc = db.Column(db.Text, nullable=False)
    step_result = db.Column(db.Text, nullable=False)
    step_label_image = db.Column(db.String(64), nullable=False, default='default_step.png')

    def __init__(self, method_timing_id, step_duration, step_desc, step_result, step_seq_number=''):
        self.method_timing_id = method_timing_id
        self.step_seq_number = step_seq_number
        self.step_duration = step_duration
        self.step_desc = step_desc
        self.step_result = step_result


######################
#####  PROJECTS  #####
######################

### Проекты ###
class Projects(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    short_desc = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    label_image = db.Column(db.String(128), nullable=False, default='default_project.png')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    moders_list = db.Column(db.Text)
    contacts_info = db.Column(db.Text)
    address = db.Column(db.Text)
    note = db.Column(db.Text)
    web_links = db.Column(db.Text)
    attach = db.Column(db.Text)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    change_date = db.Column(db.DateTime)

    def __init__(self, name, short_desc, author_id):
        self.name = name
        self.short_desc = short_desc
        self.author_id = author_id

    def __repr__(self):
        return f'Project: {self.name}'


### Периоды занятий (семестр/смена/итп) ###
class Term(db.Model):
    __tablename__ = 'term'

    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=False)
    label_image = db.Column(db.String(128), nullable=False, default='default_term.png')
    start_date = db.Column(db.DateTime)
    finish_date = db.Column(db.DateTime)

    def __init__(self, project_id, name, description, start_date, finish_date):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.start_date = start_date
        self.finish_date = finish_date
        self.created_by = current_user.id


### Курс занятий ###
class Courses(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    name = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=False)
    label_image = db.Column(db.String(128), nullable=False, default='default_course.png')
    start_date = db.Column(db.DateTime)
    finish_date = db.Column(db.DateTime)
    contacts_info = db.Column(db.Text)
    address = db.Column(db.Text)
    tutors = db.Column(db.Text)
    students_group_id = db.Column(db.Integer, db.ForeignKey('students_group.id'))
    web_links = db.Column(db.Text)
    note = db.Column(db.Text)
    attach = db.Column(db.Text)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    change_date = db.Column(db.DateTime)

    def __init__(self, project_id, term_id, name, description, start_date, finish_date):
        self.project_id = project_id
        self.term_id = term_id
        self.name = name
        self.description = description
        self.start_date = start_date
        self.finish_date = finish_date
        self.created_by = current_user.id


### Занятие ###
class Lessons(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    label_image = db.Column(db.String(128), nullable=False, default='default_lesson.png')
    lesson_date = db.Column(db.DateTime)
    start_time = db.Column(db.Time)
    finish_time = db.Column(db.Time)
    method_id = db.Column(db.Integer, db.ForeignKey('methodics.id'))
    tutors = db.Column(db.Text)
    absent_students_list = db.Column(db.Text)
    web_links = db.Column(db.Text)
    note = db.Column(db.Text)
    attach = db.Column(db.Text)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    change_date = db.Column(db.DateTime)

    def __init__(self, course_id, description, lesson_date, start_time, finish_time):
        self.course_id = course_id
        self.description = description
        self.lesson_date = lesson_date
        self.start_time = start_time
        self.finish_time = finish_time
        self.created_by = current_user.id


### Группы студентов ###
class StudentsGroup(db.Model):
    __tablename__ = 'students_group'

    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    moders_list = db.Column(db.Text)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    change_date = db.Column(db.DateTime)

    def __init__(self, description, author_id):
        self.description = description
        self.author_id = author_id
        self.created_by = current_user.id


### Студенты ###
class Students(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=False)
    age = db.Column(db.String(32))
    birthday = db.Column(db.DateTime)
    sex = db.Column(db.String(32))
    phone_num = db.Column(db.String(64))
    email = db.Column(db.String(64))
    address = db.Column(db.Text)
    avatar = db.Column(db.String(128), nullable=False, default='default_student.png')
    document_dict = db.Column(db.Text)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    change_date = db.Column(db.DateTime)
    note = db.Column(db.Text)
    attach = db.Column(db.Text)

    def __init__(self, first_name, last_name, age): #, birthday, phone_num, email, address, note):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.phone_num = ''
        self.email = ''
        self.address = ''
        self.created_by = current_user.id



### Состав групп студентов ###
class Learning_groups(db.Model):
    __tablename__ = 'learning_groups'

    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('students_group.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, group_id, student_id, course_id, term_id, project_id):
        self.group_id = group_id
        self.student_id = student_id
        self.created_by = current_user.id
        self.course_id = course_id
        self.term_id = term_id
        self.project_id = project_id
