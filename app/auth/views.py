from . import auth
from flask import render_template,redirect,session,url_for,flash,request
from .forms import LoginForm,RegisterForm
from ..models import User,Role,db
from flask_login import login_required,logout_user,login_user,current_user
from ..email import send_email
import xlrd
from xlutils.copy import copy

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
        list=[form.username.data,form.age.data,form.gender.data,form.date_of_born.data,
              form.address.data,form.email.data]
        user=User(username=list[0],
                  password=form.password.data,
                  address=list[4],
                  gender=list[2],
                  age=list[1],
                  date_of_born=list[3],
                  email=list[5])
        db.session.add(user)
        db.session.commit()
        token=user.generate_confirmation_token()
        send_email(user.email,'New User','mail/confirm-mail',user=user,token=token)

        #add the information into excel
        rb=xlrd.open_workbook('test1.xls')
        wb=copy(rb)
        wb_sheet=wb.get_sheet(0)
        for j in range(len(list)):
            wb_sheet.write(user.id,j,list[j])
        wb.save('test1.xls')
        flash('You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed is True:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account!')
    else:
        flash('The confirmation link is invalid')
    return redirect(url_for('main.index'))