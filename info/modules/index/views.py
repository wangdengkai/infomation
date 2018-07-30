from flask import render_template, current_app

from . import index_blu


#请求的首页
@index_blu.route("/")
def index():

    return render_template("news/index.html")


#在打开网页的时候,浏览器会默认请求根路径下的favicon.ico
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')