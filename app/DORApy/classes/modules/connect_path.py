from dotenv import load_dotenv
import boto3
import os
import io
from tempfile import NamedTemporaryFile
import pandas as pd
import geopandas as gpd
import fsspec
import tempfile
import shutil
from botocore.exceptions import NoCredentialsError

load_dotenv()

environment = os.getenv('ENVIRONMENT')

################################################
#aws
################################################
bucket_files_common = os.getenv('S3_BUCKET_COMMON_FILES')
bucket_files_CUSTOM = os.getenv('S3_BUCKET_USERS_FILES')

s3_region = os.getenv('S3_UPLOADS_REGION')
s3_access_key = os.getenv('S3_UPLOADS_ACCESS_KEY')
s3_secret_key = os.getenv('S3_UPLOADS_SECRET_KEY')


s3 = boto3.client(
    's3',
    region_name=s3_region,
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key
)

s3r = boto3.resource('s3',
    region_name=s3_region,
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key
)


################################################
#Dossier Docker
################################################
def definir_PATH_DOSSIER_MAITRE_racine():
    if environment =="developpement":
        PATH_DOSSIER_BDD_DORA = "/mnt/d/projet_DORA"
    if environment =="production":  
        PATH_DOSSIER_BDD_DORA = "./projet_DORA"  
    return PATH_DOSSIER_BDD_DORA

def conv_s3_obj_vers_python_obj(type_bucket,file_name):
    file_name = file_name.replace("\\","/")
    if type_bucket == "config":
        nom_bucket = bucket_files_common
    if type_bucket == "CUSTOM":
        nom_bucket = bucket_files_CUSTOM
    csv_obj = s3.get_object(Bucket=nom_bucket,Key=file_name)
    if file_name.split(".")[-1]=="csv":
        csv_content = csv_obj['Body'].read().decode('utf-8')
        obj_python = io.StringIO(csv_content)
    if file_name.split(".")[-1] in ["ods","xlsx","xlsm"]:
        obj_python = csv_obj['Body'].read()
    return obj_python

def get_file_path_racine(file_name,type_bucket=bucket_files_common):
    if environment == 'production':
        file_name = file_name.replace("\\","/")
        # Chemin pour accéder aux fichiers S3
        s3_file_path = f's3://{type_bucket}/{file_name}'
        return s3_file_path
    if environment == 'developpement':
        file_name = file_name.replace("\\","/")
        local_file_path = os.path.join(definir_PATH_DOSSIER_MAITRE_racine(),file_name)
        return local_file_path
    
def upload_file_vers_s3(type_bucket,file,path):
    def upload_workbook(workbook, bucket, key):
        with NamedTemporaryFile() as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)
            s3r.meta.client.upload_file(tmp.name, bucket, key)  

    if type_bucket == "config":
        nom_bucket = bucket_files_common
    if type_bucket == "CUSTOM":
        nom_bucket = bucket_files_CUSTOM
    extension = os.path.splitext(path)[1][1:]
    if isinstance(file, pd.DataFrame):
        csv_buffer = io.StringIO()
        file.to_csv(csv_buffer, index=False)
        # Uploader sur S3
        s3.put_object(Bucket=nom_bucket, Key=path, Body=csv_buffer.getvalue())   
    if extension == "xlsx":
        upload_workbook(file, nom_bucket, path)
    
def download_file_from_s3(type_bucket,file_key):
    if type_bucket == "config":
        nom_bucket = bucket_files_common
    if type_bucket == "CUSTOM":
        nom_bucket = bucket_files_CUSTOM   
    complet_path = os.path.join("MO_gemapi",file_key)
    url = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': nom_bucket,
            'Key': complet_path
        },
        ExpiresIn=100
    )
    return url

def lister_exclu_fichiers_folder_s3(bucket,path):
    list_obj = list(s3r.Bucket(bucket).objects.filter(Prefix=path))
    list_key = [x.key for x in list_obj]
    list_fichiers_sans_folder = [key for key in list_key if not key.endswith("/")]
    list_noms_fichiers = [key.split("/")[-1] for key in list_fichiers_sans_folder]
    return list_noms_fichiers

def lire_gpkg_sur_s3_avec_gpd(type_bucket,path):
    if type_bucket == "config":
        nom_bucket = bucket_files_common
    if type_bucket == "CUSTOM":
        nom_bucket = bucket_files_CUSTOM

    extension = path.split(".")[-1]
    base_path = path.split(".")[0]
    fs = fsspec.filesystem('s3', key=s3_access_key, secret=s3_secret_key)
    if extension=="gpkg":
        with tempfile.NamedTemporaryFile(suffix=".gpkg") as tmpfile:
            # Télécharger et sauvegarder localement
            with fs.open(path, 'rb') as s3file:
                shutil.copyfileobj(s3file, tmpfile)
            
            # Assurez-vous que le fichier est sauvegardé
            tmpfile.flush()

            # Lire avec geopandas
            gdf = gpd.read_file(tmpfile.name)

    if extension=="shp":
        shp_extensions = ['.shp', '.shx', '.dbf', '.prj']  # Ajouter d'autres extensions si nécessaire

        # Créer un répertoire temporaire local
        with tempfile.TemporaryDirectory() as tmpdir:
            # Télécharger tous les fichiers associés du Shapefile
            for ext in shp_extensions:
                s3_file = f"{base_path}{ext}"
                local_file = os.path.join(tmpdir, os.path.basename(s3_file))
                fs.get(s3_file, local_file)

            # Construire le chemin du fichier .shp local téléchargé
            local_shp_path = os.path.join(tmpdir, os.path.basename(f"{base_path}.shp"))

            # Lire le fichier Shapefile localement avec geopandas
            gdf = gpd.read_file(local_shp_path)
    return gdf  

def generer_un_lien_public_sur_s3(bucket_files_common, object_key, expiration=3600):
    try:
        response = s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_files_common,
                                                            'Key': object_key},
                                                    ExpiresIn=expiration)
    except NoCredentialsError:
        print("Credentials not available")
        return None
    return response
        