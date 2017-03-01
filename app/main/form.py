from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SubmitField
from wtforms.validators import DataRequired,Email,Length,ValidationError
from flask_login import current_user
from app.models import User,Role

class EditProfileForm(FlaskForm):
	username=StringField('Username',validators=[DataRequired()])
	age = StringField('Age', validators=[])
	gender=StringField('Gender')
	date_of_born = StringField('Date of born', validators=[])
	address = StringField('Address', validators=[])
	email = StringField('Email', validators=[DataRequired(),Email()])
	selfintr=TextAreaField('Self-introduce')
	submit = SubmitField('Submit')

	def validate_username(self,field):
		if field.data!=current_user.username and User.query.filter_by(username=field.data).first():
			raise ValidationError('Username %s already exists'%field.data)

class EditPostForm(FlaskForm):
	body=TextAreaField('Edit your post:',validators=[DataRequired(),Length(min=5)])
	submit=SubmitField('Submit')

class CommentsForm(FlaskForm):
	body=TextAreaField("Make comments here:",validators=[DataRequired(),Length(min=5)])
	submit=SubmitField('Submit')


