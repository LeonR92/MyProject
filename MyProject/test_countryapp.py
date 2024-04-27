import pytest
import requests_mock
from flask import template_rendered
from contextlib import contextmanager


# Test client setup
@pytest.fixture
def client():
    from app import create_app  # import entry point

    app = create_app()
    app.config.update = {"TESTING": True}
    with app.test_client() as client:
        yield client


# Capture template
@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


def test_get_countries(client):
    with requests_mock.Mocker() as m:
        # MOCK API and test data
        m.get(
            "https://restcountries.com/v3.1/all",
            json=[
                {
                    "name": {"common": "Test Country"},
                    "population": 123456,
                    "continents": ["Testland"],
                    "languages": {"eng": "English"},
                    "flags": {"svg": "http://example.com/flag.svg"},
                }
            ],
        )

        # Test
        with client.application.app_context():
            with captured_templates(client.application) as templates:
                response = client.get("/country/")
                # Status code and error handling
                assert (
                    response.status_code == 200
                ), "Expected HTTP 200, but got {0}".format(response.status_code)

                # Test template
                assert len(templates) == 1, "Template was not rendered"
                template, context = templates[0]
                assert (
                    template.name == "country/country.html"
                ), "Incorrect template rendered"

                # Assertion
                assert "countries" in context, "Countries not in context"
                assert (
                    len(context["countries"]) == 1
                ), "Incorrect number of countries in context"
                assert (
                    context["countries"][0]["name"]["common"] == "Test Country"
                ), "Country name does not match expected"
