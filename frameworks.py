from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,EmailField,SubmitField,StringField
from wtforms.validators import InputRequired,EqualTo,Length,Email,Regexp

class RegistorForm(FlaskForm):
    username = StringField("Username",validators=[InputRequired()],render_kw={"placeholder": "Required"})
    password = PasswordField("Password",validators=[InputRequired(),Length(min=12,message="Password mus be at least 12 characters long."),Regexp(r'^[a-zA-Z0-9\s]*$',message="Only letters, numbers, and spaces are allowed.")],render_kw={"placeholder": "Required, min 12 characters"})
    confirm_password = PasswordField("Confirm Password",validators=[InputRequired(),EqualTo("password",message="Passwords do not match"),Regexp(r'^[a-zA-Z0-9\s]*$',message="Only letters, numbers, and spaces are allowed.")],render_kw={"placeholder": "Required"})
    submit = SubmitField("Register")
    
    
class LoginForm(FlaskForm):
    username = StringField("Username",validators=[InputRequired(),Regexp(r'^[a-zA-Z0-9\s]*$',message="Only letters, numbers, and spaces are allowed.")],render_kw={"placeholder": "Required"})
    password = PasswordField("Password",validators=[InputRequired(),Length(min=12,message="Password must be at least 12 characters long."),Regexp(r'^[a-zA-Z0-9\s]*$',message="Only letters, numbers, and spaces are allowed.")],render_kw={"placeholder": "Required"})
    submit = SubmitField("Login")
    
    
class User:
    def __init__(self,user_id:str,username:str,password:str,mood:float):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.mood = mood
    
        