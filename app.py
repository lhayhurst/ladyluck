import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app    = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('LOCAL_DB_URL')
app.config['SQLALCHEMY_POOL_RECYCLE'] = 499
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20

db = SQLAlchemy(app)
db.session.expire_on_commit = False