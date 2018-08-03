from flask import render_template, redirect, g, request

from info.modules.profile import profile_blu
from info.utils.common import user_login_data

@profile_blu.route("/base_info",methods=["POST","GET"])
@user_login_data
def base_info():

    if request.method == "GET":
        data={
            "user":g.user.to_dict()
        }
        return render_template("news/user_base_info.html",data=data)
    #修改用户数据u

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