from flask import Flask,render_template,url_for,session,redirect,current_app
import functools
import sqlite3

app = Flask(__name__,template_folder="templates",)
current_app.db = sqlite3.connect("database.db")
current_app.c = current_app.db.cursor()

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args,**kwargs):
        if session.get("email") is None:
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



@app.route('/')
@login_required
def root():
    return render_template('second_page.html')

@app.route('/login')
def login():
    

app.run(host='0.0.0.0',port=5000)