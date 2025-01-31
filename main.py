from flask import Flask,render_template,url_for,session,redirect,current_app,flash
import functools
import sqlite3
import uuid
from passlib.hash import pbkdf2_sha256
from frameworks import RegistorForm,LoginForm,User
from dotenv import load_dotenv
import os
load_dotenv()
app = Flask(__name__,template_folder="templates",static_folder="static")


app.config["SECRET_KEY"]=os.environ.get("SECRET_KEY")

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args,**kwargs):
        if session.get("username") is None:
            return redirect(url_for("page_1"))
        return route(*args,**kwargs)
    return route_wrapper

@app.route('/page_1')
def page_1():
    return render_template("first_page.html")

@app.route('/page_2')
def page_2():
    return render_template("second_page.html")


@app.route('/page_3')
def page_3():
    return render_template("third_page.html")

@app.route("/login",methods=["GET","POST"])
def login():
    
    if session.get("_id"):
        return redirect(url_for('.index'))
    form = LoginForm()
    if form.validate_on_submit():
        app.db = sqlite3.connect("database.db")
        app.c = app.db.cursor()
        app.c.execute("SELECT * FROM Users WHERE username = (?)",(form.username.data,))
        user_data = app.c.fetchone()
        app.db.commit()
        app.db.close()
        
        if not user_data:
            flash("⚠ Login credentials are incorrect",category="danger")
            return redirect(url_for('.login'))
        user = User(*user_data)
        if user and pbkdf2_sha256.verify(form.password.data,user.password):
            session["_id"] = user.user_id
            session["username"] = user.username
        flash("⚠ Login credentials are incorrect",category="danger")
        return redirect(url_for('.login'))
    return render_template("login.html",form=form)
        
@app.route('/register',methods=["GET","POST"])
def register():
    if session.get("_id"):
        return redirect(url_for('.index'))
    form = RegistorForm()
    if form.validate_on_submit():
        app.db = sqlite3.connect("database.db")
        app.c = app.db.cursor()
        app.c.execute("SELECT * FROM Users WHERE username = (?)",(form.username.data,))
        user_data = app.c.fetchone()
        app.db.commit()
        app.db.close()
        if user_data:
            flash("⚠ Username already exists",category="danger")
            return redirect(url_for('.register'))
        app.db = sqlite3.connect("database.db")
        app.c = app.db.cursor()
        app.c.execute("INSERT INTO Users VALUES (?,?,?,?)",(uuid.uuid4().hex,form.username.data,pbkdf2_sha256.hash(form.password.data),0))
        app.db.commit()
        app.db.close()
        flash("Account registered",category="success")
        return redirect(url_for('.login'))
    return render_template("register.html",form=form)


@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('.page_2'))

app.run(host = '0.0.0.0',port=5000)