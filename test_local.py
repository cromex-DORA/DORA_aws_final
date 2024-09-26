from app.DORApy import check_tableau_DORA

LISTE_CODE_CUSTOM = ["MO_gemapi_10041"]

check_tableau_DORA.verification_tableau_vierge_DORA(LISTE_CODE_CUSTOM,"MO")
print("coucou")
'''bucket_files_common = os.getenv('S3_BUCKET_COMMON_FILES')
bucket_files_CUSTOM = os.getenv('S3_BUCKET_USERS_FILES')

s3_region = os.getenv('S3_UPLOADS_REGION')
s3_access_key = os.getenv('S3_UPLOADS_ACCESS_KEY')
s3_secret_key = os.getenv('S3_UPLOADS_SECRET_KEY')


dict_CUSTOM_maitre = DictCustomMaitre({})
dict_CUSTOM_maitre.set_config_type_projet(type_rendu='carte',type_donnees='action',thematique='MIA',public_cible="tech",liste_grand_bassin=['AG'])

dict_dict_info_REF = DictDfInfoShp({})
dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp()
dict_geom_REF = Class_NDictGdf.NDictGdf({})
dict_geom_REF = Class_NDictGdf.remplissage_dictgdf(dict_geom_REF,dict_CUSTOM_maitre=None,dict_dict_info_REF=dict_dict_info_REF,liste_echelle_REF=["DEP","CE_ME"])

    #Relation géographiques entre CUSTOM et référentiels
dict_decoupREF = Class_NDictGdf.creation_dict_decoupREF(dict_geom_REF,dict_CUSTOM_maitre)
    #Relation géographiques entre référentiels
dict_relation_shp_liste = Class_NDictGdf.extraction_dict_relation_shp_liste_a_partir_decoupREF(dict_CUSTOM_maitre,dict_decoupREF)


CODE_DEP = 33
dict_geom_MO = NDictGdf.recuperation_gdf_REF(dict_geom_REF,"CE_ME")
dict_geom_MO = NGdfREF.selection_par_DEP(dict_geom_MO,"CE_ME",CODE_DEP,dict_relation_shp_liste)
dict_geom_MO = NGdfREF.export_gdf_pour_geojson(dict_geom_MO)'''
