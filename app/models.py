from app import db
from flask import current_app,request
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
from flask_login import UserMixin,AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer  as Serializer
from datetime import datetime
import hashlib #生成hash值

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)  )

class Permission:
    FOLLOW = 0x01
    COMMIT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINSTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique = True)
    default = db.Column(db.Boolean,default=False,index=True)
    permission = db.Column(db.Integer)
    users = db.relationship('User',backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User':(Permission.FOLLOW |
                    Permission.COMMIT |
                    Permission.WRITE_ARTICLES, True),
            'Moderator':(Permission.FOLLOW |
                        Permission.COMMIT |
                        Permission.WRITE_ARTICLES |
                        Permission.MODERATE_COMMENTS,False),
            'Administrator':(0xff,False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permission = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True) #id 主键
    email = db.Column(db.String(64),unique=True, index=True) #邮箱
    username = db.Column(db.String(64),unique=True, index = True) # 昵称
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id')) #role_id,外键
    password_hash = db.Column(db.String(128)) # 密码的hash值
    confirmed = db.Column(db.Boolean,default=False) #账户是否确认，用在认证中
    name = db.Column(db.String(64)) #真实姓名
    location = db.Column(db.String(64)) #住址
    about_me = db.Column(db.Text()) #介绍
    #db.Column的default可以接受函数，每次要生成default值是调用函数来生成
    member_since = db.Column(db.DateTime(),default=datetime.utcnow)#注册时间
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)#最后访问的时间
    avatar_hash = db.Column(db.String(32))

    def ping(self):
        """刷新用户最后访问的时间"""
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                print('Admin is '+self.username)
                self.role = Role.query.filter_by(permission=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8').hexdigest()
            )

    def can(self,permission):
        return self.role is not None and \
                (self.role.permission & permission) == permission

    def is_administrator(self):
        return self.can(Permission.ADMINSTER)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return '<User %r>' % self.username

    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})

    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    #用来生成用户头像地址
    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
                            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
        url=url,hash=hash,size=size,default=default,rating=rating
        )

# 匿名访问者
class AnonymousUser(AnonymousUserMixin):
    def can(self,permission):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
