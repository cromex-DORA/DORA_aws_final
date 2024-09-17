import jwt
from functools import wraps
from flask import request, jsonify, current_app

def check_token_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 403

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            if data['role'] != 'admin':
                return jsonify({'message': 'Admin access required'}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 403

        return f(*args, **kwargs)
    return decorated_function