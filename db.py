from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists
db = SQLAlchemy()

def init_db(app):
    with app.app_context():
        if not database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            db.create_all()
