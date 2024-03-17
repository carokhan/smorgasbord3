from web import app
from web import db

with app.app_context():
    db.drop_all()
    db.create_all()