from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from info import app,db
'''
    这个模块专门提供启动程序的逻辑.
'''

#关联app
manager = Manager(app)
#将app于db关联
Migrate(app,db)
#将迁移命令添加到manager中
manager.add_command('db',MigrateCommand)


@app.route("/")
def index():
    return "indexinsid"

if __name__ == '__main__':
    manager.run()
