from flask import render_template,redirect,request,url_for,flash
from flask_login import login_user,logout_user
from . import auth
from ..models import User
from flask_login import login_required,current_user
from .forms import LoginForm,RegistrationForm
from .. import db
from ..emails import send_mail
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
        token = user.generate_confirmation_token()
        send_mail(user.email,'Confirm Your Account',
                'auth/email/confirm',user=user,token=token)
        flash('A confirm email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)

#Confirm 路由
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed you account. Thanks!')
    else:
        flash('The confirmation link is invaild or has expired.')
    return redirect(url_for('main.index'))

# 限制未确认用户的行为
@auth.before_app_request
def befor_request():
    if current_user.is_authenticated \
        and not current_user.confirmed \
        and request.endpoint[:5] != 'auth.' \
        and request.endpoint != 'static':
        print("befor_request redirect!!!")
        return redirect(url_for('auth.unconfirmed'))

# 未确认页面路由
@auth.route('unconfirmed')
def unconfirmed():
    #print('unconfirmed!!!')
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('/auth/unconfirmed.html')

# 重新发生账户邮件 路由
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email,'Confirm You Account',
            'auth/email/confirm',user=current_user,token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))
