from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# create and configure the app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# setup the login manager
login_manager = LoginManager()
login_manager.init_app(app)

# setup the database
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# setup the user model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))

    def __repr__(self):
        return '<User %r>' % self.username

# setup the login manager to load users
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# setup the login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember')

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=remember)
        return redirect(url_for('index'))

    return render_template('login.html')

# setup the logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# setup the signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username:
            flash('Username is required')
        elif not password:
            flash('Password is required')
        elif password != confirm_password:
            flash('Passwords do not match')
        elif User.query.filter_by(username=username).first():
            flash('Username is already taken')
        else:
            user = User(username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()

            flash('Account created successfully')
            return redirect(url_for('login'))

    return render_template('signup.html')

# setup the index route
@app.route('/')
def index():
    return render_template('index.html', current_user=current_user)

# run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
  
