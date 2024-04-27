import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from utils import cache


def dashboard1(flask_app):
    """
    Create a Dash application that is served through an existing Flask application.

    Args:
        flask_app: The Flask application instance.

    Returns:
        dash.Dash: The Dash application configured to integrate with the Flask server.
    """
    # Create a Dash instance that shares the Flask server
    app = dash.Dash(server=flask_app, url_base_pathname='/dashboard1/', suppress_callback_exceptions=True)
    app.title = 'My Dashboard'

    # Configure the Dash app layout
    app.layout = html.Div([
        html.H1('Dashboard 1'),
        dcc.Graph(id='example-graph', figure={
            'data': [{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                     {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'}],
            'layout': {'title': 'Dash Data Visualization'}
        })
    ])

    # Example of a simple callback
    @app.callback(
        Output('example-graph', 'figure'),
        [Input('example-graph', 'hoverData')]
    )
    @cache.memoize(timeout = 3600)
    def update_graph(hoverData):
        return {
            'data': [{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                     {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'}],
            'layout': {'title': 'Dash Data Visualization Updated'}
        }

