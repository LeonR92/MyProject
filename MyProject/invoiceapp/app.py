from flask import Blueprint, jsonify, render_template, request, url_for, redirect, flash
import requests
from utils import cache
from flask_login import login_required
from invoiceapp.models import Invoice, InvoiceItem, Base
from app import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


# Define the blueprint
invoice = Blueprint("invoice", __name__, template_folder="templates")

engine = create_engine("sqlite:///invoice.db")  # Update the connection string as needed
Session = sessionmaker(bind=engine)


@invoice.before_request
@login_required
def before_request():
    """Ensure user is logged in before accessing any invoice routes."""
    pass


@invoice.route("/")
def index():
    session = Session()
    try:
        invoices = session.query(Invoice).all()
        return render_template("invoice/index.html", invoices=invoices)
    finally:
        # Ensure that the session is closed after the request
        session.close()


# TODO add data validation
# Auto Calculation
@invoice.route("/newinvoice", methods=["POST"])
def new_invoice():
    session = Session()
    try:
        # Extract data from form fields and calculate total amount
        item_descriptions = request.form.getlist("description[]")
        item_quantities = request.form.getlist("quantity[]")
        item_prices = request.form.getlist("price[]")
        total_amount = sum(
            int(qty) * float(price) for qty, price in zip(item_quantities, item_prices)
        )

        # Create new invoice object
        new_invoice = Invoice(
            invoice_num=request.form["invoice_num"],
            invoice_amount=total_amount,
            sender_address=request.form["sender_address"],
            receiver_address=request.form["receiver_address"],
            invoice_date=request.form.get("invoice_date", datetime.utcnow()),
            #  payment_terms=int(request.form['payment_terms']),
            # invoice_description=request.form.get('invoice_description', ''),
            # receiver=request.form['receiver'],
            # created_by=request.form['created_by'],
            invoice_status=request.form["invoice_status"],
        )
        session.add(new_invoice)
        session.commit()
        # Add invoice items
        for desc, qty, price in zip(item_descriptions, item_quantities, item_prices):
            item = InvoiceItem(
                invoice_id=new_invoice.id,
                description=desc,
                quantity=int(qty),
                price=float(price),
            )
            session.add(item)

        session.commit()
        flash("Invoice created successfully!")
        return redirect(
            url_for("invoice.index")
        )  # Redirect to index or a confirmation page
    except Exception as e:
        session.rollback()
        flash(f"An error occurred: {e}")
        return f"{e}"
    finally:
        session.close()


@invoice.route("/update", methods=["POST"])
def update_invoice():
    """
    Endpoint to update invoice details.
    """
    session = Session()
    try:
        # Extract data from form fields
        invoice_num = request.form.get("invoice_num")
        sender_address = request.form.get("sender_address")
        receiver_address = request.form.get("receiver_address")
        item_descriptions = request.form.getlist("description[]")
        item_quantities = request.form.getlist("quantity[]")
        item_prices = request.form.getlist("price[]")
        invoice_status = request.form.get("invoice_status")

        # Find the existing invoice by its number
        invoice = session.query(Invoice).filter_by(invoice_num=invoice_num).first()
        if not invoice:
            flash(f"Invoice {invoice_num} not found.")
            return redirect(url_for("invoice.index"))

        # Update invoice fields
        invoice.sender_address = sender_address
        invoice.receiver_address = receiver_address
        invoice.invoice_status = invoice_status

        # Calculate total amount and update items
        total_amount = sum(
            int(qty) * float(price) for qty, price in zip(item_quantities, item_prices)
        )
        invoice.invoice_amount = total_amount

        # Clear existing items
        session.query(InvoiceItem).filter_by(invoice_id=invoice.id).delete()

        # Add updated items
        for desc, qty, price in zip(item_descriptions, item_quantities, item_prices):
            item = InvoiceItem(
                invoice_id=invoice.id,
                description=desc,
                quantity=int(qty),
                price=float(price),
            )
            session.add(item)

        session.commit()
        flash("Invoice updated successfully!")
        return redirect(
            url_for("invoice.index")
        )  # Redirect to index or a confirmation page
    except Exception as e:
        session.rollback()
        flash(f"An error occurred: {e}")
        return f"{e}", 400
    finally:
        session.close()
