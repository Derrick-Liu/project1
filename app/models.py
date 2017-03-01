from . import db
from flask_login import UserMixin,AnonymousUserMixin,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,url_for
from datetime import datetime
import bleach
from markdown import markdown
import random

class Permission:
    FOLLOW=0x01
    COMMIT=0x02
    WRITE_ARTICLES=0x04
    MODERATE_COMMENTS=0x08
    ADMINISTER=0x80

class Follow(db.Model):
	__tablename__='follows'
	followed_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
	follower_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
	timestamp=db.Column(db.DateTime(),default=datetime.utcnow)

class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    rolename=db.Column(db.String(64),index=True,unique=True)
    default=db.Column(db.Boolean,default=False)
    permission=db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles={
            'User':(Permission.FOLLOW|Permission.COMMIT|Permission.WRITE_ARTICLES,True),
            'Moderate':(Permission.FOLLOW|Permission.COMMIT|Permission.WRITE_ARTICLES|
                        Permission.MODERATE_COMMENTS,False),
            'Administrator':(Permission.FOLLOW|Permission.COMMIT|Permission.WRITE_ARTICLES|
                        Permission.MODERATE_COMMENTS|Permission.ADMINISTER,False)
        }
        for key in roles:
            role=Role.query.filter_by(rolename=key).first()
            if role is None:
                role=Role(rolename=key)
            role.permission = roles[key][0]
            role.default = roles[key][1]
            db.session.add(role)
        db.session.commit()


class User(UserMixin,db.Model):
	__tablename__='users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(128), unique=True, index=True)
	gender = db.Column(db.String(32))
	address = db.Column(db.String(128))
	age=db.Column(db.Integer)
	date_of_born = db.Column(db.String(32))
	password_hash = db.Column(db.String(128))
	email = db.Column(db.String(64))
	selfintr=db.Column(db.String(256))
	role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
	confirmed=db.Column(db.Boolean,default=False)
	member_since=db.Column(db.DateTime(),default=datetime.utcnow)
	last_login=db.Column(db.DateTime(),default=datetime.utcnow)

	head_img=db.Column(db.String)

	comments=db.relationship('Comment',backref='author',lazy='dynamic')
	posts=db.relationship('Post',backref='author',lazy='dynamic')
	followers=db.relationship('Follow',foreign_keys=[Follow.followed_id],
							  backref=db.backref('follower',lazy='joined'),
							  lazy='dynamic',
							  cascade='all,delete-orphan')
	followed=db.relationship('Follow',foreign_keys=[Follow.follower_id],
							 backref=db.backref('followed',lazy='joined'),
							 lazy='dynamic',
							 cascade='all,delete-orphan')
	def followers_count(self):
		return self.followers.count()

	def followed_count(self):
		return self.followed.count()

	def is_following(self,user):
		return self.followed.filter_by(followed_id=user.id).first() is not None

	def is_followed_by(self,user):
		return self.followers.filter_by(follower_id=user.id).first() is not None

	def follow(self,user):
		if not self.followed_by(user):
			follow=Follow(
				follower_id=self.id,
				followed_id=user.id
			)
			db.session.add(follow)

	def unfollow(self,user):
		if self.is_following(user):
			follow=self.followed.filter_by(followed_id=user.id).first()
			db.session.delete(follow)

	@property
	def followed_posts(self):
		return Post.query.join(Follow,Follow.followed_id==Post.author_id).filter(Follow.follower_id==self.id)

	def  __init__(self,**kwargs):
		super(User,self).__init__(**kwargs)
		if self.role is None:
			if self.email==current_app.config['FLASKY_ADMIN']:
				self.role=Role.query.filter_by(permission=0xff).first()
			if self.role is None:
				self.role=Role.query.filter_by(default=True).first()

	def can(self,permission):
		return self.role is not None and (self.role.permission&permission)==permission

	def is_administrator(self):
		return self.can(Permission.ADMINISTER)

	@property
	def password(self):
		raise AttributeError('Password can not be read!')

	@password.setter       # Enable to set password
	def password(self,password):
		self.password_hash=generate_password_hash(password)

	def checkout_password(self,password):
		return check_password_hash(self.password_hash, password)

	def generate_confirmation_token(self,expiration=3600):
		s=Serializer(current_app.config['SECRET_KEY'],expiration)
		token=s.dumps({'confirm':self.id})
		return token

	def confirm(self,token):
		s=Serializer(current_app.config['SECRET_KEY'])
		try:
			data=s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed=True
		db.session.add(self)
		return True
	@staticmethod
	def generate_fake(count=100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py

		seed()
		for i in range(count):
			j = random.randint(1, 48)
			u=User(
				username=forgery_py.internet.user_name(True),
				email=forgery_py.internet.email_address(),
				password=forgery_py.lorem_ipsum.word(),
				confirmed=True,
				address=forgery_py.address.city(),
				selfintr=forgery_py.lorem_ipsum.sentence(),
				member_since=forgery_py.date.date(True),
				head_img = url_for('static', filename='head_img/%d.jpg' % j)
			)
			db.session.add(u)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()

	@staticmethod
	def change_head_img():
		count=User.query.count()
		for i in range(3,count+1):
			j = random.randint(1, 48)
			user=User.query.get_or_404(i)
			user.head_img=url_for('static',filename='head_img/%d.jpg'%j)
			db.session.add(user)
			db.session.commit()




# class AnonymousUser(AnonymousUserMixin):
# 	def can(self,permissions):
# 		return False
# 	def is_administrator(self):
# 		return False
# login_manager.anonymous_user=AnonymousUser()

from . import login_manager
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class Post(db.Model):
	__tablename__='posts'
	id=db.Column(db.Integer,primary_key=True)
	body=db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow())
	author_id=db.Column(db.Integer,db.ForeignKey('users.id'))

	comments=db.relationship('Comment',backref='post',lazy='dynamic')

	@staticmethod
	def on_changed_body(target,value,oldvalue,initiator):
		allowed_tags=['a','abbr','acronym','b','blockquote','code','em','i','li','ol','pre','strong','ul','h1','h2','h3','p']
		target.body_html=bleach.linkify(bleach.clean(markdown(value,output_format='html'),tags=allowed_tags,strip=True))

	@staticmethod
	def generate_fake(count=100):
		from random import seed, randint
		import forgery_py
		seed()
		user_count=User.query.count()
		for i in range(count):
			u=User.query.offset(randint(0,user_count-1)).first()
			p=Post(body=forgery_py.lorem_ipsum.sentences(randint(1,3)),
			       author=u,
			       timestamp=forgery_py.date.date(True))
			db.session.add(p)
			db.session.commit()

db.event.listen(Post.body,'set',Post.on_changed_body)

class Comment(db.Model):
	__tablename__='comments'
	id=db.Column(db.Integer,primary_key=True)
	body=db.Column(db.Text)
	body_html=db.Column(db.Text)
	timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)

	post_id=db.Column(db.Integer,db.ForeignKey('posts.id'))
	author_id=db.Column(db.Integer,db.ForeignKey('users.id'))

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong',
						'ul', 'h1', 'h2', 'h3', 'p']
		target.body_html = bleach.linkify(
			bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))

	@staticmethod
	def generate_fake(count=1000):
		from random import seed, randint
		import forgery_py
		seed()
		post_count = Post.query.count()
		user_count=User.query.count()
		for i in range(count):
			u = User.query.offset(randint(0, user_count - 1)).first()
			p=Post.query.offset(randint(0,post_count-1)).first()
			c = Comment(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
						author=u,
						post=p,
						timestamp=forgery_py.date.date(True))
			db.session.add(c)
			db.session.commit()
db.event.listen(Comment.body,'set',Comment.on_changed_body)
