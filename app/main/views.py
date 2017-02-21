from . import main
from flask import redirect,render_template,flash,url_for
from flask_login import login_required,current_user
from app.models import User,Role,db
from .form import EditProfileForm
import xlrd
from xlutils.copy import copy

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile/<username>')
@login_required
def profile(username):
    user=User.query.filter_by(username=username).first()
    if user is not None:
        return render_template('user.html',user=user)
    else:
        flash('%s is not registered!'%username)
        return redirect(url_for('main.index'))

@main.route('/<username>/edit_profile',methods=['POST','GET'])
@login_required
def edit_profile(username):
    form=EditProfileForm()
    user=User.query.filter_by(username=username).first()
    if form.validate_on_submit():
        user.username=form.username.data
        user.age=form.age.data
        user.date_of_born=form.date_of_born.data
        user.gender=form.gender.data
        user.selfintr=form.selfintr.data
        user.address=form.address.data
        user.email=form.email.data

        db.session.add(user)

        profilelist=[
            form.username.data,
            form.age.data,
            form.gender.data,
            form.date_of_born.data,
            form.address.data,
            form.email.data,
            form.selfintr.data
        ]
        rb = xlrd.open_workbook('D:\\development\\git\\myproject\\test1.xls')
        wb = copy(rb)
        wb_sheet = wb.get_sheet(0)
        for i in range(len(profilelist)):
            wb_sheet.write(user.id, i, profilelist[i])
        wb.save('D:\\development\\git\\myproject\\test1.xls')
        return redirect(url_for('main.profile',username=current_user.username))
    form.username.data=user.username
    form.age.data=user.age
    form.gender.data=user.gender
    form.date_of_born.data=user.date_of_born
    form.address.data=user.address
    form.email.data=user.email
    form.selfintr.data=user.selfintr
    return render_template('edit_profile.html',form=form)
