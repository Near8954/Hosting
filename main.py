from flask import Flask, redirect, render_template, request, url_for
from data import db_session
from data.users import User
from forms.user import LoginForm, RegisterForm
from flask_login import LoginManager, login_required, login_user, logout_user
import os
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Ightksdlcz_endfignxkurjkfj7892046'

login_manager = LoginManager()
login_manager.init_app(app)

user_name = ''


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def start_page():
    param = {}
    param['username'] = 'пользователь'
    param['title'] = "Home page"
    return render_template('home_page.html', **param)


@app.route('/home_page/<username>_file_upload', methods=['POST', 'GET'])
def sample_file_upload(username):
    UPLOAD_PATH = f'static/img/{username}/'
    if request.method == 'GET':
        return render_template('file_load.html')
    elif request.method == 'POST':
        f = request.files['file']
        print(f.filename)
        open(os.path.join(UPLOAD_PATH, f.filename), 'wb').write(f.read())
        return redirect(f'/home_page/{username}')


@app.route('/home_page/<username>', methods=['POST', 'GET'])
def home_page(username):
    if request.method == 'POST':
        return redirect(f'/home_page/{username}_file_upload')
    param = {}
    param['username'] = username
    param['title'] = "Home page"
    return render_template('home_page.html', **param)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        os.mkdir(path=f'static/img/{user.name}')
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/show_photo/', methods=['GET', 'POST'])
def show_photo():
    username = user_name

    ans = '<!DOCTYPE html><html><head><meta charset="utf-8">' \
          '<title>Мои изображения</title></head><body>' \
        f'<form action="/home_page/{username}">' \
          '<button name="button">Вернуться на главную страницу</button>' \
          '</from>'
    photos = list()
    os.chdir(f'static/img/{username}')
    for root, dirs, files in os.walk("."):
        for filename in files:
            photos.append(filename)
    os.chdir('..')
    os.chdir('..')
    os.chdir('..')

    for photo in photos:
        im = Image.open(f'static/img/{username}/{photo}')
        ans += f'''<p><img src='/static/img/{username}/{photo}' width="800"
        style="vertical-align:middle"
    ><br>Filename: {photo};<br>Original size: {im.size}</p>'''

    ans += '</body></html>'

    return ans


@app.route('/login', methods=['GET', 'POST'])
def login():
    global user_name
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user_name = user.name

            return redirect(f"/home_page/{user.name}")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(debug=True)
