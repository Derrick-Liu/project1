from flask_wtf import Form
from wtforms import StringField,SubmitField,TextAreaField,PasswordField,BooleanField,ValidationError
from wtforms.validators import DataRequired,email,Length,EqualTo,Email
from ..models import User,Role

class LoginForm(Form):
    username=StringField('What is your name?',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired(),Length(1,64)])
    remember_me=BooleanField('Remember me')
    submit=SubmitField('Submit')

class RegisterForm(Form):
    username=StringField('Username',validators=[DataRequired(),Length(1,64)])
    age=StringField('Age',validators=[DataRequired()])
    gender=StringField('Gender',validators=[DataRequired(),Length(1,32)])
    date_of_born=StringField('Date of born',validators=[DataRequired()])
    address=StringField('Address',validators=[DataRequired()])
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired(),Length(1,32),
                                                  EqualTo('password2',message='Passwords must match')])
    password2=PasswordField('Confirm password',validators=[DataRequired()])
    submit=SubmitField('Submit')

    def validate_name(self,field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('Username already in use ')