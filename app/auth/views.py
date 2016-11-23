from . import auth
from flask import render_template,redirect,session,url_for,flash
from .forms import LoginForm,RegisterForm
from ..models import User,Role,db

@auth.route('/login',methods=["POST","GET"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        session['name']=form.username.data
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html',form=form,name=session.get('name'))

@auth.route('/register',methods=["POST","GET"])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        user=User(username=form.username.data,
                  password=form.password.data)
        db.session.add(user)
        flash('You can login now.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)