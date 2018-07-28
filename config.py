from redis import StrictRedis


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
