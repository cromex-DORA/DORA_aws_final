# -*- coding: utf-8 -*-
import pandas as pd
import sys
import geopandas as gpd
import json
from shapely.geometry import shape

pd.set_option("display.max_rows", None, "display.max_columns", None,'display.max_colwidth',None)
from app.DORApy.classes.Class_DictCustomMaitre import DictCustomMaitre
from app.DORApy.classes.Class_dictGdfCompletREF import dictGdfCompletREF,GdfCompletREF
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes import Class_NDictGdf


def conv_shp_en_geojson(files,temp_dir):
    # Use geopandas to read the shapefile
    gdf = gpd.read_file(temp_dir)
    gdf = gdf.to_crs("EPSG:4326")
    
    # Convert the GeoDataFrame to GeoJSON
    geojson = gdf.to_json()
    geojson = json.loads(geojson)
    return geojson

def ajout_shp_MO_gemapi_BDD_DORA(nom_mo,alias,code_siren,geometry):
    type_REF_maj = "MO"
    dict_dict_info_REF = DictDfInfoShp({})
    dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp()

    dict_geom_REF = Class_NDictGdf.NDictGdf({})
    dict_geom_REF = Class_NDictGdf.remplissage_dictgdf(dict_geom_REF,dict_CUSTOM_maitre=None,dict_dict_info_REF=dict_dict_info_REF,liste_echelle_REF=[type_REF_maj,"DEP"])

    geojson_obj = json.loads(geometry)

# Convertir en objet Polygon Shapely
    polygon = shape(geojson_obj)

    data_couche_REF = {'NOM_MO': [nom_mo], 'ALIAS': [alias],"NOM_init":[nom_mo],"geometry_"+type_REF_maj:polygon}

    couche_REF = gpd.GeoDataFrame(data_couche_REF)
    couche_REF = couche_REF.set_geometry("geometry_"+type_REF_maj)
    couche_REF = couche_REF.set_crs('EPSG:4326')
    couche_REF = couche_REF.to_crs('EPSG:2154')
    couche_REF['surface_'+type_REF_maj] = couche_REF.area
    couche_REF = dictGdfCompletREF.ajout_CODE_REF_unique(couche_REF,type_REF_maj,dict_dict_info_REF)
    gdf_DEP =dict_geom_REF['gdf_DEP'].gdf
    inter = gpd.overlay(couche_REF,gdf_DEP, how='intersection',keep_geom_type=False)
    liste_CODE_DEP = inter['CODE_DEP'].to_list()
    str_liste_CODE_DEP = (",").join(liste_CODE_DEP)

    df_info_couche_REF = couche_REF[['NOM_MO',"ALIAS","CODE_MO"]]
    df_info_couche_REF['shp'] = 1
    df_info_couche_REF['CODE_SIREN'] = code_siren
    df_info_couche_REF['TYPE_MO'] = "Syndicat"
    df_info_couche_REF['NOM_init'] = df_info_couche_REF['NOM_MO']
    df_info_couche_REF['nom_usuel'] = df_info_couche_REF['NOM_MO']
    df_info_couche_REF['CODE_DEP'] = str_liste_CODE_DEP
    
    dict_geom_REF['gdf_MO'].df_info['CODE_DEP'] = dict_geom_REF['gdf_MO'].df_info['CODE_DEP'].apply(lambda x:(",").join(x))
    dict_geom_REF['gdf_MO'].df_info = pd.concat([dict_geom_REF['gdf_MO'].df_info,df_info_couche_REF])
    Class_NDictGdf.NDictGdf.actualisation_df_info(dict_geom_REF,type_REF_maj)

    Class_NDictGdf.NDictGdf.back_up_shp(dict_geom_REF,type_REF_maj)
    dict_geom_REF['gdf_MO'].gdf = pd.concat([dict_geom_REF['gdf_MO'].gdf,couche_REF])
    Class_NDictGdf.NDictGdf.actualisation_shp(dict_geom_REF,type_REF_maj)

    print("c'est good !", file=sys.stderr)
    pass



