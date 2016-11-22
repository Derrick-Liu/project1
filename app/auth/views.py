from . import auth
from flask import render_template,redirect,session,url_for
from .forms import LoginForm

@auth.route('/login',methods=["POST","GET"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        session['name']=form.name.data
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html',form=form,name=session.get('name'))