from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from info import constants
from . import db


class BaseModel(object):
    '''模型鸡肋,为每个模型补充创建时间和更新时间'''
    #记录创建时间
    create_time = db.Column(db.DateTime,default=datetime.now)
    #记录更新时间
    update_time = db.Column(db.DateTime,default=datetime.now)


#用户收藏表,建立用户与其收藏新闻多对多的关系
tb_user_collection = db.Table(
    'info_user_collection',
    #新闻编号
    db.Column("user_id",db.Integer,db.ForeignKey("info_user.id"),primary_key=True),
    #分类标号
    db.Column("news_id",db.Integer,db.ForeignKey("info_news.id"),primary_key=True),
    #收藏夹创建时间
    db.Column("create_time",db.DateTime,default=datetime.now)
)


tb_user_follows = db.Table(
    "info_user_fans",
    #粉丝id
    db.Column("follower_id",db.Integer,db.ForeignKey('info_user.id'),primary_key=True),
    #被关注人的id
    db.Column("followed_id",db.Integer,db.ForeignKey('info_user.id'),primary_key=True)
)

class User(BaseModel,db.Model):
    '''用户表'''
    #表名字
    __tablename__ = 'info_user'

    #用户编号
    id = db.Column(db.Integer,primary_key=True)
    # 用户昵称
    nick_name = db.Column(db.String(32),unique=True,nullable=False)
    #加密密码
    password_hash = db.Column(db.String(128),nullable=False)
    #手机号
    mobile = db.Column(db.String(11),unique=True,nullable=False)
    #用户头像路径
    avatar_url = db.Column(db.String(256))
    #最后一次登录时间
    last_login = db.Column(db.DateTime,default = datetime.now)
    #是否是管理元
    is_admin = db.Column(db.Boolean,default=False)
    #用户签名
    signature = db.Column(db.String(512))
    #性别
    gender = db.Column(
        db.Enum(
            'MAN', #男
            'WOMAN' #女
        ),
        default = 'MAN'
    )

    #用户收藏的所有新闻
    collections_news = db.relationship('News',secondary=tb_user_collection,lazy='dynamic') #用户收藏的新闻
    #用户所有的粉丝
    followers = db.relationship('User',
                                secondary=tb_user_follows,
                                primaryjoin=id == tb_user_follows.c.followed_id,
                                secondaryjoin=id ==tb_user_follows.c.follower_id,
                                backref=db.backref('followed',lazy='dynamic'),
                                lazy='dynamic')

    #当前用户所发布的新闻
    news_list =db.relationship("News",backref='user',lazy='dynamic')



    @property
    def password(self):
        raise AttributeError("当前属性不可读")
    @password.setter
    def password(self,value):
        self.password_hash  = generate_password_hash(value)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)


    def to_dict(self):
        resp_dict = {
            'id':self.id,
            'nick_name':self.nick_name,
            'avatar_url':constants.QINIU_DOMIN_PREFIX + self.avatar_url if self.avatar_url else "",
            "mobile":self.mobile,
            "gender":self.gender if self.gender else "MAN",
            "followers_count":self.followers.count(),
            "news_count":self.news_list.count()
        }

        return resp_dict

    def to_admin_dict(self):
        resp_dict = {
            "id":self.id,
            "nick_name":self.nick_name,
            "register":self.create_time.strftime("%Y-%m-%d %H:%M:%s"),
            "last_login":self.last_login.strftime("%Y-%m-%d %H:%M:%s"),

        }

        return resp_dict

class News(BaseModel,db.Model):
    '''新闻'''
    __tablename__ = 'info_news'
    #新闻标号
    id = db.Column(db.Integer,primary_key=True)
    #新闻标题
    title = db.Column(db.String(256),nullable=False)
    #新闻来源
    source = db.Column(db.String(64),nullable=False)
    #新闻摘要
    digest = db.Column(db.String(512),nullable=False)
    #新闻内容
    content = db.Column(db.Text,nullable=False)
    #浏览领
    clicks = db.Column(db.Integer,default=0)
    #新闻了列表图片路径
    index_image_url = db.Column(db.String(256))
    #类型id
    category = db.Column(db.Integer,db.ForeignKey("info_category.id"))
    #用户
    user_id =db.Column(db.Integer,db.ForeignKey("info_user.id"))
    #新闻状态,如果为0代表审核通过，1代表审核中，-1代表审核不通过
    status = db.Column(db.Integer,default =0)
    ## 未通过原因，status = -1 的时候使用
    reason = db.Column(db.String(256))
    #当前新闻的所有评论
    comments = db.relationship("Comment",lazy="dynamic")

    def to_review_dict(self):
        resp_dict={
            "id":self.id,
            "title":self.title,
            "create_time":self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status":self.status,
            "reason":self.reason if self.reason else ""
        }
        return resp_dict

    def to_basic_dict(self):
        resp_dict = {
            "id":self.id,
            "title":self.title,
            "source":self.source,
            "digest":self.digest,
            "create_time":self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "index_image_url":self.index_image_url,
            "clicks":self.clicks
        }

        return resp_dict
    def to_dict(self):
        resp_dict={
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "digest": self.digest,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": self.content,
            "comments_count":self.comments.count(),
            "clicks":self.clicks,
            "category":self.category.to_dict(),
            "index_image_url":self.index_image_url,
            "author":self.user.to_dict() if self.user else None

        }


    class Comment(BaseModel,db.Model):
        '''评论'''
        __tablename__ = "info_comment"
        #评论编号
        id = db.Column(db.Integer,primary_key=True)
        #用户id
        user_id = db.Column(db.Integer,db.ForeignKey("info_user.id"),nullable=False)
        #新闻id
        news_id = db.Column(db.Integer,db.ForeignKey("info_news.id"),nullable=False)
        #评论内容
        content = db.Column(db.Text,nullable=False)
        #福评论id
        parent_id = db.Column(db.Integer,db.ForeignKey("info_comment.id"))
        #自关联
        parent = db.relationship("Comment",remote_side=[id])
        #点赞条数
        like_count = db.Column(db.Integer,default=0)

        def to_dict(self):
            resp_dict={
                "id":self.id,
                "create_time":self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "content":self.content,
                "parent":self.parent.to_dict() if self.parent else None,
                "user":User.query.get(self.user_id).to_dict(),
                "news_id":self.news_id,
                "like_count":self.like_count
            }

            return resp_dict


class CommentLike(BaseModel,db.Model):
    '''评论点咋"'''
    __tablename__ = 'info_comment_like'
    #评论编号
    comment_id = db.Column("comment_id",db.Integer,db.ForeignKey("info_comment.id"),primary_key=True)
    #用户编号
    user_id = db.Column("user_id",db.Integer,db.ForeignKey("info_user.id"),primary_key=True)

class Category(BaseModel,db.Model):
    '''新闻分类'''
    __tablename__ = 'info_category'
    #分类边好
    id = db.Column(db.Integer,primary_key=True)
    #分类名
    name = db.Column(db.String(64),nullable=False)
    news_list =db.relationship("News",backref="category",lazy='dynamic')

    def to_dict(self):
        resp_dict={
            'id':self.id,
            'name':self.name
        }

        return resp_dict
