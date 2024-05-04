from flask import Blueprint, jsonify, render_template
import requests
from utils import cache
from flask_login import login_required

dictionary = Blueprint("dictionary", __name__, template_folder="templates")


@dictionary.before_request
@login_required
def before_request():
    """Ensure user is logged in before accessing any dictionary routes."""
    pass


@dictionary.route("/")
def index():
    return "Hello"