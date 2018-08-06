import logging

from redis import StrictRedis


class Config(object):
    '''项目的配置'''

    SECRET_KEY ='ZqSFNHmDmg097SioiysE63xOgISjp0RcnTYM28DCx2kb4yGgX5Us6RPG1/jSZGCi'


    #未数据库添加配置
    SQLALCHEMY_DATABASE_URI="mysql+pymysql://wangdengkai:wangdengkai@127.0.0.1:3306/infomation"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    #在请求结束是,如果指定这个配置为True,那么sqlalchemy会自动执行一次db.session.commit
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

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
    #设置日志等级
    LOG_LEVEL = logging.DEBUG

    QINIU_DOMIN_PREFIX = "http://oyucyko3w.bkt.clouddn.com/"

class DevelopmentConfig(Config):
    '''开发环境下的配置'''
    DEBUG = True

    #设置日志等级
    LOG_LEVEL = logging.DEBUG
class ProductionConfig(Config):
    '''生产环境下的配置'''
    DEBUG = False
    #生产环境下数据库的配置

class TestingConfig(Config):
    '''单元测试环境下的配置'''
    DEBUG = True
    TESTING = True

    #未数据库添加配置
    SQLALCHEMY_DATABASE_URI="mysql://wangdengkai:wangdengkai@127.0.0.1:3306/test_infomation"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


config={
    'development':DevelopmentConfig,
    'production':ProductionConfig,
    'testing':TestingConfig
}