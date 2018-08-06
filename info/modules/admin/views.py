from datetime import datetime, timedelta
import time

from flask import request, render_template, current_app, session, redirect, g, url_for, jsonify

from info import constants, db
from info.models import User, News, Category
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET
from . import admin_blu

@admin_blu.route('/login',methods=['GET','POST'])
def admin_login():
    if request.method == 'GET':
        #取session中娶到指定的值
        user_id = session.get('user_id',None)
        is_admin = session.get('is_admin',False)
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))
        return render_template('admin/login.html')


    #娶到登录的和参数
    username = request.form.get('username')
    password = request.form.get('password')

    if not all([username,password]):
        return  render_template('admin/login.html',errmsg='参数不足')


    try:
        user = User.query.filter(User.mobile == username).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html',errmsg="用户不存在")
    if not user:
        return render_template('admin/login.html',errmsg='用户不存在')
    if not user.check_password(password):
        return render_template('admin/login.html',errmsg='密码错误')

    if not user.is_admin:
        return render_template('admin/login.html',errmsg='用户权限错误')

    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    session['is_admin'] = True
    #调转到后台管理主页,暂未实现
    return redirect(url_for('admin.admin_index'))


@admin_blu.route('/index')
@user_login_data
def admin_index():
    user =g.user
    return render_template('admin/index.html',user=user.to_dict())


@admin_blu.route('/user_count')
def user_count():
    #查询总人数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin==False).count()
    except Exception as e:
        current_app.logger.error(e)

    #查询月增新书
    mon_count = 0
    now = time.localtime()
    try:

        mon_begin = '%d-%02d-01'%(now.tm_year,now.tm_mon)
        mon_begin_date = datetime.strptime(mon_begin,'%Y-%m-%d')

        mon_count = User.query.filter(User.is_admin ==False,User.create_time >= mon_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)


    #查询日新增数
    day_count =0
    try:
        day_begin = '%d-%02d-%02d' %(now.tm_year,now.tm_mon,now.tm_mday)
        day_begin_date =datetime.strptime(day_begin,'%Y-%m-%d')
        day_count = User.query.filter(User.is_admin == False,User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    #查询图标信息
    #获取到当天00:00:00事件
    now_date = datetime.strptime(datetime.now().strftime('%Y-%m-%d'),'%Y-%m-%d')
    #定义空数据,保存数据
    active_date = []
    active_count =[]

    #一次添加数据,在反转
    for i in range(0,31):
        begin_date = now_date-timedelta(days=i)
        end_date = now_date-timedelta(days=(i-1))
        active_date.append(begin_date.strftime('%Y-%m-%d'))
        count = 0
        try:
            count = User.query.filter(User.is_admin ==False,
                                      User.last_login >= begin_date,
                                      User.last_login <end_date).count()



        except Exception as e:
            current_app.logger.error(e)

        active_count.append(count)


    active_date.reverse()
    active_count.reverse()

    data ={
        'total_count':total_count,
        'mon_count':mon_count,
        'day_count':day_count,
        'active_date':active_date,
        'active_count':active_count

    }

    return render_template('admin/user_count.html',data=data)


@admin_blu.route('/user_list')
def user_list():
    '''获取用户列表'''

    #获取参数
    page = request.args.get('p',1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    #设置变量默认值
    users = []
    current_page = 1
    total_page =1

    #查询数据u
    try:
        paginate = User.query.filter(User.is_admin==False).order_by(User.last_login.desc()).paginate(page,constants.ADMIN_USER_PAGE_MAX_COUNT,False)
        users = paginate.items
        current_page = paginate.page
        total_page =paginate.pages
    except Exception as e:
        current_app.logger.error(e)


    #将模型里列表转为字典里列表
    users_list = [ ]

    for user in users:
        users_list.append(user.to_dict())

    context = {'total_page':total_page,
               'current_page':current_page,
               'users':users_list,
               }


    return render_template('admin/user_list.html',data=context)

@admin_blu.route('/news_review')
def news_review():
    '''返回带审核新闻里列表'''
    page = request.args.get('p',1)
    keywords = request.args.get('keywords','')



    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list =[]
    current_page =1
    total_page =1

    try:
        filters = [News.status != 0]
        #如果有关键子
        if keywords:
            #添加关键字的检索选项
            filters.append(News.title.contains(keywords))
        paginate = News.query.filter(*filters ).order_by(News.create_time.desc()).paginate(page,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)

        news_list =paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())

    context = {
        'total_page':total_page,
        'current_page':current_page,
        'news_list':news_list
    }

    return render_template('admin/news_review.html',data=context)

@admin_blu.route('/news_review_detail',methods=['GET','POST'])
def news_review_detail():
    '''新闻审核详情'''
    if request.method == 'GET':
    #获取新闻id
        news_id=request.args.get('news_id')
        if not news_id:
            return render_template('admin/news_review_detail.html',data={'errmsg':'未查询到次新闻'})

        #通过id查询新闻
        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)

        if not news:
            return render_template('admin/news_review_detail.html',data={'errmsg':'未查询到这个新闻'})

        #返回数据
        data = {'news':news.to_dict()}

        return render_template('admin/news_review_detail.html',data=data)

#     执行审核操作
    #获取参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    #判断参数
    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    if action not in ('accept','reject'):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    news = None
    try:
        #查询新闻
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        return jsonify(errno=RET.NODATA,errmsg="未查询到数据")

    #根据不同的状态设置不同的值
    if action == 'accept':
        news.status = 0
    else:
        #拒绝通过,需要获取原因
        reason = request.json.get('reason')
        if not reason:
            return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

        news.reason = reason
        news.status = -1

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

        return jsonify(errno=RET.DBERR,errmsg="数据保存失败")


    return jsonify(errno=RET.OK,errmsg="操作成功")

@admin_blu.route('/news_edit')
def news_edit():
    '''返回新闻列表'''

    page = request.args.get('p',1)
    keywords = request.args.get('keywords','')

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list =[]
    current_page = 1
    total_page = 1

    try:
        filters = [ ]
        #如果有关键字
        if keywords:
            #添加关键爱你自搜索选项
            filters.append(News.title.contains(keywords))

        #查询
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)

        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages

    except Exception as e:
        current_app.logger.error(e)


    news_dict_list = [ ]
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    context={'total_page':total_page,'current_page':current_page,'news_list':news_dict_list}

    return render_template('admin/news_edit.html',data=context)


@admin_blu.route('/news_edit_detail',methods=['GET','POST'])
def news_edit_detail():
    '''新闻编辑详情'''
    if request.method == 'GET':
    #获取参数
        news_id = request.args.get('news_id')

        if not news_id:
            return render_template('admin/news_edit_detail.html',data={'errmsg':"未查询到次新闻"})

        #查询新闻
        news= None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)

        if not news:
            return render_template('admin/news_edit_detail.html',data={'errmsg':'未查询到此新闻'})

        #查询分类的数据
        categories = Category.query.all()
        categories_li = []
        for category in categories:
            c_dict = category.to_dict()
            c_dict['is_selected'] = False

            if category.id ==news.category_id:
                c_dict['is_selected'] =True

            categories_li.append(c_dict)


        #溢出最新分类
        categories_li.pop(0)

        data = {'news':news.to_dict(),'categories':categories_li}
        return render_template('admin/news_edit_detail.html',data=data)
    news_id = request.form.get('news_id')
    title  = request.form.get('title')
    digest = request.form.get('digest')
    content = request.form.get('content')
    index_image=request.files.get('index_image')
    category_id = request.form.get("category_id")
    #判断数据是否有值
    if not all([title,digest,content,category_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数有无")

    news = None

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        return jsonify(errno=RET.NODATA,errmsg="未查询到新闻数据")

    #尝试读取图片
    if index_image:
        try:
            index_image = index_image.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR,errmsg="参数有无")

    #将标题,图片上传到骑牛
        try:
            key = storage(index_image)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR,errmsg="上传图片错误")

        news.index_image_url = constants.QINIU_DOMIN_PREFIX +key

    #设置相关数据u
    news.title = title
    news.digest = digest
    news.content = content
    news.category_id = category_id

    #4 保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="保存数据失败")


    #返回结果
    return jsonify(errno=RET.OK,errmsg="编辑成功")



@admin_blu.route("/news_category")
def get_news_category():
    #获取所有要分类的数据
    categories = Category.query.all()
    #定义列表保存分类数据
    categories_dicts = [ ]
    for category in categories:
        #拼接字典
        cate_dict = category.to_dict()
        #拼接内容
        categories_dicts.append(cate_dict)

    categories_dicts.pop(0)

    #返回内容
    return render_template('admin/news_type.html',data={'categories':
                                                        categories_dicts})

@admin_blu.route("/add_category",methods=['POST'])
def add_category():
    '''添加或者修改分类'''

    category_id = request.json.get("id")
    category_name = request.json.get("name")

    if not category_name:
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    #判断是否有分类id
    if category_id:
        try:
            category = Category.query.get(category_id)

        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="查询数据失败")


        if not category:
            return jsonify(errno=RET.NODATA,errmsg="未查询到分类信息")


        category.name = category_name
    else:
        #如果没有分类id,就是添加分类
        category = Category()
        category.name = category_name
        db.session.add(category)


    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="保存数据失败")

    return jsonify(errno=RET.OK,errmsg="保存数据成功")

@admin_blu.route('/logout')
def admin_logout():

    session.pop('user_id',None)
    session.pop('mobile',None)
    session.pop('nick_name',None)
    session.pop('is_admin',None)
    # 调转到后台管理主页,暂未实现
    return redirect(url_for('admin.admin_login'))


































