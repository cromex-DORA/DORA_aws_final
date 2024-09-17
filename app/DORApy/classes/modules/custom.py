# -*- coding: utf-8 -*-
import pandas as pd
import geopandas as gpd
import glob
import os
import geopandas as gpd
import textwrap

def attribution_NOM_MO(liste_nom_synd,liste_couche_synd):    
    #Si on a recup une couche avec plusieurs polygon, on cherche une colonne pour nommer de maniére unique chaque custom
    for numero_couche,couche in enumerate(liste_couche_synd):
        if len(couche)==1:
            if 'NOM_custom' not in list(couche):
                couche['NOM_custom'] = [liste_nom_synd[numero_couche]]
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
            couche['NOM_custom'] = couche[liste_nom_colonne_potentiel_pour_nommage_unique[-1]].to_list()
    return liste_nom_synd,liste_couche_synd


def filtrage_par_custom_si_projet_action(self,gdf_gros_custom):
    if self.type_donnees == 'action':
        gdf_gros_custom = gdf_gros_custom.loc[gdf_gros_custom['NOM_MO'].isin(self.liste_nom_custom_tableau_actions)]
    return gdf_gros_custom

#Actualisation des bb des custom
def extraction_extreme_boite(projet,dict_boite_complete_pour_placement,dict_dict_info_custom):
    dict_liste_df_par_custom = {}
    for CODE_custom in dict_dict_info_custom:
        dict_liste_df_par_custom[CODE_custom] = []
    for nom_boite_maitre,dict_boite_maitre in dict_boite_complete_pour_placement.items():
        for CODE_custom,df_custom in dict_boite_maitre.boite_complete.items():
            if len(df_custom)>0:
                if dict_boite_maitre.orientation=='normal' or (dict_boite_maitre.orientation=='orthogonal' and dict_dict_info_custom[CODE_custom]['cartouche_boite_ortho_separe']==False):
                    dict_liste_df_par_custom[CODE_custom].append(df_custom[['gauche_boite_complete','droite_boite_complete','haut_boite_complete','bas_boite_complete']])


    for CODE_custom in projet.liste_CODE_custom:
        dict_liste_df_par_custom[CODE_custom] = pd.concat(dict_liste_df_par_custom[CODE_custom])
        dict_liste_df_par_custom[CODE_custom] = dict_liste_df_par_custom[CODE_custom].agg({'gauche_boite_complete' : 'min','droite_boite_complete' : 'max','bas_boite_complete' : 'min','haut_boite_complete' : 'max'})
        dict_liste_df_par_custom[CODE_custom] = dict_liste_df_par_custom[CODE_custom].to_frame()
        dict_liste_df_par_custom[CODE_custom] = dict_liste_df_par_custom[CODE_custom].transpose()
        dict_liste_df_par_custom[CODE_custom] = dict_liste_df_par_custom[CODE_custom].rename(columns={'gauche_boite_complete' : 'min_x_custom','droite_boite_complete' : 'max_x_custom','bas_boite_complete' : 'min_y_custom','haut_boite_complete' : 'max_y_custom'})
        dict_liste_df_par_custom[CODE_custom] = dict_liste_df_par_custom[CODE_custom].iloc[0].values.flatten().tolist()

    df_info_custom_tempo = pd.DataFrame.from_dict(dict_liste_df_par_custom, orient='index')
    df_info_custom_tempo.columns  = ['min_x_custom','max_x_custom','min_y_custom','max_y_custom']
    df_info_custom_tempo = df_info_custom_tempo[['min_x_custom','max_x_custom','min_y_custom','max_y_custom']]
    return df_info_custom_tempo

def selection_valeurs_min_ou_max(df_info_custom,df_info_custom_tempo,projet):
    df_info_custom_uniquement_valeur_cote = pd.concat([df_info_custom.set_index('CODE_custom'), df_info_custom_tempo])
    df_info_custom_uniquement_valeur_cote = df_info_custom_uniquement_valeur_cote.groupby(df_info_custom_uniquement_valeur_cote.index).agg({'min_x_custom':'min','max_x_custom':'max','min_y_custom':'min','max_y_custom':'max'})
    df_info_custom = df_info_custom.drop(columns=['min_x_custom','max_x_custom','min_y_custom','max_y_custom'])
    df_info_custom = pd.merge(df_info_custom,df_info_custom_uniquement_valeur_cote, left_on='CODE_custom', right_index=True)
    #PB : Pourquoi sur les cartes etats/pression, le nom de l'index reste NOM_MO, mais il est supprimé sur les cartes actions MIA
    df_info_custom.index.name = "NOM_MO"
    return df_info_custom

def ajout_marge_valeur_max(df_info_custom):
    marge= 0.03
    df_info_custom['min_x_custom'] = df_info_custom['min_x_custom'] - (df_info_custom['X_centre_custom']-df_info_custom['min_x_custom'])*marge
    df_info_custom['max_x_custom'] = df_info_custom['max_x_custom'] + (df_info_custom['max_x_custom']-df_info_custom['X_centre_custom'])*marge
    df_info_custom['min_y_custom'] = df_info_custom['min_y_custom'] - (df_info_custom['Y_centre_custom']-df_info_custom['min_y_custom'])*marge
    df_info_custom['max_y_custom'] = df_info_custom['max_y_custom'] + (df_info_custom['max_y_custom']-df_info_custom['Y_centre_custom'])*marge
    return df_info_custom

def ajout_info_boite_integral_si_boite_orthogonal_cartouche(df_info_custom,dict_dict_info_custom,dict_boite_complete_pour_placement):
    df_info_custom['cartouche_boite_ortho_separe']==False
    for custom in dict_dict_info_custom:
        for nom_boite_maitre,dict_boite_maitre in dict_boite_complete_pour_placement.items():
            for CODE_custom,df_custom in dict_boite_maitre.boite_complete.items():
                if dict_dict_info_custom[CODE_custom]['cartouche_boite_ortho_separe']==False:
                    if dict_boite_maitre.orientation =="orthogonal":
                        df_info_custom.loc[(df_info_custom.index == custom),"cartouche_boite_ortho_separe"]=True
    return df_info_custom


