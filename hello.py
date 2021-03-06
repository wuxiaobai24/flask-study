from flask import Flask,render_template,session,redirect,url_for,flash
from flask_script import Manager,Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
from flask_mail import Mail,Message
import os
from threading import Thread

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string.'
app.config['SQLALCHEMY_DATABASE_URI']=\
    'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# for mail
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = '25'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
# 在命令行下定义两个这两个变量
# > export MAIL_USERNAME=<GMail username>
# > export MAIL_PASSWORD=<GMail password>

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]' #主题的前缀
app.config['FLASKY_MAIL_SENDER'] = 'wuxiaobai24@163.com' #发件人地址
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN') #Admin的邮箱地址，如果为空，则不会发送

#初始化mail
mail = Mail(app)

db = SQLAlchemy(app)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)

class NameForm(Form):
    name = StringField('what is your name?',validators=[Required()])
    submit = SubmitField('Submit')


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique = True)
    users = db.relationship('User',backref='role', lazy='dynamic')
    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),unique=True, index = True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

#测试mail
def text_send_mail():
    msg = Message('subject',sender = app.config['MAIL_USERNAME'],
                    recipients=['wuxiaobai24@163.com'])
    msg.body='test body'
    msg.html='<b>HTML</b> body'
    mail.send(msg)

#实现异步发生Mail
def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

#kwargs is keywords
def send_mail(to,subject,template,**kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                sender = app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    #mail.send(msg)
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr


# 集成Python Shell
# 实现自动导入
def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role,mail=mail,send_mail=send_mail)
manager.add_command("shell",Shell(make_context=make_shell_context))

@app.route('/',methods=['GET','POST'])
def index():
    #name = None
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_mail(app.config['FLASKY_ADMIN'],'New User','mail/new_user',user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data=''
        return redirect(url_for('index'))
    return render_template('index.html',form=form,name = session.get('name'),
                        known = session.get('known',False),
                        current_time=datetime.utcnow())

@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    #app.run(debug=True)
    manager.run()
