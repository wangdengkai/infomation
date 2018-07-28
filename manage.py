import logging

from flask import current_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from info import create_app
from info import db
'''
    这个模块专门提供启动程序的逻辑.
'''
#create_app  就类似于工厂方法
app = create_app('development')
#关联app
manager = Manager(app)
#将app于db关联
Migrate(app,db)
#将迁移命令添加到manag er中
manager.add_command('db',MigrateCommand)




if __name__ == '__main__':
    manager.run()
