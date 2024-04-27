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
    
    # Configure Dashboard app
    dashboard1(app)
    @app.before_request
    def before_request_func():
        # Check if the requested path is part of the Dash app's path
        if '/dashboard1/' in request.path:
            # Check if the user is not authenticated
            if not current_user.is_authenticated:
                # Redirect to login page if the user is not authenticated
                return redirect(url_for('login'))


    if test_config:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(ProductionConfig)

    app.config["SECRET_KEY"] = "1283123k!jkjasd012klajsdAdasd!!@"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=1)
    app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=7)
    app.config["REMEMBER_COOKIE_SECURE"] = True
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users_login.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
    #app.config['SESSION_COOKIE_SECURE'] = True

    #  Rate Limiter to prevent DoS
    limiter = Limiter(
        app = app,
        key_func=get_remote_address,  # This function determines the client's IP address
        default_limits=["400 per day, 70 per hour"]  # This sets a general rate limit
    )

    db.init_app(app)  # Initialize the db with the app context


    with app.app_context():
        db.create_all()

    # Initialize Flask-SQLAlchemy and Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    # Import blueprints
    from countryapp.app import (
        country,
    )  # Ensure this import is correct based on your directory structure

    # Register blueprints
    app.register_blueprint(country, url_prefix="/country")

    # Register Compress and cache to Flask app
    Compress(app)
    cache.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return UserModel.query.get(int(user_id))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            if UserModel.query.filter_by(username=username).first():
                flash("Username already exists.")
                return redirect(url_for("register"))

            new_user = UserModel(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    @limiter.limit("20 per day")
    def login():
        if request.method == "POST":
            if request.form.get('password_confirm'):  # Honey Pot
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
        return "Welcome, " + current_user.username

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
    )  # Consider using `debug=True` only in a development environment
