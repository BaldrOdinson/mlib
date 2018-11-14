#user's views
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from mlibsite import db
from mlibsite.models import User, Methodics
from mlibsite.users.forms import RegistrationForm, LoginForm, UpdateUserForm
from mlibsite.users.picture_handler import add_profile_pic

users = Blueprint('users', __name__, template_folder='templates/users')

# register
# login
# logout
# account (update UserForm)
# user's list of Blog posts

##### REGISTER #####
@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        # Создаем экземпляр класса User из данных полученно формы
        user = User(username=form.username.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    phone_num=form.phone_num.data,
                    address=form.address.data,
                    curr_job_place=form.curr_job_place.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Thanks for registration!')
        return redirect(url_for('users.login'))

    return render_template('register.html', form=form)

##### LOGIN ######
@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first() # Проверка на существование юзера в базе

        if user.check_password(form.password.data) and user is not None: # Проверка пароля
            login_user(user)
            flash('Log in Success!')

            next = request.args.get('next') # Переход туда куда до этого хотел юзер
            if next == None or not next[0]=='/':
                next = url_for('core.index')
            return redirect(next)
    return render_template('login.html', form=form)


##### LOGOUT #####
@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.index'))


##### ACCOUNT #####
@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateUserForm()

    if form.validate_on_submit():

        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data, username)
            current_user.profile_image = pic

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone_num = form.phone_num.data
        current_user.address = form.address.data
        current_user.curr_job_place = form.curr_job_place.data

        db.session.commit()
        flash('User Account Updated.')
        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.phone_num.data = current_user.phone_num
        form.address.data = current_user.address
        form.curr_job_place.data = current_user.curr_job_place

    profile_image = url_for('static', filename = 'profile_pics/'+current_user.profile_image)
    return render_template('account.html', profile_image=profile_image, form=form)


##### Методики конкретного автора #####
@users.route('/<username>')
def user_methodics(username):
    page = request.args.get('page', 1, type=int) # пригодится если страниц дохера, делаем разбивку по страницам
    user = User.query.filter_by(username=username).first_or_404()
    methodics = Methodics.query.filter_by(author=user).order_by(Methodics.publish_date.desc()).paginate(page=page, per_page=6) # Сортируем по уменьшающейся дате, выводим по 5 постов на страницу
    return render_template('user_methodics.html', methodics=methodics, user=user)
