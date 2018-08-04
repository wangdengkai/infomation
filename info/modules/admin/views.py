from flask import request, render_template, current_app, session

from info.models import User
from . import admin_blu

@admin_blu.route('/login',methods=['GET','POST'])
def admin_login():
    if request.method == 'GET':
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

    if not user.check_passowrd(password):
        return render_template('admin/login.html',errmsg='密码错误')

    if not user.is_admin:
        return render_template('admin/login.html',errmsg='用户权限错误')

    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    session['is_admin'] = True
    #TODO 调转到后台管理主页,暂未实现
    return "登录成功,需跳转到主页"