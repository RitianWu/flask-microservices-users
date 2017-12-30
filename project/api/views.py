# project/api/views.py


from flask import Blueprint, jsonify, request, render_template
from project import db
from project.api.models import User
from sqlalchemy import exc

users_blueprint = Blueprint('users', __name__, template_folder='./templates')


@users_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'Pong'
    })


@users_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        db.session.add(User(username=username, email=email))
        db.session.commit()
    users = User.query.order_by(User.create_time.desc()).all()
    return render_template('index.html', users=users)


@users_blueprint.route('/users', methods=['POST'])
def add_user():
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload'
        }
        return jsonify(response_object), 400
    username = post_data.get('username')
    email = post_data.get('email')
    try:
        user = User.query.filter(User.email == email).first()
        if not user:
            user_object = User(username=username, email=email)
            db.session.add(user_object)
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'User add success',
                'data': {
                    'user_id': user_object.id
                }
            }
            return jsonify(response_object), 201
        else:
            response_object = {
                'status': 'fail',
                'message': 'User already exists'
            }
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload'
        }
        return jsonify(response_object), 400


@users_blueprint.route('/users/<user_id>', methods=['GET'])
def get_single_user(user_id):
    """Get single user details"""
    response_object = {
        'status': 'fail',
        'message': 'User does not exist'
    }
    try:
        user_object = User.query.filter(User.id == int(user_id)).first()
        if not user_object:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'message': 'Query success',
                'data': {
                    'username': user_object.username,
                    'email': user_object.email,
                    'create_time': user_object.create_time
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@users_blueprint.route('/users', methods=['GET'])
def get_all_users():
    """Get all users"""
    users = User.query.all()
    users_list = []
    for user in users:
        user_object = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'create_time': user.create_time
        }
        users_list.append(user_object)
    response_object = {
        'status': 'success',
        'message': 'Query success',
        'data': {
            'users': users_list
        }
    }
    return jsonify(response_object), 200
