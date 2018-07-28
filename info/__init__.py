import logging
from logging.handlers import RotatingFileHandler

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

def setup_log(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL) # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
def create_app(config_name):
    app = Flask(__name__)
    #设置日志
    setup_log(config_name)

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