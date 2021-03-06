from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField,SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[Required(),Length(1,64),Email()])
    password = PasswordField('Password',validators=[Required()])
    remember_me = BooleanField('Keep me logged in.')
    submit = SubmitField('Log in')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators = [Required(),Length(1,64),Email()])

    username  = StringField('Username',validators = [
        Required(),Length(1,64),Regexp('^[a-zA-Z0-9_.-]*$',0,
            'Usernames must have only letters, '
            'numbers, dots or underscores')])
    password = PasswordField('Password',validators = [
        Required(),EqualTo('password2',message='Passwords must match.')])
    password2 = PasswordField('Comfirm password',validators = [Required()] )
    submit = SubmitField('Register')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class ChangePasswordForm(FlaskForm):
    oldpassword = PasswordField('Old Password',validators = [Required(),
        Length(1,64)])
    newpassword = PasswordField('New Password',validators = [Required(),
        Length(1,64),EqualTo('newpassword2','New passwords must match.')])
    newpassword2 = PasswordField('Confirm password',validators = [Required(),
        Length(1,64)])
    submit = SubmitField('Change Password')

class ResetPasswordForm(FlaskForm):
    email = StringField('Your Email:',validators=[Required(),
        Length(1,64),Email()])
    submit = SubmitField('Submit')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Can not find this email.')

class ResetPasswordNowForm(FlaskForm):
    newpassword = PasswordField('New Password',validators = [Required(),
        Length(1,64),EqualTo('newpassword2','New passwords must match.')])
    newpassword2 = PasswordField('Confirm password',validators = [Required(),
        Length(1,64)])
    submit = SubmitField('Change Password')
