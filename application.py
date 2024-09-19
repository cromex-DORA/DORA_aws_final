from flask import Flask, send_from_directory, jsonify, request, Response
import os
from flask_cors import CORS
from app.DORApy import creation_carte,ajout_MO_ou_PPG
from app.DORApy.security import gestion_db_users,gestion_file_upload
from app.DORApy.classes.modules import connect_path
from app.DORApy import gestion_admin,creation_tableau_vierge_DORA,creation_carte
from api import api_bp
import jwt
import datetime
import sys
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='frontend/build')
CORS(app, resources={r"/*": {"origins": "*"}})  # Remplacez '*' par les domaines spécifiques si possible
app.register_blueprint(api_bp)
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


@app.route('/geojson_complet_folders', methods=['GET'])
def geojson_complet_folders():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 403

    try:
        decoded_token = jwt.decode(token, SECRET_JKEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 403

    dict_sous_dossiers = gestion_db_users.dossiers_secondaires_user(decoded_token)

    CODE_DEP = decoded_token['CODE_DEP']
    print(CODE_DEP, file=sys.stderr)
    geojson_data_MO_gemapi=creation_carte.creation_carto_syndicats(CODE_DEP)

    dict_folders = {item['id']:item for item in dict_sous_dossiers}

    for num,feature in enumerate(geojson_data_MO_gemapi['features']):
        if feature['id'] in dict_folders:
            geojson_data_MO_gemapi['features'][num]['properties'] = dict_folders[feature['id']] | feature['properties']


    response = geojson_data_MO_gemapi
    return jsonify(response), 200

@app.route('/bb_box', methods=['GET'])
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


@app.route('/vierge_DORA', methods=['POST'])
def creer_tableau_vierge_DORA():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 403

    try:
        decoded_token = jwt.decode(token, SECRET_JKEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 403 
    
    print(request.form)
    id_folder = request.form.get('id', '')
    name = request.form.get('name', '')
    path = os.path.join("MO_gemapi",id_folder)

    df_vierge_MO = creation_tableau_vierge_DORA.create_tableau_vierge_DORA([name])

    path = os.path.join("MO_gemapi",id_folder,"tableau_vierge_" + name + ".xlsx")

    connect_path.upload_file_vers_s3("custom",df_vierge_MO,path)

    return jsonify({'message': 'File created successfully'}), 201

@app.route('/download_file', methods=['GET'])
def download_file():
    file_key = request.args.get('file_key')
    if not file_key:
        return jsonify({'error': 'File path is required'}), 400
    print(file_key)
    url = connect_path.download_file_from_s3("custom",file_key)
    return jsonify({'url': url})

@app.route('/upload_MO_gemapi', methods=['POST'])
def upload_MO_gemapi():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 403

    try:
        decoded_token = jwt.decode(token, SECRET_JKEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 403 

    files = request.files.getlist('files')

    temp_dir = tempfile.mkdtemp()

    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)

    # Create a temporary directory to save uploaded files
    try:
        geojson = ajout_MO_ou_PPG.conv_shp_en_geojson(files,temp_dir)
        # Read the shapefiles using geopandas
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
        os.rmdir(temp_dir)

        return jsonify(geojson)

    except Exception as e:
        print(f"Error processing files: {e}")
        return jsonify({'message': 'Error processing files'}), 500

@app.route('/upload_complete_MO_gemapi', methods=['POST'])
def upload_complete_MO_gemapi():
    print("allo", file=sys.stderr)
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 403

    try:
        decoded_token = jwt.decode(token, SECRET_JKEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 403 
    
    nom_mo = request.form.get('NOM-MO')
    alias = request.form.get('ALIAS')
    code_siren = request.form.get('CODE_SIREN')

    # Géométrie du polygone envoyée
    geometry = request.form.get('geometry')

    ajout_MO_ou_PPG.ajout_shp_MO_gemapi_BDD_DORA(nom_mo,alias,code_siren,geometry)
    return jsonify({'message': 'Error processing files'}), 500

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
