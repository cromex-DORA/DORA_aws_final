# -*- coding: utf-8 -*-
import pandas as pd
import geopandas as gpd
from dotenv import load_dotenv
from app.DORApy.classes.modules import connect_path
from app.DORApy.classes.modules import config_DORA
dict_config_espace,dict_config_police = config_DORA.creation_dicts_config()

################################################################################################################################################################################
#ME
################################################################################################################################################################################
def creation_df_chainage_ME_aval():
    df_chainage = pd.read_csv("/mnt/g/travail/carto/couches de bases/ME/chainage_BV_ME_AG_2022.csv")
    df_chainage['CODE_ME_AVAL'] = df_chainage['CODE_ME_AVAL']
    df_chainage['CODE_ME_AMONT'] = df_chainage['CODE_ME_AMONT']
    df_chainage_ME_aval = dict(zip(df_chainage['CODE_ME_AMONT'].to_list(),df_chainage['CODE_ME_AVAL'].to_list()))
    return df_chainage_ME_aval

def df_chainage_list_amont(dict_dict_info_REF):
    df_chainage = pd.read_csv("/mnt/g/travail/carto/couches de bases/ME/chainage_BV_ME_AG_2022.csv")
    df_chainage['CODE_ME_AVAL'] = df_chainage['CODE_ME_AVAL']
    df_chainage['CODE_ME_AMONT'] = df_chainage['CODE_ME_AMONT']
    df_chainage_list_amont = df_chainage.groupby('CODE_ME_AVAL').agg({'CODE_ME_AMONT':lambda x: list(x)})
    dict_chainage_list_amont = df_chainage_list_amont.to_dict()['CODE_ME_AMONT']
    list_CODE_ME_aval_sans_ME_amont =  [x for x in dict_dict_info_REF["df_info_ME"]['CODE_ME'].to_list() if x not in list(dict_chainage_list_amont)]
    for CODE_ME_aval_sans_ME_amont in list_CODE_ME_aval_sans_ME_amont:
        dict_chainage_list_amont[CODE_ME_aval_sans_ME_amont] = []
    return dict_chainage_list_amont

def creation_dict_surface_par_ME_par_custom(dict_decoupREF_reduire,dict_special_custom_a_reduire=None):
    if dict_special_custom_a_reduire==None:
        df_adaptation_ME_decoupees = dict_decoupREF_reduire[CODE_custom]['gdf_decoupME_MO']
        df_adaptation_ME_decoupees['surface_ME'] = df_adaptation_ME_decoupees['surface_ME']/dict_config_espace['facteur_division'][self.taille_globale_carto]
        dict_surface_decoupME_par_custom={CODE_custom:dict(zip(df_adaptation_ME_decoupees['CODE_ME'].to_list(),df_adaptation_ME_decoupees['surface_ME'].to_list())) for CODE_custom in dict_decoupREF_reduire}
    if dict_special_custom_a_reduire!=None:
        dict_surface_decoupME_par_custom = {}
        for CODE_custom in dict_decoupREF_reduire:
            df_adaptation_ME_decoupees = dict_special_custom_a_reduire[CODE_custom]['df_taille_boite_complete']
            #On compléte le dictionnaire de taille par des 0 si éléments manquants
            df_adaptation_ME_decoupees["CODE_REF"] = df_adaptation_ME_decoupees["CODE_REF"].apply(lambda x: [x+"$"+str(numero) for numero in range(1,4)])
            df_adaptation_ME_decoupees=df_adaptation_ME_decoupees.explode("CODE_REF")
            df_adaptation_ME_decoupees['surface_boite'] = df_adaptation_ME_decoupees['surface_boite']/dict_config_espace['facteur_division'][self.taille_globale_carto]
            dict_surface_decoupME_par_custom[CODE_custom]=dict(zip(df_adaptation_ME_decoupees['CODE_REF'].to_list(),df_adaptation_ME_decoupees['surface_boite'].to_list()))
            liste_ME_total = dict_decoupREF_reduire[CODE_custom]['gdf_decoupME_custom']['CODE_ME'].to_list()
            dict_surface_decoupME_par_custom[CODE_custom] = {k:(dict_surface_decoupME_par_custom[CODE_custom][k] if k in dict_surface_decoupME_par_custom[CODE_custom] else 0)  for k in liste_ME_total}
    return dict_surface_decoupME_par_custom

def import_ME_CE_AG():
    filename = ("shp_files\\ME\\ME CE AG complet.shp")
    filename = connect_path.get_file_path_racine(filename)
    shp_ME_CE_AG = gpd.read_file(filename)
    return shp_ME_CE_AG


################################################################################################################################################################################
#SME
################################################################################################################################################################################
def import_shp_SOUS_ME(self):
    #couche PPG
    filename = ("shp_files\\SOUS_ME\\SME_DORA_MO.shp")
    filename = connect_path.get_file_path_racine(filename)
    shp_SME = gpd.read_file(filename)    
    shp_SME = shp_SME.to_crs('epsg:2154')
    #On dégage le premier FR
    shp_SME = shp_SME.rename(columns={'geometry':'geometry_SME'})
    shp_SME = shp_SME.set_geometry('geometry_SME')
    shp_SME['surface_SME'] = shp_SME.area
    return shp_SME

def remplacement_ME_par_SME(gdf_SME,gdf_ME):
    list_col_nom_ME = list(gdf_ME)
    tempo_shp_SME = gpd.overlay(gdf_SME[['NOM_SME','geometry_SME','surface_SME']], gdf_ME, how='intersection')
    tempo_shp_SME['surface_finale'] = tempo_shp_SME.area
    tempo_shp_SME['ratio'] = tempo_shp_SME['surface_finale']/tempo_shp_SME['surface_SME']
    tempo_shp_SME = tempo_shp_SME.loc[tempo_shp_SME['ratio']>0.70]
    tempo_shp_SME['tempo_chiffre'] = tempo_shp_SME.groupby('CODE_ME').cumcount()+1
    list_CODE_ME_a_remplacer_dans_gdf_ME = list(set(tempo_shp_SME['CODE_ME'].to_list()))
    tempo_shp_SME['CODE_ME'] = tempo_shp_SME['CODE_ME'] + "%" + tempo_shp_SME['tempo_chiffre'].astype(str)
    tempo_shp_SME['NOM_ME'] = tempo_shp_SME['NOM_SME']
    tempo_shp_SME = tempo_shp_SME.rename(columns={'geometry':'geometry_ME'})
    tempo_shp_SME['surface_ME'] = tempo_shp_SME['surface_finale']
    tempo_shp_SME = tempo_shp_SME[list_col_nom_ME]
    tempo_shp_SME = tempo_shp_SME.set_geometry('geometry_ME')
    tempo_shp_SME = tempo_shp_SME.to_crs('epsg:2154')
    gdf_ME = gdf_ME.set_geometry('geometry_ME')
    gdf_ME = gdf_ME.to_crs('epsg:2154')
    gdf_ME = gdf_ME.loc[~gdf_ME["CODE_ME"].isin(list_CODE_ME_a_remplacer_dans_gdf_ME)]
    gdf_ME = pd.concat([gdf_ME,tempo_shp_SME])
    return gdf_ME
