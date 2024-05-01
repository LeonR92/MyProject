from flask import Blueprint, jsonify, render_template
import requests
from utils import cache
from flask_login import login_required


# Define the blueprint
country = Blueprint("country", __name__, template_folder="templates")


@country.before_request
@login_required
def before_request():
    """Ensure user is logged in before accessing any country routes."""
    pass


@country.route("/")
@cache.cached(timeout=24 * 60 * 60)  # One hour cache
def get_countries():
    """
    This route pulls data from API, which is the source data
    """
    # Main URL
    url = "https://restcountries.com/v3.1/all"

    # Error Handling
    try:
        # GET response
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch countries", "message": str(e)}), 500

    # Load the JSON data returned by the API
    countries = response.json()

    return render_template("country/country.html", countries=countries)
