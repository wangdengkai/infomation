from flask import render_template

from . import index_blu
from info import redis_store

@index_blu.route("/")
def index():

    return render_template("news/index.html")