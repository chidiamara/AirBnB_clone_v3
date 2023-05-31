#!/usr/bin/python3
"""
Flask Application
"""

from models import storage
from api.v1.views import app_views
from flask import Flask, jsonify, make_response
from os import environ
from flask_cors import CORS

app = Flask(__name__)
app.register_blueprint(app_views)
cors = CORS(app, resources={r"/api/v1*": {"origins": "0.0.0.0"}})


@app.teardown_appcontext
def close_db(error):
    """ Close Storage
    This function is executed after each request
    to close the database connection.
    """
    storage.close()


@app.errorhandler(404)
def invalid_route(e):
    """Handle all 404 errors"""
    return jsonify({"error": "Not found"})


if __name__ == "__main__":
    """ Main Function
    The entry point of the application.
    It runs the Flask app on the specified host and port
    """
    host = environ.get('HBNB_API_HOST')
    port = environ.get('HBNB_API_PORT')
    if not host:
        host = '0.0.0.0'
    if not port:
        port = '5000'
    app.run(host=host, port=port, threaded=True)
