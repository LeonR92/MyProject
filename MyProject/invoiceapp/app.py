from flask import Blueprint, jsonify, render_template,request, url_for, redirect
import requests
from utils import cache
from flask_login import login_required
from invoiceapp.models import Invoice,Favorite,InvoiceItem
from app import db
from datetime import datetime



# Define the blueprint
invoice = Blueprint("invoice", __name__, template_folder="templates")

@invoice.before_request
def create_tables():
    db.create_all()

@invoice.before_request
@login_required
def before_request():
    """Ensure user is logged in before accessing any invoice routes."""
    pass

@invoice.route("/")
def index():
    invoices = Invoice.query.all()
    return render_template("invoice/index.html",invoices=invoices)


# TODO add data validation
# Auto Calculation
@invoice.route('/newinvoice', methods=['POST'])
def new_invoice():
    try:
        # Extracting data from form fields
        new_invoice = Invoice(
            invoice_num=request.form['invoice_num'],
            invoice_amount=request.form['invoice_amount'],
            sender_address=request.form['sender_address'],
            receiver_address=request.form['receiver_address'],
            invoice_date=request.form.get('invoice_date', datetime.utcnow()),  # default to now if not provided
            payment_terms=int(request.form['payment_terms']),
            invoice_description=request.form.get('invoice_description', ''),  # default to empty if not provided
            receiver=request.form['receiver'],
            created_by=request.form['created_by'],  # Adjust based on session or auth context
            invoice_status=request.form['invoice_status']
        )
        db.session.add(new_invoice)
        db.session.flush()  # Flush to assign an ID to new_invoice

        # Handling dynamically added invoice items
        item_descriptions = request.form.getlist('description[]')
        item_quantities = request.form.getlist('quantity[]')
        item_prices = request.form.getlist('price[]')

        for desc, qty, price in zip(item_descriptions, item_quantities, item_prices):
            item = InvoiceItem(
                invoice_id=new_invoice.id,
                description=desc,
                quantity=int(qty),
                price=float(price)
            )
            db.session.add(item)

        db.session.commit()
        return redirect(url_for('some_function_name'))  # Redirect or return a success message

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400