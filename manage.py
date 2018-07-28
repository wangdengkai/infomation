from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    '''项目的配置'''
    DEBUG = True

    #未数据库添加配置
    SQLALCHEMY_DATABASE_URI="mysql://wangdengkai:wangdengkai@127.0.0.1:3306/infomation"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

app = Flask(__name__)

app.config.from_object(Config)
db =SQLAlchemy(app)


@app.route("/")
def index():
    return "index"

if __name__ == '__main__':

    app.run()
