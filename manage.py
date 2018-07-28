from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis


class Config(object):
    '''项目的配置'''
    DEBUG = True

    #未数据库添加配置
    SQLALCHEMY_DATABASE_URI="mysql://wangdengkai:wangdengkai@127.0.0.1:3306/infomation"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    #Redis的配置
    REDIS_HOST ='127.0.0.1'
    REDIS_PORT =6379

app = Flask(__name__)

app.config.from_object(Config)
db =SQLAlchemy(app)

#初始化redis,存储表单
redis_store = StrictRedis(host=Config.REDIS_HOST,port =Config.REDIS_PORT)

@app.route("/")
def index():
    return "index"

if __name__ == '__main__':

    app.run()
