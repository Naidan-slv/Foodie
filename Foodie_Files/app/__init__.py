from flask import Flask,request, session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_admin import Admin
from flask_babel import Babel

def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')

app = Flask(__name__)

babel = Babel(app, locale_selector=get_locale)
admin = Admin(app,template_mode='bootstrap4')

app.config.from_object('config')

Bootstrap(app)
csrf = CSRFProtect(app)

db = SQLAlchemy(app)
migrate = Migrate(app,db)

from app import views,models

