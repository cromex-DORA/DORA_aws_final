# -*- coding: utf-8 -*-
import pandas as pd
import geopandas as gpd
from dotenv import load_dotenv
from app.DORApy.classes.modules import connect_path


################################################################################################################################################################################
#Module d'import des fichiers shapefile ME
################################################################################################################################################################################
def import_shp_SAGE(self):
    #couche PPG
    filename = ("shp_files\\SAGE\\SAGE superficiels.shp")
    filename = connect_path.get_file_path_racine(filename)
    shp_SAGE = gpd.read_file(filename)
    shp_SAGE = shp_SAGE.rename({'CODE_SAGE':'CODE_SAGE','NOM_SAGE':'NOM_SAGE'},axis=1)
    shp_SAGE = shp_SAGE.rename(columns={'geometry':'geometry_SAGE'})
    shp_SAGE = shp_SAGE.set_geometry('geometry_SAGE')
    shp_SAGE = shp_SAGE.to_crs(2154)
    return shp_SAGE



