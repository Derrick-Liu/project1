from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,PasswordField,BooleanField,ValidationError
from wtforms.validators import DataRequired,Length,EqualTo,Email
from ..models import User,Role

class LoginForm(FlaskForm):
    username=StringField('What is your name?',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired(),Length(1,64)])
    remember_me=BooleanField('Remember me')
    submit=SubmitField('Submit')

class RegisterForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(1,64)])
    password=PasswordField('Password',validators=[DataRequired(),Length(1,32),
                                                  EqualTo('password2',message='Passwords must match')])
    password2=PasswordField('Confirm password',validators=[DataRequired()])
    age=StringField('Age',validators=[])
    gender=StringField('Gender',validators=[Length(1,32)])
    date_of_born=StringField('Date of born',validators=[])
    address=StringField('Address',validators=[])
    email=StringField('Email',validators=[DataRequired(),Email()])
    selfintr=TextAreaField('Self-introduce')
    submit=SubmitField('Submit')

    def validate_name(self,field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('Username already in use ')