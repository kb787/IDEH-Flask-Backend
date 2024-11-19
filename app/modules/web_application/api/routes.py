from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from http import HTTPStatus
from methods import UserService


user_bp = Blueprint('user', __name__, url_prefix='/api/users')
def create_response(data=None, message=None, status=HTTPStatus.OK):
    response = {}
    if data is not None:
        response['data'] = data
    if message is not None:
        response['message'] = message
    return jsonify(response), status

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('', methods=['POST'])
def create_user():

    try:
        data = request.get_json()
        required_fields = ['name', 'email']
        if not all(field in data for field in required_fields):
            return create_response(
                message="Missing required fields",
                status=HTTPStatus.BAD_REQUEST
            )

        user = UserService.create_user(
            name=data['name'],
            email=data['email'],
            social_login_provider=data.get('social_login_provider'),
            profile_picture=data.get('profile_picture')
        )

        if user:
            return create_response(
                data={'user_id': user.id},
                message="User created successfully",
                status=HTTPStatus.CREATED
            )
        return create_response(
            message="Email already exists",
            status=HTTPStatus.CONFLICT
        )

    except Exception as e:
        return create_response(
            message=str(e),
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )

@user_bp.route('', methods=['GET'])
def get_users():
    try:
        search_term = request.args.get('search')
        provider = request.args.get('provider')

        if search_term:
            users = UserService.search_users(search_term)
        elif provider:
            users = UserService.get_users_by_provider(provider)
        else:
            users = UserService.get_all_users()

        return create_response(
            data=[{
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'social_login_provider': user.social_login_provider,
                'profile_picture': user.profile_picture,
                'created_at': user.created_at.isoformat()
            } for user in users]
        )

    except Exception as e:
        return create_response(
            message=str(e),
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = UserService.get_user_by_id(user_id)
        if not user:
            return create_response(
                message="User not found",
                status=HTTPStatus.NOT_FOUND
            )

        return create_response(
            data={
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'social_login_provider': user.social_login_provider,
                'profile_picture': user.profile_picture,
                'created_at': user.created_at.isoformat()
            }
        )

    except Exception as e:
        return create_response(
            message=str(e),
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user_route(user_id):
    try:
        data = request.get_json()
        user = UserService.update_user(user_id, **data)

        if not user:
            return create_response(
                message="User not found",
                status=HTTPStatus.NOT_FOUND
            )

        return create_response(
            message="User updated successfully",
            data={
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'social_login_provider': user.social_login_provider,
                'profile_picture': user.profile_picture,
                'created_at': user.created_at.isoformat()
            }
        )

    except Exception as e:
        return create_response(
            message=str(e),
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user_route(user_id):
    try:
        success = UserService.delete_user(user_id)
        if success:
            return create_response(
                message="User deleted successfully"
            )
        return create_response(
            message="User not found",
            status=HTTPStatus.NOT_FOUND
        )

    except Exception as e:
        return create_response(
            message=str(e),
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )

@user_bp.route('/<int:user_id>/profile-picture', methods=['POST'])
def upload_profile_picture(user_id):
    try:
        if 'file' not in request.files:
            return create_response(
                message="No file provided",
                status=HTTPStatus.BAD_REQUEST
            )

        file = request.files['file']
        if file.filename == '':
            return create_response(
                message="No selected file",
                status=HTTPStatus.BAD_REQUEST
            )

        if not allowed_file(file.filename):
            return create_response(
                message="File type not allowed",
                status=HTTPStatus.BAD_REQUEST
            )

        file_path = UserService.upload_profile_picture(user_id, file)
        if file_path:
            return create_response(
                message="Profile picture uploaded successfully",
                data={'profile_picture_path': file_path}
            )
        
        return create_response(
            message="Upload failed or user not found",
            status=HTTPStatus.BAD_REQUEST
        )

    except Exception as e:
        return create_response(
            message=str(e),
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )

@user_bp.route('/email/<email>', methods=['GET'])
def get_user_by_email(email):
    try:
        user = UserService.get_user_by_email(email)
        if not user:
            return create_response(
                message="User not found",
                status=HTTPStatus.NOT_FOUND
            )

        return create_response(
            data={
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'social_login_provider': user.social_login_provider,
                'profile_picture': user.profile_picture,
                'created_at': user.created_at.isoformat()
            }
        )

    except Exception as e:
        return create_response(
            message=str(e),
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )