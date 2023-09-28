from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileRequired,FileAllowed
from wtforms import StringField, SubmitField,TextAreaField,PasswordField
from wtforms.validators import Email, DataRequired,EqualTo,Length

class RegForm(FlaskForm):
    fullname = StringField("Fullname",validators=[DataRequired(message="The firstname is a must")])
    email =StringField("Email",validators=[Email(message="invalid email format"),DataRequired(message="Email must be supplied")])
    pwd =PasswordField("Enter Password",validators=[DataRequired()])
    confpwd=PasswordField("Confirm Password",validators=[EqualTo('pwd',message="both password must match")])
    btnsubmit = SubmitField("Register!")

class DpForm(FlaskForm):
    dp= FileField("Upload a profile picture",validators=[FileRequired(),FileAllowed(['jpg','png','jpeg'])])
    btnupload=SubmitField("Upload picture")

class ProfileForm(FlaskForm):
    fullname = StringField("Fullname",validators=[DataRequired(message="The firstname is a must")])
    btnsubmit = SubmitField("Update Profile!")

class ContactForm(FlaskForm):
    email = StringField("Email Address",validators=[DataRequired()])
    btnsubmit = SubmitField("Contact!")

class DonationForm(FlaskForm):
    fullname=StringField("Fullname",validators=[DataRequired("Fullname cannot be empty")])
    email = StringField("Email Address",validators=[Email(message="Enter correct email format"),DataRequired("Email must be supplied")])
    amt = StringField("Amount",validators=[DataRequired("Amount field cannot be empty")])
    btnsubmit=SubmitField("Continue")