
import pandas as pd
from app.DORApy.classes import Class_NDictGdf,Class_DictDfInfoShp
from app.DORApy.classes.Class_DictCustomMaitre import DictCustomMaitre
from flask import Flask, send_from_directory, jsonify, request
from app.DORApy import gestion_admin,creation_tableau_vierge_DORA
from app.DORApy.decorators.token_admin import check_token_admin
from app.DORApy import creation_carte
import os
import geopandas as gpd
from tempfile import NamedTemporaryFile

bucket_files_common = os.getenv('S3_BUCKET_COMMON_FILES')
bucket_files_custom = os.getenv('S3_BUCKET_USERS_FILES')

s3_region = os.getenv('S3_UPLOADS_REGION')
s3_access_key = os.getenv('S3_UPLOADS_ACCESS_KEY')
s3_secret_key = os.getenv('S3_UPLOADS_SECRET_KEY')


dict_dict_info_REF = Class_DictDfInfoShp.DictDfInfoShp({})
dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp()
dict_geom_REF = Class_NDictGdf.NDictGdf({})
dict_geom_REF = Class_NDictGdf.remplissage_dictgdf(dict_geom_REF,dict_custom_maitre=None,dict_dict_info_REF=dict_dict_info_REF)

Class_NDictGdf.generation_geojson_sur_s3(dict_geom_REF)

#Class_NDictGdf.NDictGdf.actualisation_shp(dict_geom_REF,"MO")
'''gdf_dep =dict_geom_REF['gdf_DEP'].gdf
gdf_mo = dict_geom_REF['gdf_MO'].gdf
boum = gpd.overlay(gdf_mo,gdf_dep, how='intersection',keep_geom_type=False)
boum = boum.groupby("CODE_MO").agg({'CODE_DEP':lambda x:list(x)})'''
print("coucou")

#gdf_ME = gpd.read_file("D:/projet_DORA/shp_files/ME/BV Me sup AG 2021.shp")
#dict_gdf = Class_NDictGdf.chercher_gdf()
#user_folder = actualisation_dossier_MO()
