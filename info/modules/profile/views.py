from flask import render_template, redirect, g, request, jsonify, current_app, session

from info import db, constants
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

