
import bcrypt
from app.DORApy.classes import Class_Folder
import os
import sys
from app.DORApy.classes import Class_Folder
bucket_users_files = os.getenv('S3_BUCKET_USERS_FILES')

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
        folder_prefix = 'MO_gemapi/'
        folders = Class_Folder.lister_rep_et_fichiers(bucket_users_files, folder_prefix)

    if role=="admin":
        dict_sous_dossiers_user = {}
    return folders


    
