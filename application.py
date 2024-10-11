from flask import Flask, send_from_directory, jsonify, request, Response
import os
from flask_cors import CORS
from app.DORApy import check_tableau_DORA, creation_carte,manipulation_MO
from app.DORApy.security import gestion_db_users,gestion_file_upload
from app.DORApy.classes.modules import connect_path
from app.DORApy import gestion_admin,creation_tableau_vierge_DORA,creation_carte,check_tableau_DORA
from api import dict_geom_REF,dict_dict_info_REF
from app.DORApy.classes.Class_NDictGdf import NDictGdf
from app.DORApy.classes.Class_NGdfREF import NGdfREF

from api import api_bp
from app.blueprints.MilieuxAqua import MilieuxAqua_bp
from app.blueprints.Carto import Carto_bp

import jwt
import datetime
import sys
import tempfile

app = Flask(__name__, static_folder='frontend/build')
CORS(app, resources={r"/*": {"origins": "*"}})  # Remplacez '*' par les domaines spécifiques si possible
app.register_blueprint(api_bp)
app.register_blueprint(Carto_bp)
app.register_blueprint(MilieuxAqua_bp)
SECRET_JKEY = os.getenv('SECRET_JKEY')

dict_users = gestion_admin.import_dict_users_s3()



@app.route('/login', methods=['POST'])
def login():
    print("coucou", file=sys.stderr)
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = dict_users.get(email)

    if user:
        print(f"User found: {user}", file=sys.stderr)
    else:
        print("User not found", file=sys.stderr)

    if user and gestion_admin.verify_password(password, user['password']):
        
        token = jwt.encode({
            'user': email,
            'role': user['role'],
            'CODE_DEP' : user['dep'],
            'exp': datetime.datetime.now() + datetime.timedelta(hours=1)
        }, SECRET_JKEY, algorithm='HS256')
        response = jsonify({'token': token, 'role': user['role']})

        print(response.data, file=sys.stderr)
        return response, 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/info/<string:id>', methods=['GET'])
def get_info(id):
    # Vérifiez si l'ID existe dans vos donnée
    info = {
        "id": "techon, toujours pareil",
        "name": id}

    if info:
        return jsonify(info), 200
    else:
        return jsonify({'error': 'ID not found'}), 404

@app.route('/download_file', methods=['GET'])
def download_file():
    file_key = request.args.get('file_key')
    if not file_key:
        return jsonify({'error': 'File path is required'}), 400
    print(file_key)
    url = connect_path.download_file_from_s3("CUSTOM",file_key)
    return jsonify({'url': url})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path != "" and os.path.exists(os.path.join('frontend/build', path)):
        return send_from_directory('frontend/build', path)
    else:
        return send_from_directory('frontend/build', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port,debug=True)
