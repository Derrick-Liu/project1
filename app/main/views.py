from . import main
from flask import redirect,render_template

@main.route('/')
def index():
    return render_template('index.html')