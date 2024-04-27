#for any error in flask_login install this pip install git+https://github.com/maxcountryman/flask-login.git
from flask import Flask,render_template,flash,request,redirect,url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
import secrets
from sqlalchemy.sql import func
from flask_login import UserMixin,current_user,login_user,logout_user,login_required,LoginManager
from werkzeug.security import generate_password_hash,check_password_hash
import json
def secret_key():
    key = secrets.token_hex(10)
    return key

app = Flask(__name__,template_folder="template")
app.config['SECRET_KEY'] = secret_key()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Note(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True),default = func.now())
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    firstname = db.Column(db.String(150),unique = True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    notes = db.relationship('Note')

@app.route('/home',methods = ['GET','POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note)<1:
            flash('Note is too short!',category = 'error')
        else:
            new_note = Note(data = note,user_id = current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!',category = 'success')
    return render_template("home.html",user = current_user)

@app.route('/delete-note',methods = ['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
    return jsonify({})


@app.route('/login',methods = ["GET","POST"])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password1')

        user = User.query.filter_by(email = email).first()
        if user:
            if check_password_hash(user.password,password):
                flash(f"Logged in Successfully",category = "success")
                login_user(user,remember = True)
                return redirect(url_for("home"))

            else:
                flash("Password Incorrect",category = "error")
        else:
            flash("User does not exist",category="error")
    return render_template("login.html",user = current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("login.html",user = current_user)

@app.route('/signup',methods = ["GET","POST"])
def signup():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email = email).first()

        if user:
            flash("Email already exists.",category = "error")
        elif len(email)<4:
            flash('Email must be greater than 4 characters',category = 'error')
        elif len(firstname)<2:
            flash('Firstname must be greater than 1 characters',category = 'error')
        elif password1 != password2:
            flash('Password mismatch',category = 'error')
        elif len(password1)<7:
            flash('Password must be at least 7 characters')
        else:
            new_user = User(email=email,firstname = firstname,password = generate_password_hash(password1,method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created',category='success')
            return redirect(url_for('home'))
    return render_template("signup.html",user = current_user)

if __name__ == '__main__':
    app.run(debug = True)