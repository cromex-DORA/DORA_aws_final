from app.DORApy.classes.modules.connect_path import s3,s3r
from flask import jsonify, request
import jwt
import bcrypt
import os
import sys
import pandas as pd
import py7zr
import io

SECRET_JKEY = os.getenv('SECRET_JKEY')
environment = os.getenv('ENVIRONMENT')
bucket_common_files = os.getenv('S3_BUCKET_COMMON_FILES')
bucket_users_files = os.getenv('S3_BUCKET_USERS_FILES')
s3_region = os.getenv('S3_UPLOADS_REGION')
s3_access_key = os.getenv('S3_UPLOADS_ACCESS_KEY')
s3_secret_key = os.getenv('S3_UPLOADS_SECRET_KEY')


#dict_dict_info_REF = DictDfInfoShp({})
#dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp(['MO'])

if environment=="developpement":
    chemin_vers_file = "app/files/"
if environment=="docker":
    chemin_vers_file = "files/"

def upload_df_to_s3(df, bucket_common_files, file_key):
    s3_path = f's3://{bucket_common_files}/{file_key}'
    df.to_csv(s3_path, index=False, storage_options={'anon': False})

def hash_password(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def import_dict_users_s3():
    file_name = "BDD_users/db_users.csv"
    csv_obj = s3.get_object(Bucket=bucket_users_files,Key=file_name)
    csv_content = csv_obj['Body'].read().decode('utf-8')
    df = pd.read_csv(io.StringIO(csv_content))
    dict_users = df.set_index('email').to_dict(orient='index')
    return dict_users

def hash_mdp_s3():
    file_name = "BDD_users/db_users.csv"
    csv_obj = s3.get_object(Bucket="dorabuckets3",Key=file_name)
    csv_content = csv_obj['Body'].read().decode('utf-8')
    df = pd.read_csv(io.StringIO(csv_content))
    df["password"] = df["password"].apply(lambda x: hash_password(x))
    upload_df_to_s3(df, bucket_users_files, file_name)

def check_token(token):
    if not token:
        return jsonify({'message': 'Token is missing'}), 403

    try:
        decoded_token = jwt.decode(token, SECRET_JKEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 403   
    return decoded_token



    

