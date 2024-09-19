from flask import Blueprint, jsonify
from flask import Flask, send_from_directory, jsonify, request, Response
import sys
from app.DORApy import creation_carte
from app.DORApy.security import gestion_db_users
from app.DORApy import creation_carte
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes import Class_NDictGdf,Class_NGdfREF
import jwt
import os



api_bp = Blueprint('api', __name__)
SECRET_JKEY = os.getenv('SECRET_JKEY')

dict_dict_info_REF = DictDfInfoShp({})
dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp()    
dict_geom_REF = Class_NDictGdf.NDictGdf({})
dict_geom_REF = Class_NDictGdf.remplissage_dictgdf(dict_geom_REF,dict_custom_maitre=None,dict_dict_info_REF=dict_dict_info_REF,liste_echelle_REF=["MO","DEP"])


@api_bp.route('/api/MO', methods=['GET'])
def get_MO_geojson():
    token = request.headers.get('Authorization')
    print("token", file=sys.stderr)
    print(token, file=sys.stderr)
    if not token:
        return jsonify({'message': 'Token is missing'}), 403

    try:
        decoded_token = jwt.decode(token, SECRET_JKEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 403

    CODE_DEP = decoded_token['CODE_DEP']
    print(CODE_DEP, file=sys.stderr)
    geojson_data_MO_gemapi=creation_carte.creation_carto_syndicats(CODE_DEP)

    dict_sous_dossiers = gestion_db_users.dossiers_secondaires_user(decoded_token)
    dict_folders = {item['id']:item for item in dict_sous_dossiers}

    for num,feature in enumerate(geojson_data_MO_gemapi['features']):
        if feature['id'] in dict_folders:
            geojson_data_MO_gemapi['features'][num]['properties'] = dict_folders[feature['id']] | feature['properties']


    response = geojson_data_MO_gemapi
    return jsonify(response), 200

