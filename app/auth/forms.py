from flask_wtf import Form
from wtforms import StringField,SubmitField,TextAreaField,PasswordField,BooleanField
from wtforms.validators import DataRequired,email,Length

class LoginForm(Form):
    name=StringField('What is your name?',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired(),Length(1,64)])
    remember_me=BooleanField('Remember me')
    submit=SubmitField('Submit')

