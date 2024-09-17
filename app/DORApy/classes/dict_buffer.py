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
class dict_buffer(dict):
    @property
    def _constructor(self):
        return dict_buffer

    def creation_ligne_buffer(self,dict_custom_maitre):
        for custom in self:
            self[custom]['geometry_custom_buffer'] = self[custom]['geometry_custom'].convex_hull.buffer(dict_config_espace['longueur_buffer_custom'][dict_custom_maitre.taille_carto])
            self[custom]['geometry_custom_buffer'] = self[custom]['geometry_custom_buffer'].boundary
            self[custom] = self[custom][['NOM_custom','geometry_custom_buffer']]
            self[custom] = self[custom].set_geometry('geometry_custom_buffer')
        return self

    ############################################################################################################################
    #creation dict custom
    ############################################################################################################################
    def creation_dict_df_buffer_custom(self,dict_dict_info_custom,dict_custom_maitre):
        for CODE_custom in dict_dict_info_custom:
            self[CODE_custom]=dict_custom_maitre.gdf_custom.gdf[dict_custom_maitre.gdf_custom.gdf['CODE_custom']==CODE_custom]
            self[CODE_custom] = self[CODE_custom].reset_index(drop=True)
        return self

    def ajout_attributs_coord_points_cardinaux_buffer(self):
        for custom in self:
            list_point =  self[custom]['geometry_custom_buffer'].tolist()
            list_point = list(list_point[0].coords)
            self[custom].liste_xy_extreme_NESO =  [max(list_point,key=itemgetter(1)),max(list_point),min(list_point,key=itemgetter(1)),min(list_point)]
        return self

