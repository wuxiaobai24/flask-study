from flask import render_template,redirect,request,url_for,flash
from flask_login import login_user,logout_user
from . import auth
from ..models import User
from flask_login import login_required,current_user
from .forms import LoginForm,RegistrationForm,ChangePasswordForm
from .forms import ResetPasswordForm,ResetPasswordNowForm
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

#修改密码
@auth.route('/change_password',methods=['POST','GET'])
@login_required
def change_password():
    print('change_password')
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.newpassword.data
        db.session().commit()
        flash('Chang Password Success!')
        return redirect(url_for('main.index'))
    return render_template('auth/change_password.html',form=form)

#重设密码
@auth.route('/reset_password',methods=['POST','GET'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        token = user.generate_confirmation_token()
        user.confirmed = False
        db.session.commit()
        send_mail(email,'Reset Your Password',
            'auth/email/reset_password',name = user.username ,token = token)
        flash('A confirm email has been sent to you by email')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form = form)

#重设密码 Confirm
@auth.route('/confirm/<name>/<token>')
def reset_password_confirm(name,token):
    user = User.query.filter_by(username = name).first()
    if user:
        if user.confirmed:
            return redirect(url_for('main.index'))
        if user.confirm(token):
            flash('You can reset your password now!')
            return redirect(url_for('auth.reset_password_now',name=user.username))
        else:
            flash('The confirmation link is invaild or has expired.')
            return redirect(url_for('auth.reset_password'))
    else:
        return render_template('404.html'),400

#重设密码 now
@auth.route('/reset_password/now/<name>',methods=['POST','GET'])
def reset_password_now(name):
    user = User.query.filter_by(username=name).first()
    if user is None:
        flash('User does not exist')
        return redirect('main.index')
    elif not user.confirmed:
        flash('Reset error,please try again.')
        return redirect('auth.reset_password')
    else:
        form = ResetPasswordNowForm()
        if form.validate_on_submit():
            user.password = form.newpassword.data
            user.confirmed = True
            db.session.commit()
            flash('Reset Success!')
            return redirect(url_for('auth.login'))

        return render_template('auth/reset_password_now.html',form = form)
