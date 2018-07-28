from . import index_blu


@index_blu.route("/")
def index():
    # current_app.logger.error("测试")
    return "indexi"