from datetime import datetime
from flask import render_template,session,redirect,url_for,flash,current_app
from flask_login import current_user,login_required
from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm
from .. import db
from ..models import User,Role
from ..emails import send_mail,text_send_mail
from ..decorators import admin_required

@main.route('/',methods=['GET','POST'])
def index():
    #current_app.config['SECRET_KEY'] = 'wuxiaobai24'
    #current_app.secret_key = 'wuxiaobai24'
    #current_app.config['SESSION_TYPE'] = 'filesystem'
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known'] = False
            if current_app.config['FLASKY_ADMIN']:
                send_mail(current_app.config['FLASKY_ADMIN'],'New User','mail/new_user',user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data=''
        return redirect(url_for('.index')) #加上一个点 或 main.
    return render_template('index.html',form=form,name = session.get('name'),
                        known = session.get('known',False),
                        current_time=datetime.utcnow())

#资料页面路由
@main.route('/user/<name>')
def user(name):
    user  = User.query.filter_by(username=name).first()
    if user is None:
        abort(404)
    return render_template('user.html',user=user)

#测试使用
@main.route('/email')
def email():
    text_send_mail()
    return redirect(url_for('.index'))

# 资料编辑路由
@main.route('/eidt-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user',name=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form=form)

# Admin 资料编辑
@main.route('/edit-profile/<int:id>',methods=['POST','GET'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id) #如果没找到会返回404错误
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user',name=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role.id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html',form=form,user=user)
