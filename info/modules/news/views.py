from flask import render_template, session, current_app, g, abort, request, jsonify

from info import constants
from info.models import User, News
from info.utils.response_code import RET

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

@news_blu.route("/news_collect",methods=['POST'])
@user_login_data
def collect_news():
    '''
    收藏新闻
    1 接受参数u
    2 校验参数
    3 查询新闻
    :return:
    '''
    user =g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户没有登录")
    # 1 接受参数u
    news_id=request.json.get('news_id')
    action =request.json.get("action")
    # 2 校验参数
    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")


    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    if action not in ['collect','cancel_collect']:
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")


    try:
        news = News.query.get(news_id)
    except Exception as e:
        return jsonify(errno=RET.DBERR,errmsg="数据查询错误")

    if not news:
        return jsonify(errno=RET.NODATA,errmsg="未查询到新闻数据u")

    #收藏
    if action =="cancel_collect":
        #取消收藏
        if news in user.collection_news:
            user.collection_news.remove(news)
    else:
        #收藏
        if news not in  user.collection_news:
            user.collection_news.append(news)

    return jsonify(errno=RET.OK,errmsg="操作成功")


