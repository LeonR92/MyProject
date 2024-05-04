from flask import Blueprint, jsonify, render_template,request
import requests
from utils import cache
from flask_login import login_required
from dictionary.utils import flatten_data

dictionary = Blueprint("dictionary", __name__, template_folder="templates")


@dictionary.before_request
@login_required
def before_request():
    """Ensure user is logged in before accessing any dictionary routes."""
    pass

@dictionary.route("/")
def index():
    # Simply render the form when the method is GET.
    return render_template('dictionary/index.html')


@dictionary.route("/search", methods=["POST"])
def search():
    # Get the word from the form.
    word = request.form['word']
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.ok:
        data = response.json()
        flat_data = flatten_data(data)

        # Redirect to a GET route that shows the results, or handle the display here.
        return render_template('dictionary/results.html', data=flat_data)
    else:
        # Render an error template or redirect to an error handling route.
        return "Word not found"