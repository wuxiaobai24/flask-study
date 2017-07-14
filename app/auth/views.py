from flask import render_template,redirect,request,url_for,flash
from flask_login import login_user,logout_user
from . import auth
from ..models import User
from flask_login import login_required
from .forms import LoginForm,RegistrationForm
from .. import db

# 保护路由
@auth.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'

#登录路由
@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invaild username or password')
    return render_template('auth/login.html',form=form)

#登出路由
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

#注册页面路由
@auth.route('/register',methods=['POST','GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username = form.username.data,
                    password = form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)
