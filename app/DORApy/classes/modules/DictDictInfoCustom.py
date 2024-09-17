# -*- coding: utf-8 -*-
import pandas as pd
import geopandas as gpd
import glob
import os
import geopandas as gpd
import textwrap

def verification_si_polygon_custom_inclus_dans_PPG(dict_dict_info_custom,dict_nom_custom,dict_decoupREF,dict_relation_shp_liste):
    if 'dict_liste_PPG_par_custom' in dict_relation_shp_liste:
        for nom_custom,entite_custom in dict_nom_custom.items():
            CODE_custom = entite_custom.CODE_custom
            if len(dict_relation_shp_liste['dict_liste_PPG_par_custom'][CODE_custom])==1:
                df_decoup = dict_decoupREF['gdf_decoupPPG_custom'].reset_index(drop=True)
                if df_decoup['surface_PPG'].iloc[0]/dict_nom_custom.gdf_custom.loc[dict_nom_custom.gdf_custom['CODE_custom']==CODE_custom]['surface_custom'].iloc[0]>0.95:
                    dict_dict_info_custom[CODE_custom]['PPG_inclus_dans_integral_custom'] = True
                if df_decoup['surface_PPG'].iloc[0]/dict_nom_custom.gdf_custom.loc[dict_nom_custom.gdf_custom['CODE_custom']==CODE_custom]['surface_custom'].iloc[0]<=0.95:
                    dict_dict_info_custom[CODE_custom]['PPG_inclus_dans_integral_custom'] = False
    return dict_dict_info_custom

def actualisation_attributs_contenu_boite_ortho_dict_dict_info_custom(self,dict_dict_boite_maitre,dict_nom_custom):
    for nom_boite_maitre,dict_boite_maitre in dict_dict_boite_maitre.items():
        for nom_bloc,dict_bloc in dict_boite_maitre.items():
            if dict_bloc.sous_type =="nombre_actions":
                df_donnees = dict_bloc.donnees
                for CODE_custom in dict_nom_custom.liste_CODE_custom_tableau_actions:
                    df_donnees_custom = df_donnees.loc[df_donnees["CODE_MO"]==CODE_custom]
                    if len(self[CODE_custom]["liste_echelle_boite_ortho"])==2:
                        self[CODE_custom]["info_texte_simple_boite_ortho"] = "PPG"
                    if len(self[CODE_custom]["liste_echelle_boite_ortho"])==1:
                        self[CODE_custom]["info_texte_simple_boite_ortho"] = "MO"
    return self

def dict_special_custom_a_reduire(self,dict_nom_custom):
    for CODE_custom in dict_nom_custom.liste_CODE_custom:
        self[CODE_custom] = {}
        self[CODE_custom]['custom_a_reduire'] = False
    return self

def definition_custom_a_reduire(self):
    for CODE_custom in self:
        self[CODE_custom]['custom_a_reduire'] = False
    return self

def recuperation_taille_boite_complete_par_custom(self,dict_boite_complete_pour_placement):
    for nom_boite_maitre,dict_boite_maitre in dict_boite_complete_pour_placement.items():
        for CODE_custom,df_custom in dict_boite_maitre.boite_complete.items():
            if self[CODE_custom]['custom_a_reduire'] == True:
                self[CODE_custom]['df_taille_boite_complete'] = pd.DataFrame()
    for nom_boite_maitre,dict_boite_maitre in dict_boite_complete_pour_placement.items():
        for CODE_custom,df_custom in dict_boite_maitre.boite_complete.items():
            self[CODE_custom]['df_taille_boite_complete'] = df_custom[["CODE_REF","echelle_REF","hauteur_boite_complete","largeur_boite_complete"]]
            self[CODE_custom]['df_taille_boite_complete'] = self[CODE_custom]['df_taille_boite_complete'].loc[self[CODE_custom]['df_taille_boite_complete']['echelle_REF']==dict_boite_maitre.echelle_carto]
            self[CODE_custom]['df_taille_boite_complete']["surface_boite"] = self[CODE_custom]['df_taille_boite_complete']["hauteur_boite_complete"]*self[CODE_custom]['df_taille_boite_complete']["largeur_boite_complete"]
    return self


