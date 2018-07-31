from flask import render_template, current_app, session

from info import constants
from info.models import User, News
from . import index_blu


#请求的首页
@index_blu.route("/")
def index():
    '''
    显示首页
    1 如果用户已经登录,
    2 将但钱用户已经登录,将当前用户的数据传到模板中,共模板显示.
    :return:
    '''

    # 显示用户是否登录的逻辑
    user_id = session.get("user_id",None)
    user=None
    if user_id:
        try:
            user  = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    #右侧新闻的排行的逻辑
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.HOME_PAGE_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)
    #定义一个空的字典列表,里面装的就是字典里诶包
    news_dict_li = []
    #遍历对象列表,将对象字典,添加到字典列表中
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())
    data={
        'user':user.to_dict() if user else None,
        'news_dict_li':news_dict_li

    }


    return render_template("news/index.html",data=data)


#在打开网页的时候,浏览器会默认请求根路径下的favicon.ico
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')