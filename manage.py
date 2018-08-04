
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from info import create_app
from info import db ,models



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

@manager.option('-n','-name',dest='name')
@manager.option('-p','-password',dest='password')
def createsuperuser(name,password):
    '''创建管理员用户'''
    if not all([name,password]):
        print("参数不足")
        return
    from info.models import  User
    user = User()
    user.mobile = name
    user.nick_name = name
    user.password =password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
        print("创建成功")
    except Exception as e:
        print(e)
        db.session.rollback()





if __name__ == '__main__':
    manager.run()
