from . import auth
from flask import render_template,redirect,session,url_for,flash,request
from .forms import LoginForm,RegisterForm
from ..models import User,Role,db
from flask_login import login_required,logout_user,login_user,current_user

@auth.route('/login',methods=["POST","GET"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user is not None and user.checkout_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html',form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

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