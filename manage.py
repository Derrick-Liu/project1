from flask_script import Manager,Shell
from app import create_app, db
import os
from app.models import User,Role,Post,Comment,Follow
from flask_migrate import MigrateCommand,Migrate

app=create_app(os.getenv('FLASK_CONFIG') or 'default')
manager=Manager(app)

migrate=Migrate(app,db)

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role,Post=Post,Comment=Comment,Follow=Follow)
manager.add_command('shell',Shell(make_context=make_shell_context))

manager.add_command('db',MigrateCommand)

if __name__=='__main__':
    manager.run()
