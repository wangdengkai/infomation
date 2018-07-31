import random
import re
from datetime import datetime

from flask import request, abort, current_app, make_response, jsonify, session

from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.response_code import RET
from . import passport_blu
from info.utils.captcha.captcha import  captcha


@passport_blu.route('/sms_code',methods=['POST'])
def send_sms_code():
    '''
    发送短信的逻辑
    1 获取参数:手机号,图片验证码内容,图片验证码的编号
    2  校验参数(参数是否符合规则,判断是否有值
    3   先从redis中取出验证码内容,与用户的验证码内容对比.
    4   如果对比不一致,那么验证码输入错误.
    5   如果一直,生成验证码内容
    6   发送验证码
    7   告知发送结果.
    :return:
    '''
    # 1 获取参数:手机号,图片验证码内容,图片验证码的编号
    params_dict = request.json

    mobile = params_dict.get("mobile",None)
    image_code =params_dict.get('image_code',None)
    image_code_id = params_dict.get("image_code_id",None)
    # 2  校验参数(参数是否符合规则,判断是否有值
    if not all([mobile,image_code,image_code_id]):
        #没有值就返回错误
        #{"errno":4100,"errmsg":"参数有无'}
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    #检测手机是欧服正确
    if not re.match(r'1[35678]\d{9}$',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg="手机号有错误")
    # 3   先从redis中取出验证码内容,与用户的验证码内容对比.
    try:
        real_image_code = redis_store.get("ImageCodeId_"+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmag="查询数据失败")
    if not real_image_code:
        return jsonify(errno=RET.NODATA,errmsg="图片验证码过期")

    # 4   如果对比不一致,那么验证码输入错误.
    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DBERR,errmsg="验证码输入错误")
    # 5   如果一直,生成验证码内容
    #随机数字,保证数字长度为6为3,不够再前面不上0.
    sms_code_str="%06d" % random.randint(0,999999)
    current_app.logger.debug("短信验证码是%s" % sms_code_str)

    # 6   发送验证码
    # result = CCP().send_template_sms(mobile,[sms_code_str,constants.SMS_CODE_REDIS_EXPIRES/60 ],1)
    # if result != 0 :
        #代表发送不成功
        # return jsonify(errno=RET.THIRDERR,errmsg="发送短信失败")

    #保存验证码到redis中
    try:
        redis_store.set('SMS_'+mobile,sms_code_str)
        redis_store.expire('SMS_'+mobile,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据存储错误")

    # 7   告知发送结果.
    return jsonify(errno=RET.OK,errmsg="发送成功")



@passport_blu.route('/image_code')
def get_image_code():
    '''
    #生成图片验证码并返回
    1 娶到参数
    2 判断参数是否有值
    3 生成图片验证码啊
    4 保存图片验证码文字呃逆荣到redis
    5 范湖为验证码图片

    :return:
    '''
    # 1 娶到参数,args:娶到url中?后面的参数
    image_code_id = request.args.get("imageCodeId",None)
    # 2 判断参数是否有值
    if not image_code_id:
        return abort(403)

    # 3 生成图片验证码啊
    neme,text,image=captcha.generate_captcha()
    # 4 保存图片验证码文字呃逆荣到redis

    try:

        redis_store.set("ImageCodeId_"+image_code_id,text)
        # print("---ok")
        redis_store.expire("ImageCodeId_"+image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES)
        # print("-----------ok")
        # redis_store.set("ImageCodeId_"+image_code_id,text,ex=constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        # abort(500)

    # 5 范湖为验证码图片
    response =make_response(image)
    #设置浏览器类型
    response.headers['Content-Type'] = 'image/jpg'
    return response



@passport_blu.route("/register",methods=["POST"])
def register():
    '''
    注册的逻辑
    1 获取参数
    2 校验参数
    3 娶到服务器保存的真实的短信验证码内容
    4 校验用户输入的短信验证码内容和正式验证码内容是否一致
    5 如果一直,出水啊User模型,并且属性
    6 将user保存到模型数据库
    7 返回响应
    :return:
    '''
    param_dict = request.json
    moble = param_dict.get("mobile")
    sms_code = param_dict.get("smscode")
    password = param_dict.get('password')

    if not all([moble,sms_code,password]):
        # 参数不全
        return jsonify(errno=RET.PARAMERR,errmsg="参数不足")

    if not re.match(r'1[35678]\d{9}',moble):
        return jsonify(errno=RET.PARAMERR,errmsg="手机号格式不想正确")

    try:
        real_sms_code = redis_store.get("SMS_"+moble)
    except Exception as e:
        return jsonify(errno=RET.DBERR,errmsg="获取本地验证码失败")


    if not real_sms_code:
        return jsonify(errno=RET.NODATA,errmsg="短信验证码已经过期")
    # 3. 校验验证码
    if real_sms_code.upper()  != sms_code.upper():
        return  jsonify(errno=RET.PARAMERR,errmsg="短信验证码错误")
    #删除短信验证码
    try:
        redis_store.delete('SMS_'+moble)
    except Exception as e:
        current_app.logger.error(e)
    # 4. 初始化 user 模型，并设置数据并添加到数据库
    user = User()
    user.mobile =moble
    user.nick_name = moble
    user.last_login = datetime.now()

    #TODO 对密码进行处理
    #
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        #数据爆粗你失败,回滚
        db.session.rollback()
        current_app.logger.error(e)

        return jsonify(errno=RET.DBERR,errmsg="数据保存失败")

        # 5. 保存用户登录状态
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] =user.nick_name



    return jsonify(errno=RET.OK,errmsg="注册成功")


@passport_blu.route('/login',methods=['POST'])
def login():
    '''
    登录
    1 虎丘参数
    2 J校验参数
    3  校验密码是否正确
    4   保存用户的登录状态
    5   响应
    :return:
    '''

    params_dict = request.json

    mobile =params_dict.get("mobile")
    password=params_dict.get("password")

    if not all([mobile,password]):
        return jsonify(erno=RET.PARAMERR,errmsg="参数错误")
    #校验手机号师傅zehngque
    if not re.match(r'1[35678]\d{9}',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg="手机号格式不想正")

    try:
        user =User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erno=RET.PARAMERR,errmsg="数据查询失败")


    if not user:
        return jsonify(erno=RET.NODATA,errmsg="用户不存在")

    if not user.check_passowrd(password):
        return jsonify(erno=RET.PWDERR,errmsg="用户密码错误")


    session['user_id'] =user.id
    session['mobile'] = user.mobile
    session['nick_name'] =user.nick_name

    user.last_login = datetime.now()


    # try:
    #     db.session.commit()
    # except Exception as e:
    #     db.session.rollback()
    #     current_app.logger.error(e)
    #
    #     return jsonify(errno=RET.NODATA,errmsg="登录事件2修改失败")


    return jsonify(errno=RET.OK,errmsg="登录成功")


@passport_blu.route('/logout')
def logout():
    '''
    退出功能
    清理session
    :return:
    '''
    #溢出session中的数据(dict)
    #pop 会有一个返回值,如果要溢出dekey不存在,
    session.pop('user_id',None)
    session.pop('mobile',None)
    session.pop('nick_name',None)

    return jsonify(errno=RET.OK,errmsg="退出成功")





