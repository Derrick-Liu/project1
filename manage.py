from flask_script import Manager
from app import create_app
import os
from flask_sqlalchemy import SQLAlchemy

app=create_app(os.getenv('FLASK_CONFIG') or 'default')
manager=Manager(app)
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
db=SQLAlchemy(app)



if __name__=='__main__':
    manager.run()
