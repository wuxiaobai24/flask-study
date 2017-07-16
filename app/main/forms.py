from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField,\
                    SelectField,TextAreaField
from wtforms.validators import Required,Length,Email,Regexp
from wtforms import ValidationError
from ..models import Role
class NameForm(FlaskForm):
    name = StringField('what is your name?',validators=[Required()])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    name = StringField('Real name',validators=[Length(0,64)])
    location = StringField('Location',validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class EditProfileAdminForm(FlaskForm):
    email = StringField('Email',validators=[Required(),Length(1,64),
                                            Email()])
    username = StringField('Username',validators=[Required(),
        Length(1,64),Regexp('^[A-Za-z][A-Za-z_.]*$',0,
                    'Username must have only letters, numbers,'
                    'dots or underscores')] )
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role',coerce=int)
    name = StringField('Real name',validators=[Length(0,64)])
    location = StringField('Location',validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.name)
                            for role in Role.query.filter_by(name = Role.name).all()]
        self.user = user

    def validate_email(self,field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.username.data):
            raise ValidationError('Username already registered.')
