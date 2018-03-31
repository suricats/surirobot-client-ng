from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import get_config

app = Flask(__name__)
app.config.update(get_config())
db = SQLAlchemy(app)

from management.mod_api.api import mod_api
app.register_blueprint(mod_api)

db.create_all()
