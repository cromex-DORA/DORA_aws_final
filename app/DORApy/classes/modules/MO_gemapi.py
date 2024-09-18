# -*- coding: utf-8 -*-
import pandas as pd
import glob
import os
import geopandas as gpd
import numpy as np
from app.DORApy.classes.modules import dataframe
from dotenv import load_dotenv
from app.DORApy.classes.modules import connect_path


################################################################################################################################################################################
#Module de toilettage des colonnes remplissages manuellement dans le fichier info Mo_gemapi
################################################################################################################################################################################
def toilettage_NOM_MO(csv_info_MO_gemapi):
    liste_NOM_MO = csv_info_MO_gemapi['NOM_MO'].to_list()
    liste_nom_propre_rajouter_majuscule_automatique = ["syndicat","mixte","bassin","versant","communauté","communes","commune"]
    liste_propre_NOM_MO = []
    for nom_MO in liste_NOM_MO:
        for nom_propre in liste_nom_propre_rajouter_majuscule_automatique:
            nom_MO = nom_MO.replace(nom_propre, nom_propre.capitalize())
        liste_propre_NOM_MO.append(nom_MO)
    csv_info_MO_gemapi['NOM_MO'] = liste_propre_NOM_MO
    return csv_info_MO_gemapi

def renommage_nom_entite_si_geometry_identique(gdf_base,gdf_a_ajouter,liste_CLE_primaire):
    col_nom_entite = liste_CLE_primaire[0]
    base = gdf_base.set_geometry('geometry_MO_gemapi_NA')
    a_ajouter = gdf_a_ajouter.set_geometry('geometry')
    base['surface_init'] = base.geometry.area
    tempo_inter = gpd.overlay(base, a_ajouter, how='intersection')
    tempo_inter['surface_finale'] = tempo_inter.geometry.area
    tempo_inter['ratio'] = tempo_inter['surface_finale']/tempo_inter['surface_init']
    tempo_inter = tempo_inter.loc[tempo_inter['ratio']>0.95]
    tempo_inter = tempo_inter.loc[tempo_inter[col_nom_entite + '_1']!=tempo_inter[col_nom_entite + '_2']]
    dict_tempo_tenommage = dict(zip(tempo_inter[col_nom_entite + '_2'].to_list(),tempo_inter[col_nom_entite + '_1'].to_list()))
    gdf_a_ajouter[col_nom_entite] = gdf_a_ajouter[col_nom_entite].map(dict_tempo_tenommage)
    return gdf_a_ajouter

################################################################################################################################################################################
#Module d'attribution des codes
################################################################################################################################################################################
def recherche_nom_MO_gemapi_et_SANDRE(gdf_avec_MO_gemapi):
    #couche PPG
    BDD_SANDRE = dataframe.recuperation_BDD_SANDRE()
    #On essaye de mettre un CODE SANDRE avec la colonne NOM_SANDRE
    dict_NOM_SANDRE_CD_SANDRE = dict(zip(BDD_SANDRE.NOM_MO,BDD_SANDRE.CD_SANDRE))
    
    gdf_avec_MO_gemapi['CD_SANDRE'] = gdf_avec_MO_gemapi['NOM_SANDRE'].map(dict_NOM_SANDRE_CD_SANDRE)
    liste_code_SANDRE = gdf_avec_MO_gemapi['CD_SANDRE'].to_list()
    liste_code_SANDRE = [x for x in liste_code_SANDRE if x==x]
    liste_code_SANDRE_valide = [x for x in liste_code_SANDRE if (x.startswith('INC') == True) if (len(x) == 20)]
    gdf_avec_MO_gemapi.loc[~gdf_avec_MO_gemapi['CD_SANDRE'].isin(liste_code_SANDRE_valide), 'CD_SANDRE'] = np.nan
    gdf_avec_MO_gemapi_CD_SANDRE_a_chercher = gdf_avec_MO_gemapi.loc[(gdf_avec_MO_gemapi['CD_SANDRE'].isnull())]
    liste_MO_gemapi_filtre_sans_CD_SANDRE_a_chercher = gdf_avec_MO_gemapi_CD_SANDRE_a_chercher['NOM_MO'].values.tolist()
    gdf_avec_MO_gemapi_filtre_avec_CD_SANDRE_ou_assimile = gdf_avec_MO_gemapi[~(gdf_avec_MO_gemapi['NOM_MO'].isin(liste_MO_gemapi_filtre_sans_CD_SANDRE_a_chercher))]
    gdf_avec_MO_gemapi_CD_SANDRE_a_chercher = gdf_avec_MO_gemapi_CD_SANDRE_a_chercher.drop(['CD_SANDRE'],axis=1)
    gdf_avec_MO_gemapi_CD_SANDRE_a_chercher = pd.merge(gdf_avec_MO_gemapi_CD_SANDRE_a_chercher,BDD_SANDRE[['CD_SANDRE','CODE_SIRET']],on='CODE_SIRET',how='left')
    #gdf_avec_MO_gemapi_CD_SANDRE_a_chercher = gdf_avec_MO_gemapi_CD_SANDRE_a_chercher.set_index('NOM_MO',drop=False)
    gdf_avec_MO_gemapi = pd.concat([gdf_avec_MO_gemapi_filtre_avec_CD_SANDRE_ou_assimile,gdf_avec_MO_gemapi_CD_SANDRE_a_chercher])
    gdf_avec_MO_gemapi = gdf_avec_MO_gemapi.reset_index(drop=True)
    gdf_avec_MO_gemapi.loc[(~gdf_avec_MO_gemapi['CD_SANDRE'].isnull(),'CODE_REF')]=gdf_avec_MO_gemapi['CD_SANDRE']
    return gdf_avec_MO_gemapi

def Generation_CODE_perso_MO_gemapi(gdf_avec_MO_gemapi):
    #On utilise quand méme les codes déjà utilisés pour ne pas qu'ils bougent
    gdf_avec_MO_gemapi.loc[(gdf_avec_MO_gemapi['CODE_REF'].isnull()),"CODE_REF"] = gdf_avec_MO_gemapi['CODE_MO']
    liste_CODE_REF_a_attribuer = gdf_avec_MO_gemapi.loc[(gdf_avec_MO_gemapi['CODE_REF'].isnull())]['CODE_REF'].to_list()
    liste_CODE_REF_deja_attribues = gdf_avec_MO_gemapi.loc[(gdf_avec_MO_gemapi['CODE_REF'].str.startswith('MO_gemapi_',na=False))]['CODE_REF'].to_list()
    liste_valeur_CODE_perso_deja_enregistre = [int(x.split("_")[2]) for x in liste_CODE_REF_deja_attribues]
    for numero_CODE_MO_gemapi,COE_MO_gemapi in enumerate(liste_CODE_REF_a_attribuer):
        for i in range(200,1000):
            if i not in liste_valeur_CODE_perso_deja_enregistre:
                liste_CODE_REF_a_attribuer[numero_CODE_MO_gemapi] = "MO_gemapi_" + str(i)
                liste_valeur_CODE_perso_deja_enregistre.append(i)
                break
    gdf_avec_MO_gemapi.loc[gdf_avec_MO_gemapi['CODE_REF']!=gdf_avec_MO_gemapi['CODE_REF'],'CODE_REF'] = liste_CODE_REF_a_attribuer
    return gdf_avec_MO_gemapi