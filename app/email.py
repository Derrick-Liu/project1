from flask_mail import Message
from manage import app
from flask import render_template
from app import mail

from threading import Thread
def send_asnc_email(app,msg):
    with app.app_context():
        mail.send(msg)


def send_email(to,subject,template,**kwargs):
    msg=Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,
                sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])  #something about the email
    msg.body=render_template(template+'.txt',**kwargs)
    msg.html=render_template(template+'.html',**kwargs)
    thr=Thread(target=send_asnc_email,args=[app,msg])
    thr.start()
    return thr
