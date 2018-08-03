from flask import render_template, current_app, session, request, jsonify, g

from info import constants
from info.models import User, News, Category
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_blu

@index_blu.route("/news_list")
def new_list():
    '''
    获取首页新闻数据u
    :return:
    '''
    # 1.获取参数
    #新闻分类id
    cid = request.args.get('cid',1)
    page = request.args.get('page',1)
    per_page=request.args.get('per_page',10)
    #校验参数
    try:
        page = int(page)
        per_page = int(per_page)
        cid = int(cid)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    #3查询数据
    filters= [News.status == 0]
    if cid != 1:
        #需要添加条件
        filters.append(News.category_id == cid)
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库错误")
    #到当前页的数据
    news_model_list =paginate.items
    total_page = paginate.pages
    current_page = paginate.page
    #将模型对象里里诶包转成字典里列表
    news_dict_lis =  []

    for news in news_model_list:
        news_dict_lis.append(news.to_dict())




    data={
        'total_page':total_page,
        'current_page':current_page,
        'newsList':news_dict_lis,

    }

    return jsonify(errno=RET.OK,errmsg="OK",data=data)



#请求的首页
@index_blu.route("/")
@user_login_data
def index():
    '''
    显示首页
    1 如果用户已经登录,
    2 将但钱用户已经登录,将当前用户的数据传到模板中,共模板显示.
    :return:
    '''

    # 显示用户是否登录的逻辑
    # user_id = session.get("user_id",None)
    # user=None
    # if user_id:
    #     try:
    #         user  = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)
    user= g.user

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


    # 首页分类数据
    category_list =Category.query.all()
    cate_list=[]
    for category in category_list:
        cate_list.append(category.to_dict())
    data={
        'user':user.to_dict() if user else None,
        'news_dict_li':news_dict_li,
        'category_list':cate_list,

    }


    return render_template("news/index.html",data=data)


#在打开网页的时候,浏览器会默认请求根路径下的favicon.ico
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')