# -*- coding: utf-8 -*-
import geopandas as gpd
import pandas as pd
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
import glob
import os
from app.DORApy.classes.modules import dataframe,MO_gemapi
from app.DORApy.classes.modules import connect_path


class GdfCompletREF(gpd.GeoDataFrame):
    @property
    def _constructor(self):
        return GdfCompletREF

    def attribution_GdfCompletREF(self,echelle_REF_shp):
        self.echelle_REF_shp = echelle_REF_shp
        if echelle_REF_shp=='CUSTOM':
            self.nom_entite_REF = 'NOM_CUSTOM'
            self.colonne_geometry = 'geometry_CUSTOM'
            self.type_de_geom = 'polygon'
        if echelle_REF_shp=='ME':
            self.nom_entite_REF = 'NOM_ME'
            self.colonne_geometry = 'geometry_ME'
            self.type_de_geom = 'polygon'
        if echelle_REF_shp=='SME':
            self.nom_entite_REF = 'NOM_SME'
            self.colonne_geometry = 'geometry_SME'
            self.type_de_geom = 'polygon'
        if echelle_REF_shp=='MO':
            self.nom_entite_REF = 'NOM_MO'
            self.colonne_geometry = 'geometry_MO'
            self.type_de_geom = 'polygon'
        if echelle_REF_shp=='PPG':
            self.nom_entite_REF = "NOM_PPG" 
            self.colonne_geometry = 'geometry_PPG'
            self.type_de_geom = 'polygon'
        if echelle_REF_shp=='BVG':
            self.nom_entite_REF = 'NOM_BVG'
            self.colonne_geometry = 'geometry_BVG'
            self.type_de_geom = 'polygon'
        if echelle_REF_shp=='ROE':
            self.nom_entite_REF = 'NOM_ROE'
            self.colonne_geometry = 'geometry_ROE'
            self.type_de_geom = 'point'
        if echelle_REF_shp=='SAGE':
            self.nom_entite_REF = 'NOM_SAGE'
            self.colonne_geometry = 'geometry_SAGE'
            self.type_de_geom = 'polygon'
        if echelle_REF_shp=='DEP':
            self.nom_entite_REF = 'NOM_DEP'
            self.colonne_geometry = 'geometry_DEP'  
            self.type_de_geom = 'polygon'
        if echelle_REF_shp=='REF_a_comparer':
            self.nom_entite_REF = 'NOM_REF_a_comparer'
            self.colonne_geometry = 'geometry_REF_a_comparer'  
            self.type_de_geom = 'polygon'
        self

    def recherche_shp_MO_ou_PPG_a_ajouter(REF):
        class ListGdfAjouter(list):
            @property
            def _constructor(self):
                return ListGdfAjouter

        def creation_col_NOM_REF(liste_couche_REF,REF,liste_nom_REF):
            liste_num_a_supprimer = []
            for numero,shp_REF_nouveau in enumerate(liste_couche_REF):
                if "NOM_"+REF not in list(shp_REF_nouveau):
                    print("il manque la colonne NOM_" + REF + " pour " + liste_nom_REF[numero])
                    liste_colonnes_potentielles_nom = dataframe.recuperer_liste_colonne_df_qui_commence_par_nom(shp_REF_nouveau)
                    if len(liste_colonnes_potentielles_nom)>0:
                        print("Mais je pense que NOM_" + REF + " est la colonne : " + liste_colonnes_potentielles_nom[0])
                        shp_REF_nouveau['NOM_'+REF] = shp_REF_nouveau[liste_colonnes_potentielles_nom[0]]
                    if len(liste_colonnes_potentielles_nom)==0:
                        print("Je n'ai pas trouvé de colonne qui commence par NOM_. Je ne peux pas ajouter la couche suivante : " + liste_nom_REF[numero])
                    liste_num_a_supprimer.append(numero)
            liste_couche_REF = [x for num,x in enumerate(liste_couche_REF) if num not in liste_num_a_supprimer]
            liste_nom_REF = [x for num,x in enumerate(liste_nom_REF) if num not in liste_num_a_supprimer]
            return liste_nom_REF,liste_couche_REF
        
        def recherche_col_debut_PPG(liste_couche_REF):
            liste_NOM_PPG_sans_debut_PPG = []
            for num,shp_REF_nouveau in enumerate(liste_couche_REF):
                if "debut_PPG" not in list(shp_REF_nouveau):
                    print("il manque la colonne debut PPG pour " + shp_REF_nouveau.nom_couche)
                    print("Je check le fichier tempo pour voir si il y a les infos")
                    df_tempo_pour_remplissage_debut_PPG = pd.read_csv('G:/travail/carto/couches de bases/ppg/fichier_tempo_pour_remplissage_debut_PPG.csv')
                    shp_REF_nouveau_avec_debut_PPG = pd.merge(shp_REF_nouveau,df_tempo_pour_remplissage_debut_PPG,on="NOM_PPG",how='left')
                    if shp_REF_nouveau_avec_debut_PPG["debut_PPG"].isnull().values.any():
                        print("Il manque encore des début PPG dans le fichier tempo")
                        shp_REF_nouveau_avec_debut_PPG = shp_REF_nouveau_avec_debut_PPG[["NOM_PPG","debut_PPG"]]
                        liste_NOM_PPG_sans_debut_PPG.append(shp_REF_nouveau_avec_debut_PPG)
                        liste_couche_REF.remove(shp_REF_nouveau)
                if "debut_PPG" in list(shp_REF_nouveau):
                    shp_REF_nouveau['debut_PPG'] = shp_REF_nouveau['debut_PPG'].astype(str)
                    shp_REF_nouveau['debut_PPG'] = shp_REF_nouveau['debut_PPG'].apply(lambda x: dataframe.extraire_string(x,4))
                    shp_REF_nouveau['debut_PPG'] = shp_REF_nouveau['debut_PPG'].astype(int)
                    liste_couche_REF[num] = shp_REF_nouveau
            if len(liste_NOM_PPG_sans_debut_PPG)>0:
                df_tempo_avec_nouveau_NOM_PPG_sans_debut_PPG = pd.concat(liste_NOM_PPG_sans_debut_PPG)
                df_tempo_pour_remplissage_debut_PPG = pd.concat([df_tempo_pour_remplissage_debut_PPG,df_tempo_avec_nouveau_NOM_PPG_sans_debut_PPG])
                df_tempo_pour_remplissage_debut_PPG = df_tempo_pour_remplissage_debut_PPG.sort_values(by=['debut_PPG'])
                df_tempo_pour_remplissage_debut_PPG = df_tempo_pour_remplissage_debut_PPG.drop_duplicates(subset=["NOM_PPG"],keep='first')
                df_tempo_pour_remplissage_debut_PPG.to_csv(connect_path.definir_PATH_DOSSIER_MAITRE() + "/shp_files/ppg/fichier_tempo_pour_remplissage_debut_PPG.csv",index=False)
            return liste_couche_REF
        
        if REF == 'MO':
            liste_couche_REF = [gpd.read_file(f,encoding='utf-8') for f in glob.glob(connect_path.definir_PATH_DOSSIER_MAITRE() + "/shp_files/syndicats GEMAPI/*.shp") if not f.endswith('MO_gemapi_NA.shp')]
            liste_nom_REF = [os.path.basename(f) for f in glob.glob(connect_path.definir_PATH_DOSSIER_MAITRE() + "/shp_files/syndicats GEMAPI/*.shp") if not f.endswith('MO_gemapi_NA.shp')]
            liste_nom_REF = [nom_csv[:-4] for nom_csv in liste_nom_REF]
        if REF == 'PPG':
            liste_couche_REF = [gpd.read_file(f,encoding='utf-8') for f in glob.glob(connect_path.definir_PATH_DOSSIER_MAITRE() + "/shp_files/ppg/*.shp") if not f.endswith('PPG_NA.shp')]
            liste_nom_REF = [os.path.basename(f) for f in glob.glob(connect_path.definir_PATH_DOSSIER_MAITRE() + "/shp_files/ppg/*.shp") if not f.endswith('PPG_NA.shp')]
            liste_nom_REF = [nom_csv[:-4] for nom_csv in liste_nom_REF]                
        liste_couche_REF = ListGdfAjouter(liste_couche_REF)
        for numero,shp_REF_nouveau in enumerate(liste_couche_REF):
            liste_couche_REF[numero].nom_couche = liste_nom_REF[numero]
        liste_nom_REF,liste_couche_REF = creation_col_NOM_REF(liste_couche_REF,REF,liste_nom_REF)
        if len(liste_couche_REF)>0:
            couche_REF = pd.concat(liste_couche_REF)
        if len(liste_couche_REF)==0:
            print("Besoin d'une couche propre à ajouter !")
            exit()
        couche_REF = GdfCompletREF(couche_REF)
        couche_REF = couche_REF.to_crs(2154)
        couche_REF['NOM_REF_a_comparer'] = couche_REF['NOM_'+REF]
        couche_REF['surface_REF_a_comparer'] = couche_REF.area
        couche_REF  = couche_REF.rename({"geometry":'geometry_REF_a_comparer'},axis=1)
        couche_REF['CODE_REF_a_comparer'] = couche_REF.index
        liste_colonne_a_garder = ["NOM_REF_a_comparer",'CODE_REF_a_comparer','surface_REF_a_comparer','geometry_REF_a_comparer']
        couche_REF = couche_REF[liste_colonne_a_garder]
        couche_REF = couche_REF.reset_index(drop=True)
        couche_REF = couche_REF.set_geometry('geometry_REF_a_comparer')
        GdfCompletREF.attribution_GdfCompletREF(couche_REF,'REF_a_comparer')
        return couche_REF

    
class ListGdfCUSTOM(GdfCompletREF):
    @property
    def _constructor(self):
        return ListGdfCUSTOM

    def reset_CODE_MO_et_nom_org_eventuels(self):
        self.loc[self['issu_BDD']==False,'CODE_CUSTOM'] = ""
        self.loc[self['issu_BDD']==False,'NOM_CUSTOM'] = ""
        return self

    def Attribution_CODE_MO_et_NOM_MO(self,dict_gdf_a_check):
        self['surface_CUSTOM'] = self.area
        if len(self.loc[self["issu_BDD"]==True])==len(self):
            self.liste_echelle_shp_par_CUSTOM = ['MO']
        if len(self)-len(self.loc[self["issu_BDD"]==True])>0:
            self.liste_echelle_shp_par_CUSTOM = ['MO']
        if len(self.loc[self["issu_BDD"]==True])==0:
            self.liste_echelle_shp_par_CUSTOM = []
        if len(self.loc[self["issu_BDD"]==False])>0:
            for echelle_gdf,gdf_a_check in dict_gdf_a_check.items():
                croisement_CUSTOM_BBD_MO = gpd.overlay(self.loc[self['issu_BDD']==False], gdf_a_check, how='intersection')
                croisement_CUSTOM_BBD_MO['surface_finale'] = croisement_CUSTOM_BBD_MO.geometry.area
                croisement_CUSTOM_BBD_MO['ratio_decoup'] = croisement_CUSTOM_BBD_MO['surface_finale']/croisement_CUSTOM_BBD_MO['surface_CUSTOM']
                croisement_CUSTOM_BBD_MO['ratio_origin'] = croisement_CUSTOM_BBD_MO['surface_'+gdf_a_check.echelle_REF_shp]/croisement_CUSTOM_BBD_MO['surface_CUSTOM']
                croisement_CUSTOM_BBD_MO = croisement_CUSTOM_BBD_MO.loc[croisement_CUSTOM_BBD_MO['ratio_decoup']>0.90]
                croisement_CUSTOM_BBD_MO = croisement_CUSTOM_BBD_MO.loc[(croisement_CUSTOM_BBD_MO['ratio_origin']>0.90)&(croisement_CUSTOM_BBD_MO['ratio_origin']<1.10)]
                if len(croisement_CUSTOM_BBD_MO)>0:
                    if echelle_gdf=='gdf_MO':
                        croisement_CUSTOM_BBD_MO['NOM_MO'] = croisement_CUSTOM_BBD_MO['NOM_MO_2']
                    dict_map_index_CODE = dict(zip(croisement_CUSTOM_BBD_MO['index'].to_list(),croisement_CUSTOM_BBD_MO['CODE_'+gdf_a_check.echelle_REF_shp].to_list()))
                    dict_map_index_NOM = dict(zip(croisement_CUSTOM_BBD_MO['index'].to_list(),croisement_CUSTOM_BBD_MO[gdf_a_check.nom_entite_REF].to_list()))
                    self['CODE_CUSTOM'] = self["index"].map(dict_map_index_CODE).fillna(self['CODE_CUSTOM'])
                    self['NOM_MO'] = self["index"].map(dict_map_index_NOM).fillna(self['NOM_MO'])
                    self.liste_echelle_shp_par_CUSTOM.append(gdf_a_check.echelle_REF_shp)
        return self 

    def recherche_CODE_MO_dans_BDD(self,dict_gdf_a_check):
        #Import info et gdf
        dict_df_info_shp = DictDfInfoShp({})
        dict_df_info_shp.creation_DictDfInfoShp()
        self['nom_provi'] = self['NOM_CUSTOM']
        self = ListGdfCUSTOM.reset_CODE_MO_et_nom_org_eventuels(self)
        self = ListGdfCUSTOM.Attribution_CODE_MO_et_NOM_MO(self,dict_gdf_a_check)
        self.loc[self['CODE_CUSTOM']=="",'NOM_CUSTOM'] = self.loc[self['CODE_CUSTOM']==""]['nom_provi']
        self.loc[self['CODE_CUSTOM']=="",'CODE_CUSTOM'] = ['CUSTOM_' + str(x) for x in range(0,len(self.loc[self['CODE_CUSTOM']==""]))]
        liste_col_a_garder = ['CODE_CUSTOM','NOM_CUSTOM','geometry_CUSTOM']
        return self

class GdfFondCarte(GdfCompletREF):
    @property
    def _constructor(self):
        return GdfFondCarte