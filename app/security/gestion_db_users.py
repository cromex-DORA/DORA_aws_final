
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy import URL
import pandas as pd
from DORApy.classes import Class_Folder

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def dossier_principal_user(decoded_token):
    role = decoded_token.get('role')
    if role =="admin":
        user_folder = "adminfolder"
    if role =="user":
        user_folder="MO_gemapi"
    return user_folder

def dossiers_secondaires_user(decoded_token):
    role = decoded_token["role"]
    CODE_DEP = decoded_token["CODE_DEP"]
    if role=="user":
        dossier_user_MO_gemapi = Class_Folder.get_path_dossier_CUSTOM("MO")
        list_rep_MO_gemapi = Class_Folder.lister_rep_et_fichiers(dossier_user_MO_gemapi)
        liste_CODE_MO_a_afficher = [REP for REP in list_rep_MO_gemapi if CODE_DEP in REP.list_CODE_DEP]
        dict_sous_dossiers_user = {k.name:k.NOM_MO for k in liste_CODE_MO_a_afficher}
    if role=="admin":
        dict_sous_dossiers_user = {}
    return dict_sous_dossiers_user


def trouver_NOM_physique_fichier(path_file,dict_sous_dossiers_user):
    dict_NOM_CODE = {v:k for k,v in dict_sous_dossiers_user.items()}
    path_file = path_file.split("/")
    list_tempo = []
    for element in path_file:
        if element in dict_NOM_CODE:
            list_tempo.append(dict_NOM_CODE[element])
        else:
            list_tempo.append(element)
    true_path_file = "/".join(list_tempo)    
    return true_path_file
    
