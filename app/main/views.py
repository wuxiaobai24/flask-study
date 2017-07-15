from datetime import datetime
from flask import render_template,session,redirect,url_for,flash,current_app
from flask_login import current_user,login_required
from . import main
from .forms import NameForm,EditProfileForm
from .. import db
from ..models import User
from ..emails import send_mail,text_send_mail


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
