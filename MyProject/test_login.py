import pytest
from app import create_app, db
from flask import url_for
from users import UserModel


@pytest.fixture
def app():
    """Create and return a Flask app with a test configuration."""
    _app = create_app(test_config=True)
    with _app.app_context():
        db.create_all()
    yield _app
    with _app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client using the Flask app returned from the app fixture."""
    return app.test_client()


def test_registration(client):
    """Test user registration flow."""
    response = client.post(
        "/register",
        data={"username": "newuser", "password": "newpassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Login" in response.get_data(
        as_text=True
    )  # Checking for text in the response


def test_login(client, app):
    """Test user login flow."""
    with app.app_context():
        user = UserModel(username="testuser")
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpass"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Welcome" in response.get_data(as_text=True)


def test_logout(client, app):
    """Test logout functionality."""
    with app.app_context():
        test_login(client, app)  # Log in the user before attempting to log out

    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert "Login" in response.get_data(as_text=True)
