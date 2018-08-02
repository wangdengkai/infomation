from flask import render_template, session, current_app, g, abort

from info import constants
from info.models import User, News

from . import news_blu
from info.utils.common import user_login_data


@news_blu.route("/<int:news_id>")
@user_login_data
def news_detail(news_id):
    '''
    新闻详情
    :param news_id:
    :return:
    '''
    #查询用户登录信息
    user = g.user
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


    #查询新闻数据
    news =None

    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        #新闻没找到
        abort(404)

    #更新新闻点击次数
    news.clicks +=1

    # 用户收藏
    is_collected = False
    if user:
        if news  in user.collection_news:
            is_collected=True


    data={
        'user':user.to_dict() if user else None,
        'news_dict_li':news_dict_li,
        "news":news.to_dict(),
        'is_collected':is_collected


    }


    return render_template("news/detail.html",data=data)