from flask_script import Manager,Shell
from app import create_app, db
import os
from app.models import User,Role
from flask_migrate import MigrateCommand,Migrate

app=create_app(os.getenv('FLASK_CONFIG') or 'default')
manager=Manager(app)
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True

migrate=Migrate(app,db)

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)
manager.add_command('db',MigrateCommand)
manager.add_command('shell',Shell(make_context=make_shell_context))



if __name__=='__main__':
    manager.run()
