from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


class Permission:
    FOLLOW=0x01
    COMMIT=0x02
    WRITE_ARTICLES=0x04
    MODERATE_COMMENTS=0x08
    ADMINISTER=0x80

class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    rolename=db.Column(db.String(64),index=True,unique=True)
    default=db.Column(db.Boolean)
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
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(64),index=True,unique=True)
    username=db.Column(db.String(128),unique=True,index=True)
    password_hash=db.Column(db.String(128))
    confirmed=db.Column(db.Boolean,default=False)

    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))

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


from . import login_manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))