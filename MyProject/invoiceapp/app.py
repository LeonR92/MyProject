from flask import Blueprint, jsonify, render_template
import requests
from utils import cache
from flask_login import login_required


# Define the blueprint
invoice = Blueprint("invoice", __name__, template_folder="templates")


@invoice.before_request
@login_required
def before_request():
    """Ensure user is logged in before accessing any country routes."""
    pass

@invoice.route("/")
def index():
    return "Hello Invoice"