from datetime import datetime, timedelta
import time

from flask import request, render_template, current_app, session, redirect, g, url_for

from info.models import User
from info.utils.common import user_login_data
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
    #TODO 调转到后台管理主页,暂未实现
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




