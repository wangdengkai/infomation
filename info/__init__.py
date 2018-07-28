from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import config

'''
    info模块,是具体业务模块,实现相关业务.
'''

app = Flask(__name__)

app.config.from_object(config['develop'])
db =SQLAlchemy(app)

#初始化redis,存储表单
redis_store = StrictRedis(host=config['develop'].REDIS_HOST,port =config['develop'].REDIS_PORT)

#开启当前项目CSRF保护,制作服务器验证功能,cookie中的csrf_token和表单csrf_token需要我们自己实现..
CSRFProtect(app)

#设置session保存位置
Session(app)