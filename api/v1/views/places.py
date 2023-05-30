#!/usr/bin/python3
"""
This file contains the Place module
"""

from api.v1.views import app_views
from flask import jsonify, abort, request, make_response
from models import storage
from models.place import Place
from models.city import City
from models.user import User
from models.amenity import Amenity
from models.state import State
from flasgger.utils import swag_from


@app_views.route('/cities/<string:city_id>/places',
                 methods=['GET'], strict_slashes=False)
@swag_from('documentation/places/get.yml', methods=['GET'])
def get_all_places(city_id):
    """
    Get all places for a city
    """
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<string:place_id>', methods=['GET'],
                 strict_slashes=False)
@swag_from('documentation/places/get_id.yml', methods=['GET'])
def get_place(place_id):
    """
    Get a place by ID
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<string:place_id>', methods=['DELETE'],
                 strict_slashes=False)
@swag_from('documentation/places/delete.yml', methods=['DELETE'])
def delete_place(place_id):
    """
    Delete a place by ID
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    place.delete()
    storage.save()
    return jsonify({})


@app_views.route('/cities/<string:city_id>/places', methods=['POST'],
                 strict_slashes=False)
@swag_from('documentation/places/post.yml', methods=['POST'])
def create_place(city_id):
    """
    Create a new place for a city
    """
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    if 'user_id' not in request.get_json():
        return make_response(jsonify({"error": "Missing user_id"}), 400)
    if 'name' not in request.get_json():
        return make_response(jsonify({"error": "Missing name"}), 400)
    place_data = request.get_json()
    place_data['city_id'] = city_id
    user = storage.get(User, place_data['user_id'])
    if user is None:
        abort(404)
    place = Place(**place_data)
    place.save()
    return jsonify(place.to_dict()), 201


@app_views.route('/places/<string:place_id>', methods=['PUT'],
                 strict_slashes=False)
@swag_from('documentation/places/put.yml', methods=['PUT'])
def update_place(place_id):
    """
    Update a place by ID
    """
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    for key, value in request.get_json().items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)
    storage.save()
    return jsonify(place.to_dict())


@app_views.route('/places_search', methods=['POST'],
                 strict_slashes=False)
@swag_from('documentation/places/search.yml', methods=['POST'])
def search_places():
    """
    Search places by ID, cities, or amenities
    """
    if request.get_json() is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    data = request.get_json()

    if not data or not any([data.get('states'),
                            data.get('cities'),
                            data.get('amenities')]):
        places = storage.all(Place).values()
        place_list = [place.to_dict() for place in places]
        return jsonify(place_list)

    states = [storage.get(State, state_id)
              for state_id in data.get('states', [])]
    cities = [storage.get(City, city_id)
              for city_id in data.get('cities', [])]
    amenities = [storage.get(Amenity, amenity_id)
                 for amenity_id in data.get('amenities', [])]

    place_list = []

    for state in states:
        if state:
            for city in state.cities:
                if city:
                    for place in city.places:
                        place_list.append(place)

    for city in cities:
        if city:
            for place in city.places:
                if place not in place_list:
                    place_list.append(place)

    if amenities:
        if not place_list:
            place_list = storage.all(Place).values()
        place_list = [place for place in place_list
                      if all([amenity in place.amenities
                              for amenity in amenities])]

    result = [place.to_dict() for place in place_list]
    for place_dict in result:
        place_dict.pop('amenities', None)

    return jsonify(result)
