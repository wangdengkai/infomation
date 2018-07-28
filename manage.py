from flask import Flask, session
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_session import Session

class Config(object):
    '''项目的配置'''
    DEBUG = True
    SECRET_KEY ='ZqSFNHmDmg097SioiysE63xOgISjp0RcnTYM28DCx2kb4yGgX5Us6RPG1/jSZGCi'


    #未数据库添加配置
    SQLALCHEMY_DATABASE_URI="mysql://wangdengkai:wangdengkai@127.0.0.1:3306/infomation"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    #Redis的配置
    REDIS_HOST ='127.0.0.1'
    REDIS_PORT =6379
    #指定session保存的redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)

    #Session保存位置
    SESSION_TYPE='redis'
    #是否开启session签名
    SESSION_USE_SIGNER = True
    #设置需要过期时间
    SESSION_PERMANENT=False
    #设置session,保存时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2




app = Flask(__name__)

app.config.from_object(Config)
db =SQLAlchemy(app)

#初始化redis,存储表单
redis_store = StrictRedis(host=Config.REDIS_HOST,port =Config.REDIS_PORT)

#开启当前项目CSRF保护,制作服务器验证功能,cookie中的csrf_token和表单csrf_token需要我们自己实现..
CSRFProtect(app)

#设置session保存位置
Session(app)

#关联app
manager = Manager(app)
#将app于db关联
Migrate(app,db)
#将迁移命令添加到manager中
manager.add_command('db',MigrateCommand)
@app.route("/")
def index():

    print(session['name'])
    return "index"

if __name__ == '__main__':
    manager.run()
