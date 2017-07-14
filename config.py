import os
basedir = os.path.abspath(os.path.dirname(__file__))

#配置类
class Config:
    SECRET_KEY =  os.environ.get('SKCRET_KEY') or 'hard to guess string.'

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False

    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]' #主题的前缀
    FLASKY_MAIL_SENDER  = 'wuxiaobai24@163.com' #发件人地址
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') #Admin的邮箱地址，如果为空，则不会发送
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 994
    MAIL_USE_TLS  = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI =\
        'sqlite:///' + os.path.join(basedir,'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI =\
        'sqlite:///' + os.path.join(basedir,'data-test.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI =\
        'sqlite:///' + os.path.join(basedir,'data.sqlite')

config = {
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,

    'default':DevelopmentConfig

}
