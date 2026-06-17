from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dateTime = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/signup-form', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        name    = request.form['name']
        email    = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            return "<h1>Please enter an other email because this email already exists <br> <a href='/signup'>Signup</a></h1>"

        hashed_pw = generate_password_hash(password)
        new_user  = User(username=username, email=email, name=name, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']
        user     = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/create-todo', methods=['POST'])
def ToDoForm():
    if request.method == 'POST':
        name = request.form.get('name')
        dateTime = request.form.get('dateTime')
        user_id = current_user.id
        toDo = ToDo(name=name, dateTime=dateTime, user=user_id)
        db.session.add(toDo)
        db.session.commit()
        return redirect('/dashboard')
    else:
        return redirect('/dashboard')

@app.route('/dashboard')
@login_required
def dashboard():
    toDoList = ToDo.query.filter_by(user=current_user.id)
    return render_template('dashboard.html', user=current_user, toDoList=toDoList)

@app.route('/')
def Login():
    if current_user.is_authenticated:
        return redirect('/dashboard')
    return render_template('login.html')

@app.route('/signup')
def Signup():
    return render_template('signup.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)