class Config:
    """Base configuration."""

    SECRET_KEY = "1283123k!jkjasd012klajsdAdasd!!@"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///default.db"  # Default. Should be overridden in specific configs.
    )


class ProductionConfig(Config):
    """Production specific configuration"""

    SQLALCHEMY_DATABASE_URI = "sqlite:///users_login.db"


class TestConfig(Config):
    """Testing specific configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Use in-memory database for tests.
    WTF_CSRF_ENABLED = False  # Disable CSRF tokens in the testing configuration.
