from flask import Flask, send_from_directory, jsonify, request, Response, Blueprint
import os
from flask_cors import CORS
from app.DORApy import check_tableau_DORA, creation_carte,manipulation_MO
from app.DORApy import gestion_admin,creation_tableau_vierge_DORA,creation_carte,check_tableau_DORA


from api import api_bp
import jwt
import datetime
import sys
import tempfile

Carto_bp = Blueprint('Carto', __name__)
SECRET_JKEY = os.getenv('SECRET_JKEY')


@Carto_bp.route('/bb_box', methods=['GET'])
def bbox():
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({'message': 'Token is missing'}), 403
    try:
        decoded_token = jwt.decode(token, SECRET_JKEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 403
    print("coucou", file=sys.stderr)
    dict_bb_box=creation_carte.creation_bb_REF("DEP","33")
    
    print(jsonify(dict_bb_box), file=sys.stderr)
    return jsonify(dict_bb_box)