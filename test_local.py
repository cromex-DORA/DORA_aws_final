
import pandas as pd
from app.DORApy.classes import Class_NDictGdf,Class_DictDfInfoShp
from app.DORApy.classes.Class_DictCustomMaitre import DictCustomMaitre
from app.DORApy.classes.Class_DictCustomMaitre import DictCustomMaitre
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes import Class_NDictGdf,Class_NGdfREF
from app.DORApy.classes.Class_NDictGdf import NDictGdf
from app.DORApy.classes.Class_NGdfREF import NGdfREF
from app.DORApy import creation_carte
import os
import geopandas as gpd
from tempfile import NamedTemporaryFile

bucket_files_common = os.getenv('S3_BUCKET_COMMON_FILES')
bucket_files_custom = os.getenv('S3_BUCKET_USERS_FILES')

s3_region = os.getenv('S3_UPLOADS_REGION')
s3_access_key = os.getenv('S3_UPLOADS_ACCESS_KEY')
s3_secret_key = os.getenv('S3_UPLOADS_SECRET_KEY')


dict_custom_maitre = DictCustomMaitre({})
dict_custom_maitre.set_config_type_projet(type_rendu='carte',type_donnees='action',thematique='MIA',public_cible="tech",liste_grand_bassin=['AG'])

dict_dict_info_REF = DictDfInfoShp({})
dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp()
dict_geom_REF = Class_NDictGdf.NDictGdf({})
dict_geom_REF = Class_NDictGdf.remplissage_dictgdf(dict_geom_REF,dict_custom_maitre=None,dict_dict_info_REF=dict_dict_info_REF,liste_echelle_REF=["MO","DEP","PPG","ME"])

    #Relation géographiques entre custom et référentiels
dict_decoupREF = Class_NDictGdf.creation_dict_decoupREF(dict_geom_REF,dict_custom_maitre)
    #Relation géographiques entre référentiels
dict_relation_shp_liste = Class_NDictGdf.extraction_dict_relation_shp_liste_a_partir_decoupREF(dict_custom_maitre,dict_decoupREF)


CODE_DEP = 33
dict_geom_MO = NDictGdf.recuperation_gdf_REF(dict_geom_REF,"ME")
dict_geom_MO = NGdfREF.selection_par_DEP(dict_geom_MO,"ME",CODE_DEP,dict_relation_shp_liste)


#Class_NDictGdf.NDictGdf.actualisation_shp(dict_geom_REF,"MO")
'''gdf_dep =dict_geom_REF['gdf_DEP'].gdf
gdf_mo = dict_geom_REF['gdf_MO'].gdf
boum = gpd.overlay(gdf_mo,gdf_dep, how='intersection',keep_geom_type=False)
boum = boum.groupby("CODE_MO").agg({'CODE_DEP':lambda x:list(x)})'''
print("coucou")

#gdf_ME = gpd.read_file("D:/projet_DORA/shp_files/ME/BV Me sup AG 2021.shp")
#dict_gdf = Class_NDictGdf.chercher_gdf()
#user_folder = actualisation_dossier_MO()
