
from flask import request, abort, current_app, make_response

from info import redis_store, constants
from . import passport_blu
from info.utils.captcha.captcha import  captcha
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