# -*- coding: utf-8 -*-
import pandas as pd
import glob
import os
import geopandas as gpd
from dotenv import load_dotenv
from app.DORApy.classes.modules import connect_path

################################################################################################################################################################################
#Module d'import des fichiers shapefile ME
################################################################################################################################################################################
def import_shp_dep(self):
    #couche PPG
    filename = ("shp_files\\dep\\departement NAQ + AG.shp")
    filename = connect_path.get_file_path_racine(filename)
    shp_dep = gpd.read_file(filename)
    shp_dep = shp_dep.rename({'CODE_DEPT':'CODE_DEP','NOM_DEPT':'NOM_DEP'},axis=1)
    shp_dep['CODE_DEP'] = shp_dep['CODE_DEP'].astype(str)
    shp_dep['NOM_DEP'] = shp_dep['NOM_DEP'].astype(str)
    shp_dep = shp_dep.rename(columns={'geometry':'geometry_DEP'})
    shp_dep = shp_dep.set_geometry('geometry_DEP')
    shp_dep = shp_dep.to_crs('epsg:2154')
    return shp_dep



