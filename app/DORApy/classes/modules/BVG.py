# -*- coding: utf-8 -*-
import pandas as pd
import os
import geopandas as gpd
from dotenv import load_dotenv
from app.DORApy.classes.modules import connect_path

################################################################################################################################################################################
#Module d'import des fichiers shapefile ME
################################################################################################################################################################################
def import_shp_BVG(self):
    #couche PPG
    filename = ("shp_files\\BVG\\data\\bv_gestion_sdage2022\\bv_gestion_sdage2022.shp")
    filename = connect_path.get_file_path_racine(filename)
    shp_BVG = gpd.read_file(filename)
    shp_BVG = shp_BVG.rename({'id_bvgesti':'CODE_BVG','nom_bvgest':'nom_BVG'},axis=1)
    #On dégage le premier FR
    shp_BVG = shp_BVG.rename(columns={'geometry':'geometry_BVG'})
    shp_BVG = shp_BVG.set_geometry('geometry_BVG')
    shp_BVG = shp_BVG.to_crs(2154)
    return shp_BVG

