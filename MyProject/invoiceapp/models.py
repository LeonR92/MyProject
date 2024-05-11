from flask_sqlalchemy import SQLAlchemy
from users import UserModel
from datetime import datetime

db = SQLAlchemy()

class Invoice(db.Model):
    __tablename__ = 'invoice'
    id = db.Column(db.Integer, primary_key=True)
    invoice_num = db.Column(db.String(120), unique=True, nullable=False)
    invoice_amount = db.Column(db.Float, nullable=False)
    sender_address = db.Column(db.String(255), nullable=False)  # Added sender's address
    receiver_address = db.Column(db.String(255), nullable=False)  # Added receiver's address
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)  # Added invoice date
    payment_terms = db.Column(db.Integer, nullable=False)  # Added payment terms in days
    invoice_description = db.Column(db.Text, nullable=True)  # Added invoice description
    receiver = db.Column(db.String(120), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invoice_status = db.Column(db.String(50), nullable=False)
    favorites = db.relationship('Favorite', backref='invoice', lazy='dynamic')
    items = db.relationship('InvoiceItem', backref='invoice', lazy='dynamic')  # Added item list relationship

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)  # Description of the item
    quantity = db.Column(db.Integer, nullable=False)  # Quantity of the item
    price = db.Column(db.Float, nullable=False)  # Price per item

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)