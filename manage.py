from flask import Flask, session
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_session import Session
from config import Config





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
    return "indexinsid"

if __name__ == '__main__':
    manager.run()
