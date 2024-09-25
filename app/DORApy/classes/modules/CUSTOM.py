# -*- coding: utf-8 -*-
import pandas as pd
import geopandas as gpd
import glob
import os
import geopandas as gpd
import textwrap

def attribution_NOM_MO(liste_nom_synd,liste_couche_synd):    
    #Si on a recup une couche avec plusieurs polygon, on cherche une colonne pour nommer de maniére unique chaque CUSTOM
    for numero_couche,couche in enumerate(liste_couche_synd):
        if len(couche)==1:
            if 'NOM_CUSTOM' not in list(couche):
                couche['NOM_CUSTOM'] = [liste_nom_synd[numero_couche]]
        if len(couche)>1:
            liste_nom_colonne_potentiel_pour_nommage_unique = [x for x in list(couche) if x.startswith('nom')] + [x for x in list(couche) if x.startswith('NOM')] + [x for x in list(couche) if x.startswith('Nom')]
            if len(liste_nom_colonne_potentiel_pour_nommage_unique)==0:
                print("Pas de colonne avec un nommage unique potentiel !")
                exit()
            for colonne in liste_nom_colonne_potentiel_pour_nommage_unique:
                list_nom_unique_potentiel =  couche[colonne].to_list()
                liste_doublon = []
                for x in list_nom_unique_potentiel:
                    if x in liste_doublon:
                        liste_nom_colonne_potentiel_pour_nommage_unique.remove(colonne)
                        break
                    liste_doublon.append(x)
            couche['NOM_CUSTOM'] = couche[liste_nom_colonne_potentiel_pour_nommage_unique[-1]].to_list()
    return liste_nom_synd,liste_couche_synd


def filtrage_par_CUSTOM_si_projet_action(self,gdf_gros_CUSTOM):
    if self.type_donnees == 'action':
        gdf_gros_CUSTOM = gdf_gros_CUSTOM.loc[gdf_gros_CUSTOM['NOM_MO'].isin(self.liste_nom_CUSTOM_tableau_actions)]
    return gdf_gros_CUSTOM

#Actualisation des bb des CUSTOM
def extraction_extreme_boite(projet,dict_boite_complete_pour_placement,dict_dict_info_CUSTOM):
    dict_liste_df_par_CUSTOM = {}
    for CODE_CUSTOM in dict_dict_info_CUSTOM:
        dict_liste_df_par_CUSTOM[CODE_CUSTOM] = []
    for nom_boite_maitre,dict_boite_maitre in dict_boite_complete_pour_placement.items():
        for CODE_CUSTOM,df_CUSTOM in dict_boite_maitre.boite_complete.items():
            if len(df_CUSTOM)>0:
                if dict_boite_maitre.orientation=='normal' or (dict_boite_maitre.orientation=='orthogonal' and dict_dict_info_CUSTOM[CODE_CUSTOM]['cartouche_boite_ortho_separe']==False):
                    dict_liste_df_par_CUSTOM[CODE_CUSTOM].append(df_CUSTOM[['gauche_boite_complete','droite_boite_complete','haut_boite_complete','bas_boite_complete']])


    for CODE_CUSTOM in projet.liste_CODE_CUSTOM:
        dict_liste_df_par_CUSTOM[CODE_CUSTOM] = pd.concat(dict_liste_df_par_CUSTOM[CODE_CUSTOM])
        dict_liste_df_par_CUSTOM[CODE_CUSTOM] = dict_liste_df_par_CUSTOM[CODE_CUSTOM].agg({'gauche_boite_complete' : 'min','droite_boite_complete' : 'max','bas_boite_complete' : 'min','haut_boite_complete' : 'max'})
        dict_liste_df_par_CUSTOM[CODE_CUSTOM] = dict_liste_df_par_CUSTOM[CODE_CUSTOM].to_frame()
        dict_liste_df_par_CUSTOM[CODE_CUSTOM] = dict_liste_df_par_CUSTOM[CODE_CUSTOM].transpose()
        dict_liste_df_par_CUSTOM[CODE_CUSTOM] = dict_liste_df_par_CUSTOM[CODE_CUSTOM].rename(columns={'gauche_boite_complete' : 'min_x_CUSTOM','droite_boite_complete' : 'max_x_CUSTOM','bas_boite_complete' : 'min_y_CUSTOM','haut_boite_complete' : 'max_y_CUSTOM'})
        dict_liste_df_par_CUSTOM[CODE_CUSTOM] = dict_liste_df_par_CUSTOM[CODE_CUSTOM].iloc[0].values.flatten().tolist()

    df_info_CUSTOM_tempo = pd.DataFrame.from_dict(dict_liste_df_par_CUSTOM, orient='index')
    df_info_CUSTOM_tempo.columns  = ['min_x_CUSTOM','max_x_CUSTOM','min_y_CUSTOM','max_y_CUSTOM']
    df_info_CUSTOM_tempo = df_info_CUSTOM_tempo[['min_x_CUSTOM','max_x_CUSTOM','min_y_CUSTOM','max_y_CUSTOM']]
    return df_info_CUSTOM_tempo

def selection_valeurs_min_ou_max(df_info_CUSTOM,df_info_CUSTOM_tempo,projet):
    df_info_CUSTOM_uniquement_valeur_cote = pd.concat([df_info_CUSTOM.set_index('CODE_CUSTOM'), df_info_CUSTOM_tempo])
    df_info_CUSTOM_uniquement_valeur_cote = df_info_CUSTOM_uniquement_valeur_cote.groupby(df_info_CUSTOM_uniquement_valeur_cote.index).agg({'min_x_CUSTOM':'min','max_x_CUSTOM':'max','min_y_CUSTOM':'min','max_y_CUSTOM':'max'})
    df_info_CUSTOM = df_info_CUSTOM.drop(columns=['min_x_CUSTOM','max_x_CUSTOM','min_y_CUSTOM','max_y_CUSTOM'])
    df_info_CUSTOM = pd.merge(df_info_CUSTOM,df_info_CUSTOM_uniquement_valeur_cote, left_on='CODE_CUSTOM', right_index=True)
    #PB : Pourquoi sur les cartes etats/pression, le nom de l'index reste NOM_MO, mais il est supprimé sur les cartes actions MIA
    df_info_CUSTOM.index.name = "NOM_MO"
    return df_info_CUSTOM

def ajout_marge_valeur_max(df_info_CUSTOM):
    marge= 0.03
    df_info_CUSTOM['min_x_CUSTOM'] = df_info_CUSTOM['min_x_CUSTOM'] - (df_info_CUSTOM['X_centre_CUSTOM']-df_info_CUSTOM['min_x_CUSTOM'])*marge
    df_info_CUSTOM['max_x_CUSTOM'] = df_info_CUSTOM['max_x_CUSTOM'] + (df_info_CUSTOM['max_x_CUSTOM']-df_info_CUSTOM['X_centre_CUSTOM'])*marge
    df_info_CUSTOM['min_y_CUSTOM'] = df_info_CUSTOM['min_y_CUSTOM'] - (df_info_CUSTOM['Y_centre_CUSTOM']-df_info_CUSTOM['min_y_CUSTOM'])*marge
    df_info_CUSTOM['max_y_CUSTOM'] = df_info_CUSTOM['max_y_CUSTOM'] + (df_info_CUSTOM['max_y_CUSTOM']-df_info_CUSTOM['Y_centre_CUSTOM'])*marge
    return df_info_CUSTOM

def ajout_info_boite_integral_si_boite_orthogonal_cartouche(df_info_CUSTOM,dict_dict_info_CUSTOM,dict_boite_complete_pour_placement):
    df_info_CUSTOM['cartouche_boite_ortho_separe']==False
    for CUSTOM in dict_dict_info_CUSTOM:
        for nom_boite_maitre,dict_boite_maitre in dict_boite_complete_pour_placement.items():
            for CODE_CUSTOM,df_CUSTOM in dict_boite_maitre.boite_complete.items():
                if dict_dict_info_CUSTOM[CODE_CUSTOM]['cartouche_boite_ortho_separe']==False:
                    if dict_boite_maitre.orientation =="orthogonal":
                        df_info_CUSTOM.loc[(df_info_CUSTOM.index == CUSTOM),"cartouche_boite_ortho_separe"]=True
    return df_info_CUSTOM


