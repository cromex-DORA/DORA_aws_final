# -*- coding: utf-8 -*-
import pandas as pd
import glob
import os
import geopandas as gpd
from dotenv import load_dotenv
from app.DORApy.classes.modules import connect_path

################################################################################################################################################################################
#Module d'import des fichiers shapefile PPG
################################################################################################################################################################################
def import_shp_PPG(self):
    #couche PPG
    filename = ("shp_files\\ppg\\PPG_NA.shp")
    filename = connect_path.get_file_path_racine(filename)
    perimetre_PPG = gpd.read_file(filename)    
    perimetre_PPG = perimetre_PPG.rename(columns={'geometry':'geometry_PPG'})
    perimetre_PPG = perimetre_PPG.set_geometry('geometry_PPG')
    perimetre_PPG = perimetre_PPG.to_crs('epsg:2154')
    return perimetre_PPG


