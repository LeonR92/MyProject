from flask import Blueprint, jsonify, render_template
import requests
from utils import cache
from flask_login import login_required
from invoiceapp.models import Invoice,Favorite,InvoiceItem


# Define the blueprint
invoice = Blueprint("invoice", __name__, template_folder="templates")

@invoice.before_request
@login_required
def before_request():
    """Ensure user is logged in before accessing any country routes."""
    pass

@invoice.route("/")
def index():
    return render_template("invoice/index.html")


@invoice.route('/newinvoice',methods=['POST'])
def new_invoice():
    pass