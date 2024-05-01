from flask import (
    Flask,
    send_from_directory,
    make_response,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from flask_compress import Compress
from flask_limiter import Limiter
from flask_simple_captcha import CAPTCHA
from flask_limiter.util import get_remote_address
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask_sqlalchemy import SQLAlchemy
from users import db, UserModel
from config import ProductionConfig, TestConfig
from datetime import timedelta
from utils import cache
from dashboard1.dashboard1 import dashboard1

# Create the Flask application


def create_app(test_config=False):
    """Create and configure an instance of the Flask application."""

    # Initialise Flask and configurations
    app = Flask(__name__, static_folder="./static")

    if test_config:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(ProductionConfig)

    app.config["SECRET_KEY"] = "1283123k!jkjasd012klajsdAdasd!!@"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
    app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=7)
    app.config["REMEMBER_COOKIE_SECURE"] = True
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users_login.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
    # app.config['SESSION_COOKIE_SECURE'] = True

    # Initialize Flask-Simple-Captcha
    YOUR_CONFIG = {
        "SECRET_CAPTCHA_KEY": "ajhsdkjasd72613asdhj",
        "CAPTCHA_LENGTH": 6,
        "CAPTCHA_DIGITS": False,
        "EXPIRE_SECONDS": 600,
    }
    SIMPLE_CAPTCHA = CAPTCHA(config=YOUR_CONFIG)
    app = SIMPLE_CAPTCHA.init_app(app)

    #  Rate Limiter to prevent DoS
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,  # This function determines the client's IP address
        default_limits=["400 per day, 70 per hour"],  # This sets a general rate limit
    )

    db.init_app(app)  # Initialize the db with the app context
    with app.app_context():
        db.create_all()

    # Initialize Flask-SQLAlchemy and Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    # Register Compress and cache to Flask app
    Compress(app)
    cache.init_app(app)

    # Import blueprints
    from countryapp.app import (
        country,
    )  # Ensure this import is correct based on your directory structure

    # Register blueprints
    app.register_blueprint(country, url_prefix="/country")

    # Configure Dashboard app
    dashboard1(app)

    @app.before_request
    def before_request_func():
        """
        Before request to limit request and check for login status
        """ 
        if "/dashboard1/" in request.path:
            # Check if the user is not authenticated and added rate limiter to prevent burst
            limiter.limit("15 per minute")(lambda: request.path)()
            if not current_user.is_authenticated:
                # Redirect to login page if the user is not authenticated
                return redirect(url_for("login"))

    @login_manager.user_loader
    def load_user(user_id):
        return UserModel.query.get(int(user_id))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        # Handle GET request to display the registration form with a new CAPTCHA
        if request.method == "GET":
            new_captcha_dict = SIMPLE_CAPTCHA.create()
            return render_template("register.html", captcha=new_captcha_dict)

        # Handle POST request to process the form submission
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            c_hash = request.form.get("captcha-hash")
            c_text = request.form.get("captcha-text")

            # First, verify the CAPTCHA
            if not SIMPLE_CAPTCHA.verify(c_text, c_hash):
                flash("Invalid CAPTCHA.", "error")
                return redirect(url_for("register"))

            # Check if the username already exists in the database
            if UserModel.query.filter_by(username=username).first():
                flash("Username already exists.", "error")
                return redirect(url_for("register"))

            # If passed all checks, add the new user to the database
            new_user = UserModel(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    @limiter.limit("20 per day")
    def login():
        if request.method == "POST":
            if request.form.get("password_confirm"):  # Honey Pot
                return "Success"

            username = request.form["username"]
            password = request.form["password"]
            remember = request.form.get("remember") == "on"
            user = UserModel.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user, remember=remember)
                if remember:
                    session.permanent = True
                return redirect(url_for("home"))
            else:
                return redirect(url_for("error"))
        return render_template("login.html")

    @app.route("/error")
    def error():
        return render_template("error.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.route("/")
    @login_required
    def home():
        return render_template("homepage.html")

    def custom_static_handler(filename):
        # Use the built-in method to serve static files
        response = send_from_directory(app.static_folder, filename)

        # Modify the Cache-Control header
        response.headers["Cache-Control"] = "public, max-age=3600"  # Cache for 1 hour

        return response

    app.send_static_file = custom_static_handler

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        debug=True, host="192.168.2.31"
    )  # Remove debug=True when deploying to production
