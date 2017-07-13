from flask_mail import Mail,Message
from threading import Thread

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
