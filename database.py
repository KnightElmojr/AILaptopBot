from web_app import app
from models import db, LaptopSelection

def init_db():
    with app.app_context():
        db.create_all()

def log_selection(user_id, category):
    with app.app_context():
        new_selection = LaptopSelection(user_id=user_id, category=category)
        db.session.add(new_selection)
        db.session.commit()