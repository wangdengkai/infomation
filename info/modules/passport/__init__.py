#登录注册的相关业务逻辑都放在这里
from flask import Blueprint

passport_blu = Blueprint('passport',__name__,url_prefix='/passport')

from . import views