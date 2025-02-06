from flask import Flask,render_template,url_for,session,redirect,flash
import functools
import sqlite3
import uuid
from passlib.hash import pbkdf2_sha256
from frameworks import *
from language_processing import get_mood
from dotenv import load_dotenv
import os
import requests
from datetime import date,timedelta
from cryptography.fernet import Fernet
load_dotenv()
app = Flask(__name__,template_folder="templates",static_folder="static")

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY").encode()
app.config["NOTES_KEY"] = os.environ.get("NOTES_KEY").encode()

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404
 
def encrypt_journal(entry:JournalEntry) -> JournalEntry:
    entry.content = Fernet(app.config["NOTES_KEY"]).encrypt(entry.content.encode()).decode()
    return entry

def decrypt_journal(entry:JournalEntry) -> JournalEntry:
    entry.content = Fernet(app.config["NOTES_KEY"]).decrypt(entry.content.encode()).decode()
    return entry

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args,**kwargs):
        if session.get("_id") is None:
            return redirect(url_for("login"))
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
            return redirect(url_for("index"))
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
        app.c.execute("INSERT INTO Users VALUES (?,?,?,?,?,?)",(uuid.uuid4().hex,form.username.data,pbkdf2_sha256.hash(form.password.data),0,date(1900,1,1),0))
        app.db.commit()
        app.db.close()
        flash("Account registered",category="success")
        return redirect(url_for('.login'))
    return render_template("register.html",form=form)

def get_quote():
        url = "https://zenquotes.io/api/random"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()[0]['q'] + " - " + response.json()[0]['a']
        return "Error fetching quote"

@app.route('/home')
@login_required
def index():
    file = open("static/quote.txt","r")
    data = file.read().split(",",1)
    file.close()
    if data[0] != date.today().strftime('%d/%m/%Y'):
        file = open("static/quote.txt","w")
        file.write(date.today().strftime('%d/%m/%Y')+","+get_quote())
        file.close()
        return redirect(url_for(".index"))
    
    app.db = sqlite3.connect("database.db")
    app.c = app.db.cursor()
    app.c.execute("SELECT * FROM Users WHERE user_id = (?)",(session.get("_id"),))
    user_data = app.c.fetchone()
    user = User(*user_data)
    app.db.commit()
    app.db.close()
    
    if (date.today() - user.last_date) > timedelta(1):
        app.db = sqlite3.connect("database.db")
        app.c = app.db.cursor()
        app.c.execute("UPDATE Users SET  streak = 0 WHERE user_id = (?)",(session.get("_id"),))
        app.db.commit()
        app.db.close()
    
    return render_template('MoodTracker.html',quote=data[1],user = user)

@app.route('/journal',methods = ["GET","POST"])
@login_required
def journal():
    app.db = sqlite3.connect("database.db")
    app.c = app.db.cursor()
    app.c.execute("SELECT * FROM Users WHERE user_id = (?)",(session.get("_id"),))
    user_data = app.c.fetchone()
    app.db.commit()
    
    app.c.execute("SELECT * FROM Journal WHERE user_ID = (?)",(session.get("_id"),))
    entries = [decrypt_journal(JournalEntry(*entry)) for entry in app.c.fetchall()]
    entries.sort()
    app.db.commit()
    
    app.db.close()
    
    user = User(*user_data)
    if user.last_date != date.today():
        form = JournalForm()
    else:
        app.db = sqlite3.connect("database.db")
        app.c = app.db.cursor()
        app.c.execute("SELECT content FROM Journal WHERE user_ID = (?) AND date = (?)",(session.get("_id"),date.today(),))
        entry = JournalFormObj(app.c.fetchone()[0])
        entry.content = Fernet(app.config["NOTES_KEY"]).decrypt(entry.content.encode()).decode()
        app.db.commit()
        form = UpdateForm(obj = entry)
        app.db.close()
        
    if form.validate_on_submit():
        if user.last_date!=date.today():
            app.db = sqlite3.connect("database.db")
            app.c = app.db.cursor()
            content = form.content.data
            app.c.execute("INSERT INTO Journal VALUES (?,?,?,?,?)",(uuid.uuid4().hex,user.user_id,Fernet(app.config["NOTES_KEY"]).encrypt(content.encode()).decode(),date.today(),get_mood(content),))
            user.last_date = date.today()
            user.streak += 1
            app.db.commit()
            app.c.execute("UPDATE Users SET last_entry = (?),streak = (?) WHERE user_ID = (?)",(user.last_date,user.streak,session["_id"],))
            app.db.commit()
            app.db.close()
        else:
            app.db = sqlite3.connect("database.db")
            app.c = app.db.cursor()
            content = form.content.data
            app.c.execute("UPDATE Journal SET content = (?),evaluation = (?) WHERE date = (?) AND user_ID = (?)",(Fernet(app.config["NOTES_KEY"]).encrypt(content.encode()).decode(),get_mood(content),date.today(),session["_id"],))
            app.db.commit()
            app.db.close()
        
        app.db = sqlite3.connect("database.db")
        app.c = app.db.cursor()
        app.c.execute("SELECT * FROM Journal WHERE user_ID = (?)",(session.get("_id"),))
        entries = [decrypt_journal(JournalEntry(*entry)) for entry in app.c.fetchall()]
        entries.sort()
        app.db.commit()
        app.db.close()
        count = 0
        summation = 0
        for entry in entries[:5]:
            summation+=entry.evaluation
            count += 1
        app.db = sqlite3.connect("database.db")
        app.c = app.db.cursor()
        app.c.execute("UPDATE Users SET mood = (?) WHERE user_ID = (?)",(summation/count,session.get("_id"),))
        app.db.commit()
        app.db.close()
        return redirect(url_for('journal'))
    return render_template('daily_journal.html', form = form, user = user,entries = entries, log = user.last_date == date.today())

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('.page_2'))

@app.route('/4-7-8')
@login_required
def breathing():
    return render_template("breathing.html")

@app.route('/')
def home():
    return render_template("index.html")
app.run(host = '0.0.0.0',port=5000)