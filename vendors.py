from flask_sqlalchemy import SQLAlchemy
from app import app, db

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///companies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300))
    phone = db.Column(db.String(50))
    mobile = db.Column(db.String(50))
    email = db.Column(db.String(120))
    services = db.Column(db.Text)


with app.app_context():
    db.create_all()
    print("Tables created successfully.")