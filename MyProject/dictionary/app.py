from flask import Blueprint, jsonify, render_template,request,session
import requests
from utils import cache
from flask_login import login_required
from dictionary.utils import flatten_data,get_random_word

dictionary = Blueprint("dictionary", __name__, template_folder="templates")




@dictionary.before_request
@login_required
def before_request():
    """Ensure user is logged in before accessing any dictionary routes."""
    pass


@dictionary.route("/")
def index():
    word = session['recent_searches'][-1]
    print(session['recent_searches'])
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.ok:
        data = response.json()
        flat_data = flatten_data(data)
        return render_template('dictionary/index.html', data=flat_data)
    else:
        return "Word not found"



@dictionary.route("/search", methods=["POST"])
def search():
    # Get the word from the form.
    word = request.form['word']
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.ok:
        data = response.json()
        flat_data = flatten_data(data)
        if 'recent_searches' not in session:
            session['recent_searches'] = []  # Initialize if not present
            session['recent_searches'].append(word)  # Append the new word
            session['recent_searches'] = session['recent_searches'][-5:]  # Keep only the last 5 entries
            session.modified = True
        else:
            session['recent_searches'].append(word)  # Append the new word
            session['recent_searches'] = session['recent_searches'][-5:]  # Keep only the last 5 entries
            session.modified = True
        # Redirect to a GET route that shows the results, or handle the display here.
        return render_template('dictionary/results.html', data=flat_data)
    else:
        # Render an error template or redirect to an error handling route.
        return "Word not found"