from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import config

'''
    info模块,是具体业务模块,实现相关业务.
'''
#初始化数据库,
# 在flask很多拓展里面都可以先初始化托找的对象,然后调用init_appfangfa 初始化
db = SQLAlchemy()
def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    #初始化db
    db.init_app(app)

    #初始化redis,存储表单
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST,port =config[config_name].REDIS_PORT)

    #开启当前项目CSRF保护,制作服务器验证功能,cookie中的csrf_token和表单csrf_token需要我们自己实现..
    CSRFProtect(app)

    #设置session保存位置
    Session(app)
    return app