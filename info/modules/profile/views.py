from flask import render_template, redirect, g, request, jsonify, current_app, session

from info import db, constants
from info.models import Category, News
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET


@profile_blu.route("/base_info",methods=["POST","GET"])
@user_login_data
def base_info():
    user = g.user
    if request.method == "GET":
        data={
            "user":g.user.to_dict()
        }
        return render_template("news/user_base_info.html",data=data)
    #修改用户数据
    data_dict = request.json
    nick_name = data_dict.get("nick_name")
    gender = data_dict.get("gender")
    signature = data_dict.get("signature")

    if not all([nick_name,gender,signature]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    if gender not in (['MAN','WOMAN']):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    #更新并保存数据
    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="保存数据到数据库失败")

    #将session中保存的数据进行实施更新
    session['nick_name'] = nick_name

    return jsonify(errno=RET.OK,errmsg="更新成功")


@profile_blu.route("/info")
@user_login_data
def user_info():
    user = g.user
    if not user:
        return redirect('/')

    data={
        "user":user.to_dict()
    }

    return render_template("news/user.html",data=data)

@profile_blu.route('/pic_info',methods=['POST',"GET"])
@user_login_data
def pic_info():
    user=g.user
    if request.method == 'GET':
        return render_template('news/user_pic_info.html',data={'user_info':user.to_dict()})

    #1获取到上传的文件
    try:
        avatar_file =request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg="读取文件出错")

    #2在将文件上传到骑牛云
    try:
        url = storage(avatar_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="上传图片错误")
    #保存头像地址
    user.avatar_url = url
    return jsonify(errno=RET.OK,errmsg="OK",data={"avatar_url":constants.QINIU_DOMIN_PREFIX + url})


@profile_blu.route("/pass_info",methods=['POST','GET'])
@user_login_data
def pass_info():


    if request.method == 'GET':
        return render_template('news/user_pass_info.html')

    #获取参数
    new_password =request.json.get("new_password")
    old_password = request.json.get('old_password')

    #校验参数
    if not all([old_password,new_password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    #判断就密码是欧服正确
    user = g.user
    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.PWDERR,errmsg="密码错误")

    #设置新密码
    user.password = new_password
    return jsonify(errno=RET.OK,errmsg="修改密码成功")

@profile_blu.route('/collection')
@user_login_data
def user_collection():
    #获取参数
    page =request.args.get('p',1)
    #判断参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    #查询用户指定页数收藏的新闻
    user =g.user
    news_list =[ ]
    total_page=1
    current_page=1
    try:
        paginate = user.collection_news.paginate(page,constants.USER_COLLECTION_MAX_NEWS,False)

        current_page =paginate.page
        total_page =paginate.pages
        news_list=paginate.items
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li =[]
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        'total_page':total_page,
        'current_page':current_page,
        'collections':news_dict_li,

    }

    return render_template('news/user_collection.html',data=data)

@profile_blu.route("/news_release",methods=["POST","GET"])
@user_login_data
def news_release():
    if request.method == "GET":

        categories = []

        try:
            #获取所有的分类数据
            categories = Category.query.order_by(Category.id).all()
        except Exception as e:
            current_app.logger.error(e)


        #定义列表保存分类数据
        categories_dicts = []

        for category in categories:
            #获取字典
            cate_dict = category.to_dict()
            #拼接内容
            categories_dicts.append(cate_dict)


        #溢出,最新分类
        categories_dicts.pop(0)
        #返回内容

        return render_template("news/user_news_release.html",data={"categories":categories_dicts})

    #post提交
    #获取提交的数据
    title = request.form.get("title")
    source = "个人发布"
    digest = request.form.get('digest')
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")

    #判断是否有值
    if not all([title,source,digest,content,index_image,category_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数有无")

    #尝试读取图片
    try:
        index_image = index_image.read()
    except Exception as e:
        current_app.logger.error(e)

        return jsonify(errno=RET.PARAMERR,errmsg="参数有无")

    #将标题图片上传到骑牛
    try:
        key = storage(index_image)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="上传图片错误")


    #3初始化新闻模型,并设置相关数据
    news = News()
    news.title  = title
    news.digest = digest
    news.source = source
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX+key
    news.category_id = category_id
    news.user_id = g.user.id

    #1 代表审核状态
    news.status = 1
    #保存到数据库
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

        return jsonify(errno=RET.DBERR,errmsg="保存数据失败")
    print(news.id)
    #返回结果
    return jsonify(errno=RET.OK,errmsg="发布成功,等待审核")

@profile_blu.route('/news_list')
@user_login_data
def news_list():
    #获取页数
    p  = request.args.get("p",1)
    try:
        p = int(p)

    except Exception as e:
        current_app.logger.error(e)
        p = 1

    user =g.user
    news_li = []
    current_page =  1
    total_page = 1
    try:
        paginate = News.query.filter(News.user_id == user.id).paginate(p,constants.USER_COLLECTION_MAX_NEWS,False)
        #获取当前页的数据u
        news_li = paginate.items
        #获取当前也饿的
        current_page = paginate.page
        #获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []

    for news_item in news_li:
        news_dict_li.append(news_item.to_review_dict())


    data = {'news_list':news_dict_li,'total_page':total_page,'current_page':current_page}

    return  render_template('news/user_news_list.html',data=data)












