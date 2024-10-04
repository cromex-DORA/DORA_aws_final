from flask import Blueprint, jsonify
from flask import Flask, send_from_directory, jsonify, request, Response
import sys
from app.DORApy import creation_carte
from app.DORApy.security import gestion_db_users
from app.DORApy import creation_carte
from app.DORApy.classes.Class_DictCustomMaitre import DictCustomMaitre
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes import Class_NDictGdf,Class_NGdfREF
from app.DORApy.classes.Class_NDictGdf import NDictGdf
from app.DORApy.classes.Class_NGdfREF import NGdfREF
from app.DORApy.classes.Class_DictIconeDORA import DictIcone
import jwt
import os



api_bp = Blueprint('api', __name__)
SECRET_JKEY = os.getenv('SECRET_JKEY')


dict_CUSTOM_maitre = None
dict_dict_info_REF = None
dict_geom_REF = None
dict_decoupREF = None
dict_relation_shp_liste = None

def initialize_data():
    global dict_CUSTOM_maitre, dict_dict_info_REF, dict_geom_REF, dict_decoupREF, dict_relation_shp_liste
    
    if dict_CUSTOM_maitre is None:
        # Initialise dict_CUSTOM_maitre
        dict_CUSTOM_maitre = DictCustomMaitre({})
        dict_CUSTOM_maitre.set_config_type_projet(type_rendu='carte', type_donnees='action', thematique='MIA', public_cible="tech", liste_grand_bassin=['AG'])

        # Initialise dict_dict_info_REF
        dict_dict_info_REF = DictDfInfoShp({})
        dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp()

        # Initialise dict_geom_REF
        dict_geom_REF = Class_NDictGdf.NDictGdf({})
        dict_geom_REF = Class_NDictGdf.remplissage_dictgdf(dict_geom_REF, dict_CUSTOM_maitre=None, dict_dict_info_REF=dict_dict_info_REF, liste_echelle_REF=["MO", "DEP", "PPG", "ME", "CE_ME"])

        # Relation géographiques entre CUSTOM et référentiels
        dict_decoupREF = Class_NDictGdf.creation_dict_decoupREF(dict_geom_REF, dict_CUSTOM_maitre)

        # Relation géographiques entre référentiels
        dict_relation_shp_liste = Class_NDictGdf.extraction_dict_relation_shp_liste_a_partir_decoupREF(dict_CUSTOM_maitre, dict_decoupREF)
        print("Données initialisées", file=sys.stderr)
    else:
        print("Données déjà initialisées", file=sys.stderr)

if  os.getenv('ENVIRONMENT')!="test":
    initialize_data()

@api_bp.route('/api/MO', methods=['GET'])
def get_MO_geojson():
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
    dict_geom_MO = NDictGdf.recuperation_gdf_REF(dict_geom_REF,"MO")
    dict_geom_MO = NGdfREF.selection_par_DEP(dict_geom_MO,"MO",CODE_DEP,dict_relation_shp_liste)
    dict_geom_MO = NGdfREF.ajout_TYPE_MO(dict_geom_MO)
    dict_geom_MO = NGdfREF.ajout_LISTE_ME(dict_geom_MO,dict_relation_shp_liste)
    dict_geom_MO = NGdfREF.ajout_dict_coordonnes_ME(dict_geom_MO,dict_decoupREF)
    geojson_data_MO_gemapi=NGdfREF.export_gdf_pour_geojson(dict_geom_MO)

    dict_folders = {item['id']:item for item in dict_sous_dossiers}

    for num,feature in enumerate(geojson_data_MO_gemapi['features']):
        if feature['id'] in dict_folders:
            geojson_data_MO_gemapi['features'][num]['properties'] = dict_folders[feature['id']] | feature['properties']


    response = geojson_data_MO_gemapi
    return jsonify(response), 200


@api_bp.route('/api/PPG', methods=['GET'])
def get_PPG_geojson():
    type_REF = "PPG"
    token = request.headers.get('Authorization')
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
    dict_geom_TYPE_REF = NDictGdf.recuperation_gdf_REF(dict_geom_REF,type_REF)
    dict_geom_TYPE_REF = NGdfREF.selection_par_DEP(dict_geom_TYPE_REF,type_REF,CODE_DEP,dict_relation_shp_liste)
    geojson_data_PPG_gemapi=NGdfREF.export_gdf_pour_geojson(dict_geom_TYPE_REF)

    response = geojson_data_PPG_gemapi
    return jsonify(response), 200

@api_bp.route('/api/ME', methods=['GET'])
def get_ME_geojson():
    type_REF = "ME"
    token = request.headers.get('Authorization')
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
    dict_geom_TYPE_REF = NDictGdf.recuperation_gdf_REF(dict_geom_REF,type_REF)
    dict_geom_TYPE_REF = NGdfREF.selection_par_DEP(dict_geom_TYPE_REF,type_REF,CODE_DEP,dict_relation_shp_liste)
    dict_geom_TYPE_REF = NGdfREF.ajout_nom_ME_simplifie(dict_geom_TYPE_REF)
    geojson_data_ME_gemapi=NGdfREF.export_gdf_pour_geojson(dict_geom_TYPE_REF)

    response = geojson_data_ME_gemapi
    return jsonify(response), 200

@api_bp.route('/api/CE_ME', methods=['GET'])
def get_CE_ME_geojson():
    type_REF = "CE_ME"
    token = request.headers.get('Authorization')
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
    dict_geom_TYPE_REF = NDictGdf.recuperation_gdf_REF(dict_geom_REF,type_REF)
    dict_geom_TYPE_REF = NGdfREF.selection_par_DEP(dict_geom_TYPE_REF,type_REF,CODE_DEP,dict_relation_shp_liste)
    geojson_data_ME_gemapi=NGdfREF.export_gdf_pour_geojson(dict_geom_TYPE_REF)

    response = geojson_data_ME_gemapi
    return jsonify(response), 200

@api_bp.route('/api/icons_DORA', methods=['GET'])
def get_icons():
    dict_icone = DictIcone()
    dict_icone = dict_icone.remplissage_dict_icone("MIA","PRESS")
    dict_icone_pour_json = {nom_icone:icone_dict.url_publique for nom_icone,icone_dict in dict_icone.items()}
    return jsonify(dict_icone_pour_json)