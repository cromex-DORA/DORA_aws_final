from flask import Flask, send_from_directory, jsonify, request, Response, Blueprint
import os
from flask_cors import CORS
from app.DORApy import check_tableau_DORA, creation_carte,manipulation_MO
from app.DORApy import gestion_admin,creation_tableau_vierge_DORA,creation_carte,check_tableau_DORA
from app.DORApy.classes.modules import connect_path
from werkzeug.utils import secure_filename

from api import api_bp
import jwt
import datetime
import sys
import tempfile

MilieuxAqua_bp = Blueprint('MilieuxAqua', __name__)
SECRET_JKEY = os.getenv('SECRET_JKEY')

@MilieuxAqua_bp.route('/vierge_DORA', methods=['POST'])
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

    df_vierge_MO = creation_tableau_vierge_DORA.create_tableau_vierge_DORA([id_folder])

    path = os.path.join("MO_gemapi",id_folder,"tableau_vierge_" + name + ".xlsx")

    connect_path.upload_file_vers_s3("CUSTOM",df_vierge_MO,path)

    return jsonify({'message': 'File created successfully'}), 201

@MilieuxAqua_bp.route('/upload_MO_gemapi', methods=['POST'])
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
        geojson = manipulation_MO.conv_shp_en_geojson(files,temp_dir)
        # Read the shapefiles using geopandas
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
        os.rmdir(temp_dir)

        return jsonify(geojson)

    except Exception as e:
        print(f"Error processing files: {e}")
        return jsonify({'message': 'Error processing files'}), 500

@MilieuxAqua_bp.route('/upload_complete_MO_gemapi', methods=['POST'])
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

    manipulation_MO.ajout_shp_MO_gemapi_BDD_DORA(nom_mo,alias,code_siren,geometry)
    return jsonify({"message": "c'est tout bon !"}), 200

@MilieuxAqua_bp.route('/verif_tableau_DORA', methods=['POST'])
def verif_tableau_DORA():
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


    file = request.form.get('file')
    NOM_MO = request.form.get('NOM_MO')
    CODE_MO = request.form.get('CODE_MO')
    file_name = file.filename
    connect_path.upload_file_vers_s3("CUSTOM",file,os.path.join("MO_gemapi",CODE_MO,file_name))
    #check_tableau_DORA.verification_tableau_vierge_DORA([NOM_MO])
    return jsonify({'message': 'Error processing files'}), 500

@MilieuxAqua_bp.route('/suppression_MO_GEMAPI', methods=['POST'])
def suppression_MO_GEMAPI():
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
    
    CODE_MO = request.form.get('id')

    manipulation_MO.suppression_shp_MO_gemapi_BDD_DORA(CODE_MO)
    return jsonify({"message": "c'est tout bon !"}), 200