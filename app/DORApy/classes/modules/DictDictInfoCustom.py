# -*- coding: utf-8 -*-
import pandas as pd
import geopandas as gpd
import glob
import os
import geopandas as gpd
import textwrap

def verification_si_polygon_CUSTOM_inclus_dans_PPG(dict_dict_info_CUSTOM,dict_nom_CUSTOM,dict_decoupREF,dict_relation_shp_liste):
    if 'dict_liste_PPG_par_CUSTOM' in dict_relation_shp_liste:
        for nom_CUSTOM,entite_CUSTOM in dict_nom_CUSTOM.items():
            CODE_CUSTOM = entite_CUSTOM.CODE_CUSTOM
            if len(dict_relation_shp_liste['dict_liste_PPG_par_CUSTOM'][CODE_CUSTOM])==1:
                df_decoup = dict_decoupREF['gdf_decoupPPG_CUSTOM'].reset_index(drop=True)
                if df_decoup['surface_PPG'].iloc[0]/dict_nom_CUSTOM.gdf_CUSTOM.loc[dict_nom_CUSTOM.gdf_CUSTOM['CODE_CUSTOM']==CODE_CUSTOM]['surface_CUSTOM'].iloc[0]>0.95:
                    dict_dict_info_CUSTOM[CODE_CUSTOM]['PPG_inclus_dans_integral_CUSTOM'] = True
                if df_decoup['surface_PPG'].iloc[0]/dict_nom_CUSTOM.gdf_CUSTOM.loc[dict_nom_CUSTOM.gdf_CUSTOM['CODE_CUSTOM']==CODE_CUSTOM]['surface_CUSTOM'].iloc[0]<=0.95:
                    dict_dict_info_CUSTOM[CODE_CUSTOM]['PPG_inclus_dans_integral_CUSTOM'] = False
    return dict_dict_info_CUSTOM

def actualisation_attributs_contenu_boite_ortho_dict_dict_info_CUSTOM(self,dict_dict_boite_maitre,dict_nom_CUSTOM):
    for nom_boite_maitre,dict_boite_maitre in dict_dict_boite_maitre.items():
        for nom_bloc,dict_bloc in dict_boite_maitre.items():
            if dict_bloc.sous_type =="nombre_actions":
                df_donnees = dict_bloc.donnees
                for CODE_CUSTOM in dict_nom_CUSTOM.liste_CODE_CUSTOM_tableau_actions:
                    df_donnees_CUSTOM = df_donnees.loc[df_donnees["CODE_MO"]==CODE_CUSTOM]
                    if len(self[CODE_CUSTOM]["liste_echelle_boite_ortho"])==2:
                        self[CODE_CUSTOM]["info_texte_simple_boite_ortho"] = "PPG"
                    if len(self[CODE_CUSTOM]["liste_echelle_boite_ortho"])==1:
                        self[CODE_CUSTOM]["info_texte_simple_boite_ortho"] = "MO"
    return self

def dict_special_CUSTOM_a_reduire(self,dict_nom_CUSTOM):
    for CODE_CUSTOM in dict_nom_CUSTOM.liste_CODE_CUSTOM:
        self[CODE_CUSTOM] = {}
        self[CODE_CUSTOM]['CUSTOM_a_reduire'] = False
    return self

def definition_CUSTOM_a_reduire(self):
    for CODE_CUSTOM in self:
        self[CODE_CUSTOM]['CUSTOM_a_reduire'] = False
    return self

def recuperation_taille_boite_complete_par_CUSTOM(self,dict_boite_complete_pour_placement):
    for nom_boite_maitre,dict_boite_maitre in dict_boite_complete_pour_placement.items():
        for CODE_CUSTOM,df_CUSTOM in dict_boite_maitre.boite_complete.items():
            if self[CODE_CUSTOM]['CUSTOM_a_reduire'] == True:
                self[CODE_CUSTOM]['df_taille_boite_complete'] = pd.DataFrame()
    for nom_boite_maitre,dict_boite_maitre in dict_boite_complete_pour_placement.items():
        for CODE_CUSTOM,df_CUSTOM in dict_boite_maitre.boite_complete.items():
            self[CODE_CUSTOM]['df_taille_boite_complete'] = df_CUSTOM[["CODE_REF","echelle_REF","hauteur_boite_complete","largeur_boite_complete"]]
            self[CODE_CUSTOM]['df_taille_boite_complete'] = self[CODE_CUSTOM]['df_taille_boite_complete'].loc[self[CODE_CUSTOM]['df_taille_boite_complete']['echelle_REF']==dict_boite_maitre.echelle_carto]
            self[CODE_CUSTOM]['df_taille_boite_complete']["surface_boite"] = self[CODE_CUSTOM]['df_taille_boite_complete']["hauteur_boite_complete"]*self[CODE_CUSTOM]['df_taille_boite_complete']["largeur_boite_complete"]
    return self


