from . import main
from flask import redirect,render_template,flash,url_for,request,abort,send_from_directory,current_app
from flask_login import login_required,current_user
from app.models import User,Role,db,Post
from .form import EditProfileForm,EditPostForm
import xlrd
from xlutils.copy import copy
from werkzeug.utils import secure_filename
import os
from app.models import Permission

@main.route('/',methods=['GET','POST'])
def index():
	form=EditPostForm()
	if request.method=="POST":
		post=Post(
			body=request.form.get('body'),
			author=current_user._get_current_object()
		)
		db.session.add(post)
		return redirect(url_for('main.index'))
	page=request.args.get('page',default=1,type=int)
	pagination=Post.query.order_by(Post.timestamp.desc()).paginate(
		page,current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False
	)
	posts=pagination.items
	return render_template('index.html',form=form,posts=posts,pagination=pagination)

@main.route('/profile/<username>')
@login_required
def profile(username):
    user=User.query.filter_by(username=username).first()
    if user is not None:
	    posts=user.posts.order_by(Post.timestamp.desc()).all()
	    return render_template('user.html',user=user,posts=posts)
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

@main.route('/upload_file',methods=["GET","POST"])
@login_required
def upload_file():
    app = current_app._get_current_object()
    if request.method=="POST":
        file=request.files.get('file')
        if file:
            filename=secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_IMG_LOCATION'],filename))
            return redirect(url_for('main.uploaded_file',filename=filename))
        else:
            abort(404)
    return redirect(url_for('main.profile',username=current_user.username))

@main.route('/uploaded_file/<filename>')
def uploaded_file(filename):
    app = current_app._get_current_object()
    return send_from_directory(app.config['UPLOAD_IMG_LOCATION'],filename)

@main.route('/edit_post',methods=['POST',"GET"])
@login_required
def edit_post():
	form=EditPostForm()
	if form.validate_on_submit() and current_user.can(Permission.WRITE_ARTICLES):
		post=Post(
			body=form.body.data,
			author=current_user._get_current_object()
		)
		db.session.add(post)
		return redirect(url_for('main.edit_post'))
	posts=current_user.posts.order_by(Post.timestamp.desc()).all()
	return render_template('edit_post.html',form=form,posts=posts)

@main.route('/edit_post/<int:id>',methods=["POST","GET"])
def edit_old_post(id):
	post=Post.query.get_or_404(id)
	form=EditPostForm()
	if form.validate_on_submit():
		post.body=form.body.data
		db.session.add(post)
		return redirect(url_for('main.profile',username=current_user.username))
	form.body.data=post.body
	return render_template('edit_post.html',form=form)

@main.route('/post/<int:id>')
def post(id):
	post=Post.query.get_or_404(id)
	return render_template('post.html',posts=[post])
