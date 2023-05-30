#!/usr/bin/python3
"""
City module
"""

from api.v1.views import app_views
from flask import jsonify, abort, request, make_response
from models import storage
from models.state import State
from models.cities import City


@app_views.route('/states/<state_id>/cities', methods=['GET'],
                 strict_slashes=False)
def get_all_cities():
    """
    Get all citys
    """
    all_list = [obj.to_dict() for obj in storage.all(State).values()]
    return jsonify(all_list)


@app_views.route('/states/<string:state_id>/cities', methods=['GET'],
                 strict_slashes=False)
def get_city(city_id):
    """
    Get a city by ID
    """
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    return jsonify(city.to_dict())


@app_views.route('/cities/<string:city_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_city(city_id):
    """
    Delete a city by ID
    """
    city = storage.get(State, city_id)
    if city is None:
        abort(404)
    city.delete()
    storage.save()
    return jsonify({})


@app_views.route('/states/<string:state_id>/cities', methods=['POST'],
                 strict_slashes=False)
def create_city():
    """
    Create a new city
    """
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    if 'name' not in request.get_json():
        return make_response(jsonify({"error": "Missing name"}), 400)
    city_data = request.get_json()
    city = City(**city_data)
    city.save()
    return jsonify(city.to_dict()), 201


@app_views.route('/cities/<string:city_id>', methods=['PUT'],
                 strict_slashes=False)
def update_city(city_id):
    """
    Update a city by ID
    """
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    for key, value in request.get_json().items():
        if key not in ['id', 'created_at', 'updated']:
            setattr(City, key, value)
    storage.save()
    return jsonify(city.to_dict())
