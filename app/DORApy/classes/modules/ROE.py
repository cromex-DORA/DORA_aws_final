# -*- coding: utf-8 -*-
import pandas as pd
import geopandas as gpd
from dotenv import load_dotenv
from app.DORApy.classes.modules import connect_path

################################################################################################################################################################################
#Module d'import des fichiers shapefile ME
################################################################################################################################################################################
def import_shp_ROE():
    #couche PPG
    filename = ("shp_files\\ROE\\ROE_AG_2023.gpkg")
    filename = connect_path.get_file_path_racine(filename)
    shp_ROE = gpd.read_file(filename, engine='pyogrio', use_arrow=True)   
    #On dégage le premier FR
    dict_renommage = {'geometry':'geometry_ROE',"CdObstEcou":"CODE_ROE","NomPrincip":"NOM_ROE","CdEuMasseD":"CODE_ME_maitre"}
    shp_ROE = shp_ROE.rename(columns=dict_renommage)
    shp_ROE = shp_ROE[list(dict_renommage.values())]
    shp_ROE = shp_ROE.set_geometry('geometry_ROE')
    shp_ROE = shp_ROE.to_crs(2154)
    return shp_ROE

