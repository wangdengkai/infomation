from . import index_blu
from info import redis_store

@index_blu.route("/")
def index():
    # current_app.logger.error("测试")
    # redis_store.set("werwer4","3242")
    # print(redis_store.get("werwer4"))
    redis_store.set("name","haha")
    return "indexi"