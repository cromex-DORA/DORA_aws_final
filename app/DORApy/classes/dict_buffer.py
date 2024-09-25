# -*- coding: utf-8 -*-
import pandas as pd
import geopandas as gpd
from app.DORApy.classes.modules import config_DORA
import geopandas as gpd
from operator import itemgetter

#from mod.globals import convertir_liste_liste_texte_en_listes_largeur_hauteur
#Les classes correspondent é des boites avec des infos é l'intérieur.
#Ces infos peuvent étre du texte ou des icénes

#Creation des dictionnaires de configuration
dict_config_espace,dict_config_police = config_DORA.creation_dicts_config()

##########################################################################################
#buffer
##########################################################################################
class gdf_buffer:
    def __init__(self):
        self.type_de_gdf = "gdf_buffer"

class dict_buffer(dict):
    @property
    def _constructor(self):
        return dict_buffer

    def creation_ligne_buffer(self,dict_CUSTOM_maitre):
        for CUSTOM in dict_CUSTOM_maitre:
            self[CUSTOM] = gdf_buffer()
            self[CUSTOM].gdf_buffer = dict_CUSTOM_maitre[CUSTOM].gdf.convex_hull.buffer(dict_config_espace['longueur_buffer_custom'][dict_CUSTOM_maitre.taille_carto])
            self[CUSTOM].gdf_buffer = gpd.GeoDataFrame(geometry=gpd.GeoSeries(self[CUSTOM].gdf_buffer))
            self[CUSTOM].gdf_buffer = self[CUSTOM].gdf_buffer.rename({"geometry":"geometry_CUSTOM_buffer"},axis=1)
            self[CUSTOM].gdf_buffer['CODE_CUSTOM'] = [CUSTOM]
            self[CUSTOM].gdf_buffer['geometry_CUSTOM_buffer'] = self[CUSTOM].gdf_buffer['geometry_CUSTOM_buffer'].boundary
            self[CUSTOM].gdf_buffer = self[CUSTOM].gdf_buffer[['CODE_CUSTOM','geometry_CUSTOM_buffer']]
            self[CUSTOM].gdf_buffer = self[CUSTOM].gdf_buffer.set_geometry('geometry_CUSTOM_buffer')
        return self

    ############################################################################################################################
    #creation dict CUSTOM
    ############################################################################################################################
    def ajout_attributs_coord_points_cardinaux_buffer(self):
        for CUSTOM in self:
            list_point =  self[CUSTOM].gdf_buffer['geometry_CUSTOM_buffer'].tolist()
            list_point = list(list_point[0].coords)
            self[CUSTOM].liste_xy_extreme_NESO =  [max(list_point,key=itemgetter(1)),max(list_point),min(list_point,key=itemgetter(1)),min(list_point)]
        return self

