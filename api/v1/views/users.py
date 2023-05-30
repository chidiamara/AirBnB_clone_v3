#!/usr/bin/python3
"""
This file contains the User module
"""

from api.v1.views import app_views
from flask import jsonify, abort, request, make_response
from models import storage
from models.user import User
from flasgger.utils import swag_from


@app_views.route('/users', methods=['GET'], strict_slashes=False)
@swag_from('documentation/user/get.yml', methods=['GET'])
def get_all_users():
    """
    Get all users
    """
    users = [user.to_dict() for user in storage.all(User).values()]
    return jsonify(users)


@app_views.route('/users/<string:user_id>', methods=['GET'],
                 strict_slashes=False)
@swag_from('documentation/user/get_id.yml', methods=['GET'])
def get_user(user_id):
    """
    Get a user by ID
    """
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    return jsonify(user.to_dict())


@app_views.route('/users/<string:user_id>', methods=['DELETE'],
                 strict_slashes=False)
@swag_from('documentation/user/delete.yml', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete a user by ID
    """
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    user.delete()
    storage.save()
    return jsonify({})


@app_views.route('/users/', methods=['POST'],
                 strict_slashes=False)
@swag_from('documentation/user/post.yml', methods=['POST'])
def create_user():
    """
    Create a new user
    """
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    if 'email' not in request.get_json():
        return make_response(jsonify({"error": "Missing email"}), 400)
    if 'password' not in request.get_json():
        return make_response(jsonify({"error": "Missing password"}), 400)
    user_data = request.get_json()
    user = User(**user_data)
    user.save()
    return jsonify(user.to_dict()), 201


@app_views.route('/users/<string:user_id>', methods=['PUT'],
                 strict_slashes=False)
@swag_from('documentation/user/put.yml', methods=['PUT'])
def update_user(user_id):
    """
    Update a user by ID
    """
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    for key, value in request.get_json().items():
        if key not in ['id', 'email', 'created_at', 'updated_at']:
            setattr(user, key, value)
    storage.save()
    return jsonify(user.to_dict())