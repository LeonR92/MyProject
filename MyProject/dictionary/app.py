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


@dictionary.route("/<string:word>")
def index(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.ok:
        data = response.json()
        return render_template('dictionary/index.html', word=word, meanings=data[0]['meanings'])
    else:
        return render_template('error.html', message="Word not found")