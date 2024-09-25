# -*- coding: utf-8 -*-
from re import A
import pandas as pd
import geopandas as gpd

from app.DORApy.classes.modules import dataframe,geodataframe_boite
from app.DORApy.classes.Class_Bloc import Bloc,BlocTexteSimple,BlocIcone,BlocLignesMultiples

import shapely.geometry as geom
from shapely.geometry import Polygon,Point
from shapely.affinity import translate
from shapely import affinity

import os.path
from os import path
import numpy as np
import copy
import itertools
from functools import reduce

from app.DORApy.classes.modules import config_DORA

#Creation des dictionnaires de configuration
dict_config_espace,dict_config_police = config_DORA.creation_dicts_config()

##########################################################################################
#PARTIE boite complete
##########################################################################################
class DictBoiteComplete(dict):
    def __init__(self,taille_globale_carto):
        super().__init__()
        self.taille_globale_carto = taille_globale_carto

    ##########################################################################################
    #Calcul des tailles de boites
    ##########################################################################################
    def creation_eventuelle_dict_boite_ortho(self,dict_dict_info_CUSTOM):
        dict_boite_complete_pour_placement_orthogonal = copy.deepcopy(self)
        dict_CODE_CUSTOM_a_enlever = {}
        for nom_boite_maitre,dict_boite_maitre in self.items():
            dict_CODE_CUSTOM_a_enlever[nom_boite_maitre] = []
            for CODE_CUSTOM,df_CUSTOM in dict_boite_maitre.boite_complete.items():
                if dict_boite_maitre.orientation=='normal' or (dict_boite_maitre.orientation=='orthogonal' and dict_dict_info_CUSTOM[CODE_CUSTOM]['cartouche_boite_ortho_separe']==False):
                    dict_CODE_CUSTOM_a_enlever[nom_boite_maitre].append(CODE_CUSTOM)
        for nom_boite_maitre,list_CODE_CUSTOM_a_enlever in dict_CODE_CUSTOM_a_enlever.items():
            for CODE_CUSTOM in list_CODE_CUSTOM_a_enlever:
                del dict_boite_complete_pour_placement_orthogonal[nom_boite_maitre].boite_complete[CODE_CUSTOM]
        dict_boite_complete_pour_placement_orthogonal = {k:v for k,v in dict_boite_complete_pour_placement_orthogonal.items() if v.orientation == "orthogonal"}
        return dict_boite_complete_pour_placement_orthogonal

    def suppression_eventuelle_boite_ortho(self,dict_dict_info_CUSTOM):
        dict_CODE_CUSTOM_a_enlever = {}
        for nom_boite_maitre,dict_boite_maitre in self.items():
            dict_CODE_CUSTOM_a_enlever[nom_boite_maitre] = []
            for CODE_CUSTOM,df_CUSTOM in dict_boite_maitre.boite_complete.items():
                if (dict_boite_maitre.orientation=='orthogonal' and dict_dict_info_CUSTOM[CODE_CUSTOM]['cartouche_boite_ortho_separe']==True):
                    dict_CODE_CUSTOM_a_enlever[nom_boite_maitre].append(CODE_CUSTOM)
        for nom_boite_maitre,list_CODE_CUSTOM_a_enlever in dict_CODE_CUSTOM_a_enlever.items():
            for CODE_CUSTOM in list_CODE_CUSTOM_a_enlever:
                del self[nom_boite_maitre].boite_complete[CODE_CUSTOM]

        return self

    ##########################################################################################
    #PARTIE CUSTOM
    ##########################################################################################
    def actualisation_cote_bb_CUSTOM(self,df_info_CUSTOM,df_contour_global):
        marge_bord = 5/100
        self = pd.merge(self,df_info_CUSTOM[["CODE_CUSTOM","min_x_CUSTOM","max_x_CUSTOM","min_y_CUSTOM","max_y_CUSTOM"]],on="CODE_CUSTOM")
        self = pd.merge(self,df_contour_global,on="CODE_CUSTOM")
        self['max_x_CUSTOM'] = self[["droite_boite_complete", "max_x_CUSTOM"]].max(axis=1)+(self["max_x_CUSTOM"]-self["min_x_CUSTOM"])*marge_bord
        self['min_x_CUSTOM'] = self[["gauche_boite_complete", "min_x_CUSTOM"]].min(axis=1)-(self["max_x_CUSTOM"]-self["min_x_CUSTOM"])*marge_bord
        self['max_y_CUSTOM'] = self[["haut_boite_complete", "max_y_CUSTOM"]].max(axis=1)+(self["max_y_CUSTOM"]-self["min_y_CUSTOM"])*marge_bord
        self['min_y_CUSTOM'] = self[["bas_boite_complete", "min_y_CUSTOM"]].min(axis=1)-(self["max_y_CUSTOM"]-self["min_y_CUSTOM"])*marge_bord
        self = self[[x for x in list(self) if x not in ['droite_boite_complete','gauche_boite_complete','haut_boite_complete','bas_boite_complete']]]
        return self

    ##########################################################################################
    #Creation contour boite complete
    ##########################################################################################
    def decalage_final(self):
        def generation_boite_contour_simple(df,taille_globale_carto):
            #Generation boite biais
            bas = df["bas_boite_complete"]
            haut = df["haut_boite_complete"]
            gauche = df["gauche_boite_complete"]
            droite = df["droite_boite_complete"]
            liste_liste_coord_boite = [0,1,2,3]
            liste_liste_coord_boite[0] = droite,haut
            liste_liste_coord_boite[1] = droite,bas
            liste_liste_coord_boite[2] = gauche,bas
            liste_liste_coord_boite[3] = droite,haut
            polygon = Polygon(liste_liste_coord_boite)
            return polygon             
        self['contour_simple_tempo'] = self.apply(lambda x: generation_boite_contour_simple(x,"petite"),axis=1)

        return self


    def creation_df_contour(self,type_boite_placement):
        for nom_boite_maitre,dict_boite_complete in self.items():
            dict_boite_complete.df_contour = dict_boite_complete.df
        return self
    
    def import_hauteur_deviation(self,type_boite_placement):
        #dict_tempo_boite_complete_avec_point_y_deviation = copy.deepcopy(self)
        for nom_boite_maitre,dict_boite_complete in self.items():
            if dict_boite_complete.orientation in type_boite_placement:
                for nom_bloc,dict_bloc in dict_boite_complete.items():
                    if dict_bloc.type == "bloc_lignes_multiples":
                        dict_boite_complete.df_contour = pd.merge(dict_boite_complete.df_contour,dict_bloc.df[['CODE_REF','ecart_hauteur_origine']],on="CODE_REF",how='left')
                        dict_boite_complete.df_contour = pd.merge(dict_boite_complete.df_contour,dict_bloc.df_indiv.groupby("CODE_REF").agg({"hauteur_ligne_indiv_droit" : 'first'}),on="CODE_REF",how='left')
                        dict_boite_complete.df_contour['hauteur_premiere_ligne'] = dict_boite_complete.df_contour['hauteur_ligne_indiv_droit']/2/np.cos(dict_config_espace['angle_rotation_lm_paysage'][dict_bloc.taille_globale_carto] * np.pi / 180. )
                        
                        dict_boite_complete.df_contour.loc[~dict_boite_complete.df_contour['ecart_hauteur_origine'].isnull(),'ecart_hauteur_origine'] = dict_boite_complete.df_contour['ecart_hauteur_origine'] + dict_config_espace['alineaY_entre_boite_et_point_lm_paysage'][dict_bloc.taille_globale_carto]+ dict_config_espace['alineaY_point_lm_et_phrase_lm_paysage'][dict_bloc.taille_globale_carto] + dict_boite_complete.df_contour['hauteur_premiere_ligne']
                        dict_boite_complete.df_contour.loc[dict_boite_complete.df_contour['ecart_hauteur_origine'].isnull(),'ecart_hauteur_origine'] = dict_boite_complete.df_contour['taille_hauteur_boite_biais'] 
        for nom_boite_maitre,dict_boite_complete in self.items():
            if 'ecart_hauteur_origine' not in list(dict_boite_complete.df_contour):
                dict_boite_complete.df_contour['ecart_hauteur_origine'] = dict_boite_complete.df_contour['taille_hauteur_boite_biais']
        return self

    def creation_contour_boite_complete(self,type_boite_placement):
        def generation_boite_contour(df,taille_globale_carto):
            #Generation boite biais
            bas = df["bas_boite_complete"]
            haut = df["haut_boite_complete"]
            gauche = df["gauche_boite_complete"]
            droite = df["droite_boite_complete"]
            ecart_devi = df["ecart_hauteur_origine"]
            orientation = df["type_placement_boite_final"]
            liste_liste_coord_boite = [0,1,2,3,4,5]
            if orientation == 'G':
                liste_liste_coord_boite[0] = droite,haut
                liste_liste_coord_boite[1] = droite,bas
                liste_liste_coord_boite[2] = droite,bas
                liste_liste_coord_boite[3] = gauche,bas
                liste_liste_coord_boite[4] = gauche,haut
                liste_liste_coord_boite[5] = droite,haut
            if orientation == 'D':
                liste_liste_coord_boite[0] = droite,haut
                liste_liste_coord_boite[1] = droite,bas
                liste_liste_coord_boite[2] = droite,bas
                liste_liste_coord_boite[3] = gauche,bas
                liste_liste_coord_boite[4] = gauche,haut
                liste_liste_coord_boite[5] = droite,haut
            if orientation == 'B':
                ecart_devi = haut - ecart_devi
                liste_liste_coord_boite[0] = gauche,haut
                liste_liste_coord_boite[1] = droite,haut
                liste_liste_coord_boite[2] = [droite,ecart_devi]
                liste_liste_coord_boite[3] = [droite+(ecart_devi-bas)*np.cos((360-dict_config_espace['angle_rotation_lm_paysage'][taille_globale_carto]) * np.pi / 180. )*dict_config_espace['facteur_decalage_boite_complet_si_lm'][taille_globale_carto],bas]
                liste_liste_coord_boite[4] = [gauche+(ecart_devi-bas)*np.cos((360-dict_config_espace['angle_rotation_lm_paysage'][taille_globale_carto]) * np.pi / 180. )*dict_config_espace['facteur_decalage_boite_complet_si_lm'][taille_globale_carto],bas]
                liste_liste_coord_boite[5] = [gauche,ecart_devi]
            if orientation == 'H':
                ecart_devi = bas + ecart_devi
                liste_liste_coord_boite[0] = gauche,bas
                liste_liste_coord_boite[1] = droite,bas
                liste_liste_coord_boite[2] = [droite,ecart_devi]
                liste_liste_coord_boite[3] = [droite+(haut-ecart_devi)*np.cos(dict_config_espace['angle_rotation_lm_paysage'][taille_globale_carto] * np.pi / 180. )*dict_config_espace['facteur_decalage_boite_complet_si_lm'][taille_globale_carto],haut]
                liste_liste_coord_boite[4] = [gauche+(haut-ecart_devi)*np.cos(dict_config_espace['angle_rotation_lm_paysage'][taille_globale_carto] * np.pi / 180. )*dict_config_espace['facteur_decalage_boite_complet_si_lm'][taille_globale_carto],haut]
                liste_liste_coord_boite[5] = [gauche,ecart_devi]
            polygon = Polygon(liste_liste_coord_boite)
            return polygon         

        for nom_boite_maitre,dict_boite_complete in self.items():
            if dict_boite_complete.orientation in type_boite_placement:
                dict_boite_complete.df_contour["geom_boite"] = dict_boite_complete.df_contour.apply(lambda x: generation_boite_contour(x,dict_boite_complete.taille_globale_carto),axis=1)
                dict_boite_complete.df_contour = dict_boite_complete.df_contour[[x for x in list(dict_boite_complete.df_contour) if x!="geometry_point_interception"]]
                dict_boite_complete.df_contour = dict_boite_complete.df_contour.set_geometry('geom_boite')
                #dict_boite_complete.df_contour.to_file("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/test/essai_contour.shp")
        return self
    ##########################################################################################
    #Ajout des éventuelles infos des boites orthogonales
    ##########################################################################################
    def rassemblement_par_boite_complete(self):
        dict_df_tempo_par_orientation = {}
        for nom_boite_maitre,dict_boite_complete in self.items():
            dict_df_tempo_par_orientation[dict_boite_complete.orientation] = []
            for nom_bloc,dict_bloc in dict_boite_complete.items():
                dict_df_tempo_par_orientation[dict_boite_complete.orientation].append(dict_bloc.df)
                
        ###Renommage des colonnes
        for orientation,list_df in dict_df_tempo_par_orientation.items():
            for numero_bloc,df_bloc in enumerate(list_df):
                col_hauteur = [x for x in list(df_bloc) if (x.startswith('hauteur_bloc'))]
                col_hauteur_droit = [x for x in list(df_bloc) if (x.startswith('hauteur') and x.endswith('droit'))]
                col_hauteur_biais = [x for x in list(df_bloc) if (x.startswith('hauteur') and x.endswith('biais'))]
                col_largeur = [x for x in list(df_bloc) if (x.startswith('largeur_bloc'))]
                col_largeur_droit = [x for x in list(df_bloc) if (x.startswith('largeur') and x.endswith('droit'))]
                col_largeur_biais = [x for x in list(df_bloc) if (x.startswith('largeur') and x.endswith('biais'))]
                list_col_a_tester = [col_hauteur,col_hauteur_droit,col_hauteur_biais,col_largeur,col_largeur_droit,col_largeur_biais]
                #list_col_a_tester =  [x for xs in list_col_a_tester for x in xs]
                for col_a_tester in list_col_a_tester:
                    if len(col_a_tester)>0:
                        col_a_tester = col_a_tester[0]
                        if len(col_hauteur)>0:
                            if col_a_tester==col_hauteur[0]:
                                    list_df[numero_bloc]['taille_hauteur_bloc_droit'] = list_df[numero_bloc][col_a_tester]
                                    list_df[numero_bloc]['taille_hauteur_bloc_biais'] = list_df[numero_bloc][col_a_tester]
                        if len(col_largeur)>0:            
                            if col_a_tester==col_largeur[0]:
                                    list_df[numero_bloc]['taille_largeur_bloc_droit'] = list_df[numero_bloc][col_a_tester]
                                    list_df[numero_bloc]['taille_largeur_bloc_biais'] = list_df[numero_bloc][col_a_tester]
                        if len(col_hauteur_droit)>0:            
                            if col_a_tester==col_hauteur_droit[0]:
                                    list_df[numero_bloc]['taille_hauteur_bloc_droit'] = list_df[numero_bloc][col_a_tester]
                        if len(col_hauteur_biais)>0:            
                            if col_a_tester==col_hauteur_biais[0]:
                                    list_df[numero_bloc]['taille_hauteur_bloc_biais'] = list_df[numero_bloc][col_a_tester]
                        if len(col_largeur_droit)>0:             
                            if col_a_tester==col_largeur_droit[0]:
                                    list_df[numero_bloc]['taille_largeur_bloc_droit'] = list_df[numero_bloc][col_a_tester]
                        if len(col_largeur_biais)>0:            
                            if col_a_tester==col_largeur_biais[0]:
                                    list_df[numero_bloc]['taille_largeur_bloc_biais'] = list_df[numero_bloc][col_a_tester]
        ###Rassemblement des colonnes                            
        for orientation,list_df in dict_df_tempo_par_orientation.items():        
            df_taille_boite_complete = pd.concat(list_df)
            df_taille_boite_complete = df_taille_boite_complete[['CODE_REF','taille_hauteur_bloc_droit','taille_largeur_bloc_droit','taille_hauteur_bloc_biais','taille_largeur_bloc_biais']]
            df_taille_boite_complete = df_taille_boite_complete.groupby("CODE_REF").agg({'taille_hauteur_bloc_droit':"sum",'taille_largeur_bloc_droit':"max",'taille_hauteur_bloc_biais':"sum",'taille_largeur_bloc_biais':"max"})
            df_taille_boite_complete = df_taille_boite_complete.rename({'taille_hauteur_bloc_droit':'taille_hauteur_boite_droit','taille_largeur_bloc_droit':"taille_largeur_boite_droit",'taille_hauteur_bloc_biais':"taille_hauteur_boite_biais",'taille_largeur_bloc_biais':"taille_largeur_boite_biais"},axis=1)
            df_taille_boite_complete = df_taille_boite_complete.reset_index()
            dict_df_tempo_par_orientation[orientation] = df_taille_boite_complete
        for nom_boite_maitre,dict_boite_complete in self.items():
            dict_boite_complete.df = pd.merge(dict_boite_complete.df,dict_df_tempo_par_orientation[dict_boite_complete.orientation],on="CODE_REF")
        return self

    def suppression_boite_complete_vide(self):
        for type_boite in list(self):
            if len(self[type_boite].df)==0:
                del self[type_boite]
        return self    
    
    
    def modification_nom_colonne_echelle_carto_en_REF_commun(self,dict_dict_info_CUSTOM):
        for nom_boite_maitre,dict_boite_complete in self.items():
            for CODE_CUSTOM,df_CUSTOM in dict_boite_complete.boite_complete.items():
                df_CUSTOM['echelle_REF']=dict_boite_complete.echelle_carto
                df_CUSTOM.columns = [colonne.replace(dict_boite_complete.echelle_carto, 'REF') for colonne in list(df_CUSTOM)]
        return self

    def rassemblement_un_seul_df_par_CUSTOM(self,dict_dict_info_CUSTOM):
        #On rassemble tout dans le normal, par convention (pas de création de nouveau dict)
        dict_liste_CODE_REF = {}
        for nom_CUSTOM in dict_dict_info_CUSTOM:
            dict_liste_CODE_REF[nom_CUSTOM] = []
        for nom_boite_maitre,dict_boite_maitre in self.items():
            for nom_CUSTOM,df_CUSTOM in dict_boite_maitre.boite_complete.items():
                if dict_boite_maitre.orientation == "orthogonal" and dict_dict_info_CUSTOM[nom_CUSTOM]['cartouche_boite_ortho_separe']==False:
                    df_ortho = dict_boite_maitre.boite_complete[nom_CUSTOM]
                    dict_liste_CODE_REF[nom_CUSTOM].append(df_ortho)
                if dict_boite_maitre.orientation == "normal":
                    df_normal = dict_boite_maitre.boite_complete[nom_CUSTOM]
                    dict_liste_CODE_REF[nom_CUSTOM].append(df_normal)
        for nom_boite_maitre,dict_boite_maitre in self.items():
            for nom_CUSTOM,df_CUSTOM in dict_boite_maitre.boite_complete.items():
                if dict_boite_maitre.orientation=='normal' or (dict_boite_maitre.orientation=='orthogonal' and dict_dict_info_CUSTOM[nom_CUSTOM]['cartouche_boite_ortho_separe']==False):
                    dict_boite_maitre.boite_complete[nom_CUSTOM] = pd.concat(dict_liste_CODE_REF[nom_CUSTOM])
                    dict_boite_maitre.boite_complete[nom_CUSTOM] = dict_boite_maitre.boite_complete[nom_CUSTOM].reset_index(drop=True)
        return self

    def rassemblement_eventuel_boites_orthogonals(self,dict_dict_info_CUSTOM,dict_relation_shp_liste):
        self.modification_nom_colonne_echelle_carto_en_REF_commun(dict_dict_info_CUSTOM)
        self.rassemblement_un_seul_df_par_CUSTOM(dict_dict_info_CUSTOM)
        return self

    def ajout_colonne_placement_boite_final(self):
        df_CUSTOM = self.df
        if len(df_CUSTOM)>0:
            df_CUSTOM.loc[df_CUSTOM["orient_CUSTOM"]=='portrait',"type_placement_boite_final"] = df_CUSTOM["orient_GD"]
            df_CUSTOM.loc[df_CUSTOM["orient_CUSTOM"]=='paysage',"type_placement_boite_final"] = df_CUSTOM["orient_BH"]
            df_CUSTOM["replacement"] = "Non"
        return self 
    
    def placement_boite_complet_ME_entre_eux(self,dict_info_CUSTOM,type_placement):
        def empilement_boite_portrait(le_geodataframe_boite,type_placement,dict_info_CUSTOM):
            geodataframe_modifie = geodataframe_boite.empilement_portrait(le_geodataframe_boite,type_placement,dict_info_CUSTOM)
            return geodataframe_modifie

        def empilement_boite_paysage(le_geodataframe_boite,type_placement,dict_info_CUSTOM):
            geodataframe_modifie = geodataframe_boite.empilement_paysage(le_geodataframe_boite,type_placement,dict_info_CUSTOM)
            return geodataframe_modifie

        #Placement boite
        df_CUSTOM = self.df
        if len(df_CUSTOM)>0 and self.orientation=="normal":
            if (dict_info_CUSTOM['orient_CUSTOM'] =='portrait' and self.orientation=='normal'):
                if type_placement =="placement_boite_classique":
                    df_CUSTOM = empilement_boite_portrait(df_CUSTOM,type_placement,dict_info_CUSTOM)
                if type_placement =="placement_boite_extremite_qui_depassent" and dict_info_CUSTOM['boite_a_replacer']==True:
                    df_CUSTOM = empilement_boite_paysage(df_CUSTOM,type_placement,dict_info_CUSTOM)


            if (dict_info_CUSTOM['orient_CUSTOM'] =='paysage' and self.orientation=='normal'):
                if type_placement =="placement_boite_classique":
                    df_CUSTOM = empilement_boite_paysage(df_CUSTOM,type_placement,dict_info_CUSTOM)
                if type_placement =="placement_boite_extremite_qui_depassent" and dict_info_CUSTOM['boite_a_replacer']==True:
                    df_CUSTOM = empilement_boite_portrait(df_CUSTOM,type_placement,dict_info_CUSTOM)
        self.df = df_CUSTOM
        return self


    def tracer_ligne_pour_intersection_buffer(self,dict_info_CUSTOM,type_placement):
        if len(self.df)>0:
            if (dict_info_CUSTOM['orient_CUSTOM'] =='portrait' and self.orientation=='normal' and type_placement=="placement_boite_classique") or (dict_info_CUSTOM['orient_CUSTOM'] =='paysage' and self.orientation=='normal' and type_placement=="placement_boite_extremite_qui_depassent"):
                self.df['X_point_ouest'] = 300000
                self.df['X_point_est'] = 1800000
                self.df['geometry_point1_ligne_inter'] = gpd.points_from_xy(self.df['X_point_ouest'],self.df["Y_centre_boiteREF_apres_empilement"])
                self.df['geometry_point2_ligne_inter'] = gpd.points_from_xy(self.df['X_point_est'],self.df["Y_centre_boiteREF_apres_empilement"])
                self.df['geometry_ligne_inter_buffer'] = self.df.apply(lambda x: geom.LineString([x['geometry_point1_ligne_inter'], x['geometry_point2_ligne_inter']]), axis=1)
                self.df = self.df.drop(['geometry_point1_ligne_inter','geometry_point2_ligne_inter'],axis=1)
            if (dict_info_CUSTOM['orient_CUSTOM'] =='paysage' and self.orientation=='normal' and type_placement=="placement_boite_classique") or (dict_info_CUSTOM['orient_CUSTOM'] =='portrait' and self.orientation=='normal' and type_placement=="placement_boite_extremite_qui_depassent"):
                self.df['Y_point_sud'] = 6000000
                self.df['Y_point_nord'] = 7000000
                self.df['geometry_point1_ligne_inter'] = gpd.points_from_xy(self.df["X_centre_boiteREF_apres_empilement"],self.df['Y_point_sud'])
                self.df['geometry_point2_ligne_inter'] = gpd.points_from_xy(self.df["X_centre_boiteREF_apres_empilement"],self.df['Y_point_nord'])
                self.df['geometry_ligne_inter_buffer'] = self.df.apply(lambda x: geom.LineString([x['geometry_point1_ligne_inter'], x['geometry_point2_ligne_inter']]), axis=1)
                self.df = self.df.drop(['geometry_point1_ligne_inter','geometry_point2_ligne_inter'],axis=1)
            if self.orientation=='normal':
                self.df = self.df.set_geometry('geometry_ligne_inter_buffer')
                self.df = self.df.set_crs('epsg:2154')
        return self

    def intersection_ligne_buffer(self,df_buffer_CUSTOM,df_info_CUSTOM,type_placement):
        #La fonction intersection permet de comparer 2 gdf de méme longueur. Faut donc faire un merge avant
        if self.orientation=='normal':
            if len(self.df)>0:
                if type_placement =="placement_boite_classique":
                    #On prend toures les boites
                    gdf_filtre = self.df
                if type_placement =="placement_boite_extremite_qui_depassent":
                    if df_info_CUSTOM['orient_CUSTOM']=="paysage":
                        filtre_boite = (self.df["replacement"]=="portrait")
                    if df_info_CUSTOM['orient_CUSTOM']=="portrait":
                        filtre_boite = (self.df["replacement"]=="paysage")
                    gdf_filtre = self.df[filtre_boite]
                geometry_CUSTOM_buffer_tempo = df_buffer_CUSTOM.gdf_buffer.reset_index()['geometry_CUSTOM_buffer']
                liste_ligne_inter_buffer_tempo = gdf_filtre['geometry_ligne_inter_buffer'].tolist()
                gdf_filtre['liste_point_intersection']=[lignes.intersection(geometry_CUSTOM_buffer_tempo[0]) for lignes in liste_ligne_inter_buffer_tempo]    
                #Si on foire l'intersection (cf pas QUE des points), c'est qu'il faut réduire le CUSTOM
                if type_placement =="placement_boite_classique":
                    self.df = gdf_filtre
                if type_placement =="placement_boite_extremite_qui_depassent":
                    liste_resultats_intersection = gdf_filtre['liste_point_intersection'].to_list()
                    liste_resultats_intersection = [x.geom_type for x in liste_resultats_intersection]
                    self.df = self.df[~filtre_boite]
                    self.df = pd.concat([self.df,gdf_filtre])
        return self

    def gestion_erreurs_interceptions_ligne_buffer(self,df_info_CUSTOM,type_placement):
        if self.orientation=='normal':
            if len(self.df)>0:
                if type_placement == "placement_boite_classique":
                    #On prend toures les boites
                    gdf_filtre = self.df
                if type_placement =="placement_boite_extremite_qui_depassent":
                    if df_info_CUSTOM['orient_CUSTOM']=="paysage":
                        filtre_boite = (self.df["replacement"]=="portrait")
                    if df_info_CUSTOM['orient_CUSTOM']=="portrait":
                        filtre_boite = (self.df["replacement"]=="paysage")
                    gdf_filtre = self.df[filtre_boite]
                liste_point_inter_buffer_tempo = gdf_filtre['liste_point_intersection'].tolist()
                gdf_filtre['liste_point_intersection'] = [np.nan if point.is_empty else point for point in liste_point_inter_buffer_tempo]
                #Si il y a trop de boites et que éa dépasse, on remplit avec les points précédents ou suivants
                if type_placement =="placement_boite_classique":
                    if (df_info_CUSTOM['orient_CUSTOM'] =='portrait' and self.orientation=='normal'):
                        gdf_filtre.loc[gdf_filtre['liste_point_intersection'].isnull(),'replacement'] = 'paysage'
                        gdf_filtre['liste_point_intersection'] = gdf_filtre.groupby('orient_GD')['liste_point_intersection'].bfill()
                        gdf_filtre['liste_point_intersection'] = gdf_filtre.groupby('orient_GD')['liste_point_intersection'].ffill()
                        if gdf_filtre.loc[gdf_filtre['orient_GD']=="G"]["liste_point_intersection"].isnull().all():
                            len_orient_G = len(gdf_filtre.loc[gdf_filtre['orient_GD']=="G"])
                            gdf_filtre.loc[gdf_filtre['orient_GD']=="G","liste_point_intersection"] = gpd.points_from_xy([df_info_CUSTOM['min_x_CUSTOM']]*len_orient_G,gdf_filtre.loc[gdf_filtre['orient_GD']=="G"]["Y_centre_boiteREF_apres_empilement"])
                            gdf_filtre.loc[gdf_filtre['orient_GD']=="G","liste_point_intersection"] = gdf_filtre.loc[gdf_filtre['orient_GD']=="G"]["liste_point_intersection"].apply(lambda x:(x,x))
                        if gdf_filtre.loc[gdf_filtre['orient_GD']=="D"]["liste_point_intersection"].isnull().all():
                            len_orient_D = len(gdf_filtre.loc[gdf_filtre['orient_GD']=="D"])
                            gdf_filtre.loc[gdf_filtre['orient_GD']=="D","liste_point_intersection"] = gpd.points_from_xy([df_info_CUSTOM['max_x_CUSTOM']]*len_orient_D,gdf_filtre.loc[gdf_filtre['orient_GD']=="D"]["Y_centre_boiteREF_apres_empilement"])
                            gdf_filtre.loc[gdf_filtre['orient_GD']=="D","liste_point_intersection"] = gdf_filtre.loc[gdf_filtre['orient_GD']=="D"]["liste_point_intersection"].apply(lambda x:(x,x))
                    if (df_info_CUSTOM['orient_CUSTOM'] =='paysage' and self.orientation=='normal'):
                        gdf_filtre.loc[gdf_filtre['liste_point_intersection'].isnull(),'replacement'] = 'portrait'
                        gdf_filtre['liste_point_intersection'] = gdf_filtre.groupby('orient_BH')['liste_point_intersection'].bfill()
                        gdf_filtre['liste_point_intersection'] = gdf_filtre.groupby('orient_BH')['liste_point_intersection'].ffill()
                        if gdf_filtre.loc[gdf_filtre['orient_BH']=="B"]["liste_point_intersection"].isnull().all():
                            len_orient_B = len(gdf_filtre.loc[gdf_filtre['orient_BH']=="B"])
                            gdf_filtre.loc[gdf_filtre['orient_BH']=="B","liste_point_intersection"] = gpd.points_from_xy(gdf_filtre.loc[gdf_filtre['orient_BH']=="B"]["X_centre_boiteREF_apres_empilement"],[df_info_CUSTOM['min_y_CUSTOM']]*len_orient_B)
                            gdf_filtre.loc[gdf_filtre['orient_BH']=="B","liste_point_intersection"] = gdf_filtre.loc[gdf_filtre['orient_BH']=="B"]["liste_point_intersection"].apply(lambda x:(x,x))
                        if gdf_filtre.loc[gdf_filtre['orient_BH']=="H"]["liste_point_intersection"].isnull().all():
                            len_orient_H = len(gdf_filtre.loc[gdf_filtre['orient_BH']=="H"])
                            gdf_filtre.loc[gdf_filtre['orient_BH']=="H","liste_point_intersection"] = gpd.points_from_xy(gdf_filtre.loc[gdf_filtre['orient_BH']=="H"]["X_centre_boiteREF_apres_empilement"],[df_info_CUSTOM['max_y_CUSTOM']]*len_orient_H)
                            gdf_filtre.loc[gdf_filtre['orient_BH']=="H","liste_point_intersection"] = gdf_filtre.loc[gdf_filtre['orient_BH']=="H"]["liste_point_intersection"].apply(lambda x:(x,x))

                #Si il y a trop de boites et que éa dépasse, on remplit avec les points précédents ou suivants
                if type_placement =="placement_boite_extremite_qui_depassent":
                    if (df_info_CUSTOM['orient_CUSTOM'] =='portrait' and self.orientation=='normal'):
                        gdf_filtre.loc[gdf_filtre['liste_point_intersection'].isnull(),'replacement'] = 'paysage'
                        gdf_filtre['liste_point_intersection'] = gdf_filtre.groupby('orient_BH')['liste_point_intersection'].bfill()
                        gdf_filtre['liste_point_intersection'] = gdf_filtre.groupby('orient_BH')['liste_point_intersection'].ffill()
                    if (df_info_CUSTOM['orient_CUSTOM'] =='paysage' and self.orientation=='normal'):
                        gdf_filtre.loc[gdf_filtre['liste_point_intersection'].isnull(),'replacement'] = 'portrait'
                        gdf_filtre['liste_point_intersection'] = gdf_filtre.groupby('orient_GD')['liste_point_intersection'].bfill()
                        gdf_filtre['liste_point_intersection'] = gdf_filtre.groupby('orient_GD')['liste_point_intersection'].ffill()
                if type_placement =="placement_boite_classique":
                    self.df = gdf_filtre
                if type_placement =="placement_boite_extremite_qui_depassent":
                    self.df = self.df[~filtre_boite]
                    self.df = pd.concat([self.df,gdf_filtre])
        return self

    def extraction_liste_coord_apres_interception(self,df_info_CUSTOM,type_placement):
        if self.orientation=='normal':
            if len(self.df)>0:
                if type_placement =="placement_boite_classique":
                    #On prend toures les boites
                    gdf_filtre = self.df
                if type_placement =="placement_boite_extremite_qui_depassent":
                    if df_info_CUSTOM['orient_CUSTOM']=="paysage":
                        filtre_boite = (self.df["replacement"]=="portrait")
                    if df_info_CUSTOM['orient_CUSTOM']=="portrait":
                        filtre_boite = (self.df["replacement"]=="paysage")
                    gdf_filtre = self.df[filtre_boite]
                if type_placement=="placement_boite_classique":
                    if (df_info_CUSTOM['orient_CUSTOM'] =='portrait' and self.orientation=='normal'):
                        liste_liste_2_points_G = gdf_filtre['liste_point_intersection'].loc[gdf_filtre['orient_GD'] == 'G'].tolist()
                        liste_liste_2_points_D = gdf_filtre['liste_point_intersection'].loc[gdf_filtre['orient_GD'] == 'D'].tolist()
                        liste_liste_2_x_G = [[(pt.geoms[0].x),(pt.geoms[1].x)] for pt in liste_liste_2_points_G]
                        liste_liste_2_x_D = [[(pt.geoms[0].x),(pt.geoms[1].x)] for pt in liste_liste_2_points_D]
                        liste_x_G = [min(liste_2_x_G) for liste_2_x_G in liste_liste_2_x_G]
                        liste_x_D = [max(liste_2_x_D) for liste_2_x_D in liste_liste_2_x_D]
                        liste_x = liste_x_G + liste_x_D
                        gdf_filtre["X_centre_boiteREF_apres_empilement"]=liste_x
                    if (df_info_CUSTOM['orient_CUSTOM'] =='paysage' and self.orientation=='normal'):
                        liste_liste_2_points_B = gdf_filtre['liste_point_intersection'].loc[gdf_filtre['orient_BH'] == 'B'].tolist()
                        liste_liste_2_points_H = gdf_filtre['liste_point_intersection'].loc[gdf_filtre['orient_BH'] == 'H'].tolist()
                        liste_liste_2_y_B = [[(pt.geoms[0].y),(pt.geoms[1].y)] for pt in liste_liste_2_points_B]
                        liste_liste_2_y_H = [[(pt.geoms[0].y),(pt.geoms[1].y)] for pt in liste_liste_2_points_H]
                        liste_y_B = [min(liste_2_y_B) for liste_2_y_B in liste_liste_2_y_B]
                        liste_y_H = [max(liste_2_y_H) for liste_2_y_H in liste_liste_2_y_H]
                        liste_y = liste_y_B + liste_y_H
                        gdf_filtre["Y_centre_boiteREF_apres_empilement"]=liste_y
                if type_placement=="placement_boite_extremite_qui_depassent":
                    if (df_info_CUSTOM['orient_CUSTOM'] =='portrait' and self.orientation=='normal'):
                        liste_liste_2_points_B = gdf_filtre['liste_point_intersection'].loc[gdf_filtre['orient_BH'] == 'B'].tolist()
                        liste_liste_2_points_H = gdf_filtre['liste_point_intersection'].loc[gdf_filtre['orient_BH'] == 'H'].tolist()
                        liste_liste_2_y_B = [[(pt.geoms[0].y),(pt.geoms[1].y)] for pt in liste_liste_2_points_B]
                        liste_liste_2_y_H = [[(pt.geoms[0].y),(pt.geoms[1].y)] for pt in liste_liste_2_points_H]
                        liste_y_B = [min(liste_2_y_B) for liste_2_y_B in liste_liste_2_y_B]
                        liste_y_H = [max(liste_2_y_H) for liste_2_y_H in liste_liste_2_y_H]
                        liste_y = liste_y_B + liste_y_H
                        gdf_filtre["Y_centre_boiteREF_apres_empilement"]=liste_y
                        gdf_filtre["traité"] = "oui"
                    if (df_info_CUSTOM['orient_CUSTOM'] =='paysage' and self.orientation=='normal'):
                        liste_liste_2_points_G = gdf_filtre['liste_point_intersection'].loc[gdf_filtre['orient_GD'] == 'G'].tolist()
                        liste_liste_2_points_D = gdf_filtre['liste_point_intersection'].loc[gdf_filtre['orient_GD'] == 'D'].tolist()
                        liste_liste_2_x_G = [[(pt.geoms[0].x),(pt.geoms[1].x)] for pt in liste_liste_2_points_G]
                        liste_liste_2_x_D = [[(pt.geoms[0].x),(pt.geoms[1].x)] for pt in liste_liste_2_points_D]
                        liste_x_G = [min(liste_2_x_G) for liste_2_x_G in liste_liste_2_x_G]
                        liste_x_D = [max(liste_2_x_D) for liste_2_x_D in liste_liste_2_x_D]
                        liste_x = liste_x_G + liste_x_D
                        gdf_filtre["X_centre_boiteREF_apres_empilement"]=liste_x
                        gdf_filtre["traité"] = "oui"
                if type_placement =="placement_boite_classique":
                    self.df = gdf_filtre
                if type_placement =="placement_boite_extremite_qui_depassent":
                    self.df = self.df[~filtre_boite]
                    self.df = pd.concat([self.df,gdf_filtre])
        return self
    
    def actualisation_orient_GD_et_BH(self,df_info_CUSTOM):
        if self.orientation=='normal':
            if len(self.df)>0:
                if (df_info_CUSTOM['orient_CUSTOM'] =='portrait' and self.orientation=='normal'):
                    milieu_y_CUSTOM = (df_info_CUSTOM['max_y_CUSTOM']+df_info_CUSTOM['min_y_CUSTOM'])/2
                    self.df.loc[self.df['Y_centre_boiteREF_apres_empilement']>milieu_y_CUSTOM,'orient_BH'] = "H"
                    self.df.loc[self.df['Y_centre_boiteREF_apres_empilement']<milieu_y_CUSTOM,'orient_BH'] = "B"
                if (df_info_CUSTOM['orient_CUSTOM'] =='paysage' and self.orientation=='normal'):
                    milieu_x_CUSTOM = (df_info_CUSTOM['max_x_CUSTOM']+df_info_CUSTOM['min_x_CUSTOM'])/2
                    self.df.loc[self.df['X_centre_boiteREF_apres_empilement']>milieu_x_CUSTOM,'orient_GD'] = "D"
                    self.df.loc[self.df['X_centre_boiteREF_apres_empilement']<milieu_x_CUSTOM,'orient_GD'] = "G"
        return self

    def calcul_nombre_boite_qui_depassent_a_deplacer(self,df_info_CUSTOM):
        ###Replacement boite
        if len(self.df)>1 and self.orientation=="normal":
            if (df_info_CUSTOM['orient_CUSTOM'] =='portrait' and self.orientation=='normal'):
                #HAUT
                largeur_maximal_dispo_sur_CUSTOM = (df_info_CUSTOM['max_x_CUSTOM']+dict_config_espace['longueur_buffer_custom'][self.taille_globale_carto])-(df_info_CUSTOM['min_x_CUSTOM']-dict_config_espace['longueur_buffer_custom'][self.taille_globale_carto])
                nombre_boite_a_deplacer_H = len(self.df[(self.df['replacement']=='paysage')&(self.df['orient_BH']=='H')])
                nombre_boite_H = len(self.df[(self.df['orient_BH']=='H')])
                if nombre_boite_a_deplacer_H>0:
                    df_info_CUSTOM["boite_a_replacer"] = True
                    self.df = self.df.sort_values(by="Y_centre_boiteREF_apres_empilement")
                    self.df = self.df.reset_index(drop=True)
                    liste_y_boite=self.df["Y_centre_boiteREF_apres_empilement"].to_list()
                    liste_largeur = self.df["taille_largeur_boite_biais"].to_list()
                    liste_x = self.df["X_centre_boiteREF_apres_empilement"].to_list()
                    liste_orient = self.df["orient_GD"].to_list()
                    liste_REF = self.df["CODE_REF"].to_list()
                    liste_largeur_disponible_H = [largeur_maximal_dispo_sur_CUSTOM] * len(liste_REF)
                    nombre_boite_partie_haute = len(self.df[self.df["orient_BH"]=="H"])
                    #Définition largeur disponible en fonction des boites déplacées
                    for numero_REF in range(len(liste_REF)-1,nombre_boite_partie_haute,-1):
                        premiere_valeur_droite = self.df.iloc[:numero_REF].loc[self.df["orient_GD"]=="D"].iloc[-1]["X_centre_boiteREF_apres_empilement"]
                        premiere_valeur_gauche = self.df.iloc[:numero_REF].loc[self.df["orient_GD"]=="G"].iloc[-1]["X_centre_boiteREF_apres_empilement"]
                        liste_largeur_disponible_H[numero_REF] = premiere_valeur_droite-premiere_valeur_gauche
                    liste_espace_pris_par_boite_H = np.cumsum(liste_largeur[::-1])[::-1]
                    liste_espace_pris_par_boite_H = [largeur_cumsum+(len(liste_espace_pris_par_boite_H)-numero_REF+1)*dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto] for numero_REF,largeur_cumsum in enumerate(liste_espace_pris_par_boite_H)]
                    #Si on a assez de place pour replacer le nombre de boite à déplacer,on vise le minimum.
                    liste_ecart_H = [9999999999] * len(liste_REF)
                    #On demarre directement à la boite qui depasse pas
                    for numero_REF in range(len(liste_REF)-nombre_boite_a_deplacer_H,-1,-1):
                        liste_ecart_H[numero_REF] = liste_espace_pris_par_boite_H[numero_REF]-liste_largeur_disponible_H[numero_REF]
                        if liste_espace_pris_par_boite_H[numero_REF]<liste_largeur_disponible_H[numero_REF]:
                            numero_boite_a_bouger_max = numero_REF+1
                            for numero_boite in range(numero_boite_a_bouger_max-1,len(liste_REF)):
                                self.df.loc[numero_boite,"replacement"] = "paysage"
                            break
                        #Si y pas la place, on cherche le minimum (et on envisage de découper en plus petit le syndicat)
                        if numero_REF<nombre_boite_H:
                            index_boite_optimal_a_replacer_H = liste_ecart_H.index(min(liste_ecart_H))
                            for numero_boite in range(index_boite_optimal_a_replacer_H,len(liste_REF)):
                                self.df.loc[numero_boite,"replacement"] = "paysage"

                #BAS
                largeur_maximal_dispo_sur_CUSTOM = (df_info_CUSTOM['max_x_CUSTOM']+dict_config_espace['longueur_buffer_custom'][self.taille_globale_carto])-(df_info_CUSTOM['min_x_CUSTOM']-dict_config_espace['longueur_buffer_custom'][self.taille_globale_carto])
                nombre_boite_a_deplacer_B = len(self.df[(self.df['replacement']=='paysage')&(self.df['orient_BH']=='B')])
                nombre_boite_B = len(self.df[(self.df['orient_BH']=='B')])
                if nombre_boite_a_deplacer_B>0:
                    df_info_CUSTOM["boite_a_replacer"] = True
                    self.df = self.df.sort_values(by="Y_centre_boiteREF_apres_empilement")
                    self.df = self.df.reset_index(drop=True)
                    liste_largeur = self.df["taille_largeur_boite_droit"].to_list()
                    liste_REF = self.df["CODE_REF"].to_list()
                    nombre_boite_partie_basse = len(self.df[self.df["orient_BH"]=="B"])
                    liste_largeur_disponible_B = [largeur_maximal_dispo_sur_CUSTOM] * len(liste_REF)
                    #Définition largeur disponible en fonction des boites déplacées
                    for numero_REF in range(0,nombre_boite_partie_basse-1):
                        premiere_valeur_droite = self.df.iloc[numero_REF+1:].loc[self.df["orient_GD"]=="D"].iloc[0]["X_centre_boiteREF_apres_empilement"]
                        premiere_valeur_gauche = self.df.iloc[numero_REF+1:].loc[self.df["orient_GD"]=="G"].iloc[0]["X_centre_boiteREF_apres_empilement"]
                        liste_largeur_disponible_B[numero_REF] = premiere_valeur_droite-premiere_valeur_gauche
                    liste_espace_pris_par_boite_B = np.cumsum(liste_largeur)
                    liste_espace_pris_par_boite_B = [largeur_cumsum+(numero_REF)*dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto] for numero_REF,largeur_cumsum in enumerate(liste_espace_pris_par_boite_B)]
                    liste_ecart_B = [9999999999] * len(liste_REF)
                    #Définition largeur prises par l'ensemble des boites déplacées
                    
                    for numero_REF in range(nombre_boite_a_deplacer_B-1,len(liste_REF)):
                        liste_ecart_B[numero_REF] = liste_espace_pris_par_boite_B[numero_REF]-liste_largeur_disponible_B[numero_REF]
                        if liste_espace_pris_par_boite_B[numero_REF]<liste_largeur_disponible_B[numero_REF]:
                            numero_boite_a_bouger_max = numero_REF+1
                            for numero_boite in range(0,numero_boite_a_bouger_max):
                                self.df.loc[numero_boite,"replacement"] = "paysage"
                            #Si y pas la place, on fait rien, et on découpe le CUSTOM en éléments plus petits
                            break
                        #Si y pas la place, on cherche le minimum (et on envisage de découper en plus petit le syndicat)
                        if numero_REF>nombre_boite_B:
                            index_boite_optimal_a_replacer_B = liste_ecart_B.index(min(liste_ecart_B))
                            for numero_boite in range(0,index_boite_optimal_a_replacer_B+1):
                                self.df.loc[numero_boite,"replacement"] = "paysage"

            if (df_info_CUSTOM['orient_CUSTOM'] =='paysage' and self.orientation=='normal'):
                #DROITE
                hauteur_maximal_dispo_sur_CUSTOM = (df_info_CUSTOM['max_y_CUSTOM']+dict_config_espace['longueur_buffer_custom'][self.taille_globale_carto])-(df_info_CUSTOM['min_y_CUSTOM']-dict_config_espace['longueur_buffer_custom'][self.taille_globale_carto])
                nombre_boite_a_deplacer_D = len(self.df[(self.df['replacement']=='portrait')&(self.df['orient_GD']=='D')])
                if nombre_boite_a_deplacer_D>0:
                    df_info_CUSTOM["boite_a_replacer"] = True
                    self.df = self.df.sort_values(by="X_centre_boiteREF_apres_empilement")
                    self.df = self.df.reset_index(drop=True)
                    liste_x_boite=self.df["X_centre_boiteREF_apres_empilement"].to_list()
                    liste_hauteur = self.df["taille_hauteur_boite_droit"].to_list()
                    liste_y = self.df["Y_centre_boiteREF_apres_empilement"].to_list()
                    liste_orient = self.df["orient_BH"].to_list()
                    liste_REF = self.df["CODE_REF"].to_list()
                    liste_hauteur_disponible_D = [hauteur_maximal_dispo_sur_CUSTOM] * len(liste_REF)
                    nombre_boite_partie_droite = len(self.df[self.df["orient_GD"]=="D"])
                    #Définition largeur disponible en fonction des boites déplacées
                    for numero_REF in range(len(liste_REF)-1,nombre_boite_partie_droite,-1):
                        premiere_valeur_haute = self.df.iloc[:numero_REF].loc[self.df["orient_BH"]=="H"].iloc[-1]["Y_centre_boiteREF_apres_empilement"]
                        premiere_valeur_basse = self.df.iloc[:numero_REF].loc[self.df["orient_BH"]=="B"].iloc[-1]["Y_centre_boiteREF_apres_empilement"]
                        liste_hauteur_disponible_D[numero_REF] = premiere_valeur_haute-premiere_valeur_basse
                    liste_espace_pris_par_boite_D = np.cumsum(liste_hauteur[::-1])[::-1]
                    liste_espace_pris_par_boite_D = [hauteur_cumsum+(len(liste_espace_pris_par_boite_D)-numero_REF+1)*dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto] for numero_REF,hauteur_cumsum in enumerate(liste_espace_pris_par_boite_D)]
                    #Définition hauteur prises par l'ensemble des boites déplacées
                    for numero_REF in range(len(liste_REF)-nombre_boite_a_deplacer_D,-1,-1):
                        if liste_espace_pris_par_boite_D[numero_REF]<liste_hauteur_disponible_D[numero_REF]:
                            numero_boite_a_bouger_max = numero_REF+1
                            for numero_boite in range(numero_boite_a_bouger_max-1,len(liste_REF)):
                                self.df.loc[numero_boite,"replacement"] = "portrait"
                            #Si y pas la place, on fait rien, et on découpe le CUSTOM en éléments plus petits
                            break


                #GAUCHE
                hauteur_maximal_dispo_sur_CUSTOM = (df_info_CUSTOM['max_y_CUSTOM']+dict_config_espace['longueur_buffer_custom'][self.taille_globale_carto])-(df_info_CUSTOM['min_y_CUSTOM']-dict_config_espace['longueur_buffer_custom'][self.taille_globale_carto])
                nombre_boite_a_deplacer_G = len(self.df[(self.df['replacement']=='portrait')&(self.df['orient_GD']=='G')])
                if nombre_boite_a_deplacer_G>0:
                    df_info_CUSTOM["boite_a_replacer"] = True
                    self.df = self.df.sort_values(by="X_centre_boiteREF_apres_empilement")
                    self.df = self.df.reset_index(drop=True)
                    liste_x_boite=self.df["X_centre_boiteREF_apres_empilement"].to_list()
                    liste_hauteur = self.df["taille_hauteur_boite_droit"].to_list()
                    liste_y = self.df["Y_centre_boiteREF_apres_empilement"].to_list()
                    liste_orient = self.df["orient_BH"].to_list()
                    liste_REF = self.df["CODE_REF"].to_list()
                    liste_hauteur_disponible_G = [hauteur_maximal_dispo_sur_CUSTOM] * len(liste_REF)
                    nombre_boite_partie_gauche = len(self.df[self.df["orient_GD"]=="G"])
                    #Définition hauteur disponible en fonction des boites déplacées
                    for numero_REF in range(0,nombre_boite_partie_gauche-1):
                        premiere_valeur_haute = self.df.iloc[numero_REF+1:].loc[self.df["orient_BH"]=="H"].iloc[0]["Y_centre_boiteREF_apres_empilement"]
                        premiere_valeur_basse = self.df.iloc[numero_REF+1:].loc[self.df["orient_BH"]=="B"].iloc[0]["Y_centre_boiteREF_apres_empilement"]
                        liste_hauteur_disponible_G[numero_REF] = premiere_valeur_haute-premiere_valeur_basse
                    liste_espace_pris_par_boite_G = np.cumsum(liste_hauteur)
                    liste_espace_pris_par_boite_G = [hauteur_cumsum+(numero_REF)*dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto] for numero_REF,hauteur_cumsum in enumerate(liste_espace_pris_par_boite_G)]
                    #Définition largeur prises par l'ensemble des boites déplacées
                    for numero_REF in range(nombre_boite_a_deplacer_G-1,len(liste_REF)):
                        if liste_espace_pris_par_boite_G[numero_REF]<liste_hauteur_disponible_G[numero_REF]:
                            numero_boite_a_bouger_max = numero_REF+1
                            for numero_boite in range(0,numero_boite_a_bouger_max):
                                self.df.loc[numero_boite,"replacement"] = "portrait"
                            #Si y pas la place, on fait rien, et on découpe le CUSTOM en éléments plus petits
                            break
        return self

    def actualisation_hauteur_et_largeur_boites_normales_qui_depassent(self,df_info_CUSTOM):
        if self.orientation=='normal':
            if (df_info_CUSTOM['orient_CUSTOM'] =='portrait' and self.orientation=='normal'):
                self.df.loc[self.df['replacement']=="paysage","hauteur_boite_complete"] = self.df["taille_hauteur_boite_biais"]
                self.df.loc[self.df['replacement']=="paysage","largeur_boite_complete"] = self.df["taille_largeur_boite_biais"]
            if (df_info_CUSTOM['orient_CUSTOM'] =='paysage' and self.orientation=='normal'):
                self.df.loc[self.df['replacement']=="portrait","hauteur_boite_complete"] = self.df["taille_hauteur_boite_droit"]
                self.df.loc[self.df['replacement']=="portrait","largeur_boite_complete"] = self.df["taille_largeur_boite_droit"]
        return self

    def calcul_valeur_limite_si_boite_a_replacer(self,df_info_CUSTOM):
        ###Replacement boite
        if len(self.df)>0 and self.orientation=="normal":
            if (df_info_CUSTOM['orient_CUSTOM'] =='portrait' and self.orientation=='normal' and df_info_CUSTOM["boite_a_replacer"] == True):
                #BAS
                if len(self.df[(self.df["orient_BH"]=="B") & (self.df["replacement"]=='paysage')])>0:
                    if len(self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="D")])>0:
                        limite_x_droite_boite_basse = self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="D")].iloc[0]["X_centre_boiteREF_apres_empilement"]
                        df_info_CUSTOM["limite_x_droite_boite_basse"] = limite_x_droite_boite_basse
                    else:
                        df_info_CUSTOM["limite_x_droite_boite_basse"] = df_info_CUSTOM['max_x_CUSTOM']

                    if len(self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="G")])>0:
                        limite_x_gauche_boite_basse = self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="G")].iloc[0]["X_centre_boiteREF_apres_empilement"]
                        df_info_CUSTOM["limite_x_gauche_boite_basse"] = limite_x_gauche_boite_basse
                    else:
                        df_info_CUSTOM["limite_x_gauche_boite_basse"] = df_info_CUSTOM['min_x_CUSTOM']

                    if len(self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="D")])>0:
                        limite_y_droite_boite_basse = self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="D")].iloc[0]["Y_centre_boiteREF_apres_empilement"]
                        df_info_CUSTOM["limite_y_droite_boite_basse"] = limite_y_droite_boite_basse
                    else:
                        df_info_CUSTOM["limite_y_droite_boite_basse"] = df_info_CUSTOM['min_y_CUSTOM']

                    if len(self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="G")])>0:
                        limite_y_gauche_boite_basse = self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="G")].iloc[0]["Y_centre_boiteREF_apres_empilement"]
                        df_info_CUSTOM["limite_y_gauche_boite_basse"] = limite_y_gauche_boite_basse
                    else:
                        df_info_CUSTOM["limite_y_gauche_boite_basse"] = df_info_CUSTOM['min_y_CUSTOM']

                #HAUT
                if len(self.df[(self.df["orient_BH"]=="H") & (self.df["replacement"]=='paysage')])>0:
                    if len(self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="D")])>0:
                        limite_x_droite_boite_haut = self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="D")].iloc[-1]["X_centre_boiteREF_apres_empilement"]
                        df_info_CUSTOM["limite_x_droite_boite_haut"] = limite_x_droite_boite_haut
                    else:
                        df_info_CUSTOM["limite_x_droite_boite_haut"] = df_info_CUSTOM['max_x_CUSTOM']

                    if len(self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="G")])>0:
                        limite_x_gauche_boite_haut = self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="G")].iloc[-1]["X_centre_boiteREF_apres_empilement"]
                        df_info_CUSTOM["limite_x_gauche_boite_haut"] = limite_x_gauche_boite_haut
                    else:
                        df_info_CUSTOM["limite_x_gauche_boite_haut"] = df_info_CUSTOM['max_x_CUSTOM']

                    if len(self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="D")])>0:
                        limite_y_droite_boite_haut = self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="D")].iloc[-1]["Y_centre_boiteREF_apres_empilement"]
                        df_info_CUSTOM["limite_y_droite_boite_haut"] = limite_y_droite_boite_haut
                    else:
                        df_info_CUSTOM["limite_y_droite_boite_haut"] = df_info_CUSTOM['max_y_CUSTOM']

                    if len(self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="G")])>0:
                        limite_y_droite_boite_haut = self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="G")].iloc[-1]["Y_centre_boiteREF_apres_empilement"]
                        df_info_CUSTOM["limite_y_droite_boite_haut"] = limite_y_droite_boite_haut
                    else:
                        df_info_CUSTOM["limite_y_droite_boite_haut"] = df_info_CUSTOM['max_y_CUSTOM']

            if (df_info_CUSTOM['orient_CUSTOM'] =='paysage' and self.orientation=='normal' and df_info_CUSTOM["boite_a_replacer"] == True):
                #DROITE
                if len(self.df[(self.df["orient_GD"]=="D") & (self.df["replacement"]=='portrait')])>0:
                    limite_y_haute_boite_droite = self.df[(self.df["replacement"]!="portrait")&(self.df["orient_BH"]=="H")].iloc[-1]["Y_centre_boiteREF_apres_empilement"]
                    df_info_CUSTOM["limite_y_haute_boite_droite"] = limite_y_haute_boite_droite
                    limite_y_basse_boite_droite = self.df[(self.df["replacement"]!="portrait")&(self.df["orient_BH"]=="B")].iloc[-1]["Y_centre_boiteREF_apres_empilement"]
                    df_info_CUSTOM["limite_y_basse_boite_droite"] = limite_y_basse_boite_droite

                    limite_x_haute_boite_droite = self.df[(self.df["replacement"]!="portrait")&(self.df["orient_BH"]=="H")].iloc[-1]["X_centre_boiteREF_apres_empilement"]
                    df_info_CUSTOM["limite_x_haute_boite_droite"] = limite_x_haute_boite_droite
                    limite_x_basse_boite_droite = self.df[(self.df["replacement"]!="portrait")&(self.df["orient_BH"]=="B")].iloc[-1]["X_centre_boiteREF_apres_empilement"]
                    df_info_CUSTOM["limite_x_basse_boite_droite"] = limite_x_basse_boite_droite

                #GAUCHE
                if len(self.df[(self.df["orient_GD"]=="G") & (self.df["replacement"]=='portrait')])>0:
                    limite_y_haute_boite_gauche = self.df[(self.df["replacement"]!="portrait")&(self.df["orient_BH"]=="H")].iloc[0]["Y_centre_boiteREF_apres_empilement"]
                    df_info_CUSTOM["limite_y_haute_boite_gauche"] = limite_y_haute_boite_gauche
                    limite_y_basse_boite_gauche = self.df[(self.df["replacement"]!="portrait")&(self.df["orient_BH"]=="B")].iloc[0]["Y_centre_boiteREF_apres_empilement"]
                    df_info_CUSTOM["limite_y_basse_boite_gauche"] = limite_y_basse_boite_gauche

                    limite_x_haute_boite_gauche = self.df[(self.df["replacement"]!="portrait")&(self.df["orient_BH"]=="H")].iloc[0]["X_centre_boiteREF_apres_empilement"]
                    df_info_CUSTOM["limite_x_haute_boite_gauche"] = limite_x_haute_boite_gauche
                    limite_x_basse_boite_gauche = self.df[(self.df["replacement"]!="portrait")&(self.df["orient_BH"]=="B")].iloc[0]["X_centre_boiteREF_apres_empilement"]
                    df_info_CUSTOM["limite_x_basse_boite_gauche"] = limite_x_basse_boite_gauche
        return self

    def calcul_limite_boites_extremitees(self,df_info_CUSTOM):
        ###Replacement boite
        if len(self.df)>0 and self.orientation=="normal" and df_info_CUSTOM["boite_a_replacer"] == True:
            #Portrait
            if (df_info_CUSTOM['orient_CUSTOM'] =='portrait' and self.orientation=='normal' and df_info_CUSTOM["boite_a_replacer"] == True):
                #X sur les boites hautes
                self.df = self.df.sort_values(by=["X_centre_boiteREF_apres_empilement"])
                if len(self.df[(self.df["replacement"]=="paysage")&(self.df["orient_GD"]=="G")&(self.df["orient_BH"]=="H")])>0:
                    limite_x_milieu_boite_superieure_gauche = self.df[(self.df["replacement"]=="paysage")&(self.df["orient_GD"]=="G")&(self.df["orient_BH"]=="H")].iloc[0]["X_centre_boiteREF_apres_empilement"]
                    df_info_CUSTOM["limite_x_milieu_boite_superieure_gauche"] = min([limite_x_milieu_boite_superieure_gauche,df_info_CUSTOM['min_x_CUSTOM']-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])
                if len(self.df[(self.df["replacement"]=="paysage")&(self.df["orient_GD"]=="D")&(self.df["orient_BH"]=="H")])>0:
                    limite_x_milieu_boite_superieure_droite = self.df[(self.df["replacement"]=="paysage")&(self.df["orient_GD"]=="D")&(self.df["orient_BH"]=="H")].iloc[-1]["X_centre_boiteREF_apres_empilement"]
                    df_info_CUSTOM["limite_x_milieu_boite_superieure_droite"] = max([limite_x_milieu_boite_superieure_droite,df_info_CUSTOM['max_x_CUSTOM']+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])
                #X sur les boites basses
                if len(self.df[(self.df["replacement"]=="paysage")&(self.df["orient_GD"]=="G")&(self.df["orient_BH"]=="B")])>0:
                    limite_x_milieu_boite_inferieure_gauche = self.df[(self.df["replacement"]=="paysage")&(self.df["orient_GD"]=="G")&(self.df["orient_BH"]=="B")].iloc[0]["X_centre_boiteREF_apres_empilement"]
                    df_info_CUSTOM["limite_x_milieu_boite_inferieure_gauche"] = min([limite_x_milieu_boite_inferieure_gauche,df_info_CUSTOM['min_x_CUSTOM']-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])
                if len(self.df[(self.df["replacement"]=="paysage")&(self.df["orient_GD"]=="D")&(self.df["orient_BH"]=="B")])>0:
                    limite_x_milieu_boite_inferieure_droite = self.df[(self.df["replacement"]=="paysage")&(self.df["orient_GD"]=="D")&(self.df["orient_BH"]=="B")].iloc[-1]["X_centre_boiteREF_apres_empilement"]
                    df_info_CUSTOM["limite_x_milieu_boite_inferieure_droite"] = max([limite_x_milieu_boite_inferieure_droite,df_info_CUSTOM['max_x_CUSTOM']+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])

                #Y sur les boites qui depassent é DROITE
                if len(self.df[(self.df["orient_GD"]=="D") & (self.df["replacement"]!="paysage")])>0:
                    self.df = self.df.sort_values(by=["Y_centre_boiteREF_apres_empilement"],ascending=False)
                    if len(self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="D")])>0:
                        limite_y_milieu_boite_superieure_droite = self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="D")].iloc[0]["Y_centre_boiteREF_apres_empilement"]+self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="D")].iloc[0]["taille_hauteur_boite_droit"]/2+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                        df_info_CUSTOM["limite_y_milieu_boite_superieure_droite"] = max([limite_y_milieu_boite_superieure_droite,df_info_CUSTOM['max_y_CUSTOM']+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])
                        limite_y_milieu_boite_inferieure_droite = self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="D")].iloc[-1]["Y_centre_boiteREF_apres_empilement"]-self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="D")].iloc[-1]["taille_hauteur_boite_droit"]/2-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                        df_info_CUSTOM["limite_y_milieu_boite_inferieure_droite"] = min([limite_y_milieu_boite_inferieure_droite,df_info_CUSTOM['min_y_CUSTOM']-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])
                #Y sur les boites qui depassent é GAUCHE
                if len(self.df[(self.df["orient_GD"]=="G") & (self.df["replacement"]!="paysage")])>0:
                    self.df = self.df.sort_values(by=["Y_centre_boiteREF_apres_empilement"],ascending=False)
                    if len(self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="G")])>0:
                        limite_y_milieu_boite_superieure_gauche = self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="G")].iloc[0]["Y_centre_boiteREF_apres_empilement"]+self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="G")].iloc[0]["taille_hauteur_boite_droit"]/2+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                        df_info_CUSTOM["limite_y_milieu_boite_superieure_gauche"] = max([limite_y_milieu_boite_superieure_gauche,df_info_CUSTOM['max_y_CUSTOM']+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])
                        limite_y_milieu_boite_inferieure_gauche = self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="G")].iloc[-1]["Y_centre_boiteREF_apres_empilement"]-self.df[(self.df["replacement"]!="paysage")&(self.df["orient_GD"]=="G")].iloc[-1]["taille_hauteur_boite_droit"]/2-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                        df_info_CUSTOM["limite_y_milieu_boite_inferieure_gauche"] = min([limite_y_milieu_boite_inferieure_gauche,df_info_CUSTOM['min_y_CUSTOM']-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])
                
            #Paysage
            if (df_info_CUSTOM['orient_CUSTOM'] =='paysage' and self.orientation=='normal' and df_info_CUSTOM["boite_a_replacer"] == True):
                #X sur les boites hautes
                self.df = self.df.sort_values(by=["X_centre_boiteREF_apres_empilement"])
                if len(self.df[(self.df["replacement"]!="portrait")&(self.df["orient_BH"]=="H")])>0:
                    gdf_boite_haute = self.df[(self.df["replacement"]!="portrait")&(self.df["orient_BH"]=="H")]
                    limite_x_milieu_boite_superieure_gauche = gdf_boite_haute.iloc[0]["X_centre_boiteREF_apres_empilement"] - gdf_boite_haute.iloc[0]["taille_largeur_boite_biais"]/2
                    df_info_CUSTOM["limite_x_milieu_boite_superieure_gauche"] = min([limite_x_milieu_boite_superieure_gauche,df_info_CUSTOM['min_x_CUSTOM']-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])
                    limite_x_milieu_boite_superieure_droite = gdf_boite_haute.iloc[-1]["X_centre_boiteREF_apres_empilement"] + gdf_boite_haute.iloc[-1]["taille_largeur_boite_biais"]/2
                    df_info_CUSTOM["limite_x_milieu_boite_superieure_droite"] = max([limite_x_milieu_boite_superieure_droite,df_info_CUSTOM['max_x_CUSTOM']+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])
                #X sur les boites basses
                if len(self.df[(self.df["replacement"]!="portrait")&(self.df["orient_BH"]=="B")])>0:
                    gdf_boite_basse = self.df[(self.df["replacement"]!="portrait")&(self.df["orient_BH"]=="B")]
                    limite_x_milieu_boite_inferieure_gauche = gdf_boite_basse.iloc[0]["X_centre_boiteREF_apres_empilement"] - gdf_boite_basse.iloc[0]["taille_largeur_boite_biais"]/2
                    df_info_CUSTOM["limite_x_milieu_boite_inferieure_gauche"] = min([limite_x_milieu_boite_inferieure_gauche,df_info_CUSTOM['min_x_CUSTOM']-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])
                    limite_x_milieu_boite_inferieure_droite = gdf_boite_basse.iloc[-1]["X_centre_boiteREF_apres_empilement"] + gdf_boite_basse.iloc[-1]["taille_largeur_boite_biais"]/2
                    df_info_CUSTOM["limite_x_milieu_boite_inferieure_droite"] = max([limite_x_milieu_boite_inferieure_droite,df_info_CUSTOM['max_x_CUSTOM']+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])

                #Y sur les boites qui depassent é DROITE
                if len(self.df[(self.df["orient_GD"]=="D") & (self.df["replacement"]=='portrait')])>0:
                    self.df = self.df.sort_values(by=["Y_centre_boiteREF_apres_empilement"],ascending=False)
                    if len(self.df[(self.df["replacement"]=="portrait")&(self.df["orient_GD"]=="D")])>0:
                        limite_y_milieu_boite_superieure_droite = self.df[(self.df["replacement"]=="portrait")&(self.df["orient_GD"]=="D")].iloc[0]["Y_centre_boiteREF_apres_empilement"]+self.df[(self.df["replacement"]=="portrait")&(self.df["orient_GD"]=="D")].iloc[0]["taille_hauteur_boite_biais"]/2+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                        df_info_CUSTOM["limite_y_milieu_boite_superieure_droite"] = max([limite_y_milieu_boite_superieure_droite,df_info_CUSTOM['max_y_CUSTOM']+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])
                        limite_y_milieu_boite_inferieure_droite = self.df[(self.df["replacement"]=="portrait")&(self.df["orient_GD"]=="D")].iloc[-1]["Y_centre_boiteREF_apres_empilement"]-self.df[(self.df["replacement"]=="portrait")&(self.df["orient_GD"]=="D")].iloc[-1]["taille_hauteur_boite_biais"]/2-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                        df_info_CUSTOM["limite_y_milieu_boite_inferieure_droite"] = min([limite_y_milieu_boite_inferieure_droite,df_info_CUSTOM['min_y_CUSTOM']-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])
                #Y sur les boites qui depassent é GAUCHE
                if len(self.df[(self.df["orient_GD"]=="G") & (self.df["replacement"]=='portrait')])>0:
                    self.df = self.df.sort_values(by=["Y_centre_boiteREF_apres_empilement"],ascending=False)
                    if len(self.df[(self.df["replacement"]=="portrait")&(self.df["orient_GD"]=="G")])>0:
                        limite_y_milieu_boite_superieure_gauche = self.df[(self.df["replacement"]=="portrait")&(self.df["orient_GD"]=="G")].iloc[0]["Y_centre_boiteREF_apres_empilement"]+self.df[(self.df["replacement"]=="portrait")&(self.df["orient_GD"]=="G")].iloc[0]["taille_hauteur_boite_biais"]/2+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                        df_info_CUSTOM["limite_y_milieu_boite_superieure_gauche"] = max([limite_y_milieu_boite_superieure_gauche,df_info_CUSTOM['max_y_CUSTOM']+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])
                        limite_y_milieu_boite_inferieure_gauche = self.df[(self.df["replacement"]=="portrait")&(self.df["orient_GD"]=="G")].iloc[-1]["Y_centre_boiteREF_apres_empilement"]-self.df[(self.df["replacement"]=="portrait")&(self.df["orient_GD"]=="G")].iloc[-1]["taille_hauteur_boite_biais"]/2-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                        df_info_CUSTOM["limite_y_milieu_boite_inferieure_gauche"] = min([limite_y_milieu_boite_inferieure_gauche,df_info_CUSTOM['min_y_CUSTOM']-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]])
        return self

    def replacement_boites_extremitees(self,df_info_CUSTOM):
        if len(self.df)>0 and self.orientation=="normal" and df_info_CUSTOM["boite_a_replacer"] == True:
            #Portrait
            if (df_info_CUSTOM['orient_CUSTOM'] =='portrait' and self.orientation=='normal'):
                ###Boites normales
                ###boite hautes droite
                filtre_boite = (self.df["orient_GD"] == "D") & (self.df["orient_BH"] == "H") & (self.df["replacement"]!="paysage")
                gdf_filtre = self.df[filtre_boite]
                if "limite_x_milieu_boite_superieure_droite" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["X_centre_boiteREF_apres_empilement"]<df_info_CUSTOM["limite_x_milieu_boite_superieure_droite"]),"X_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_x_milieu_boite_superieure_droite"]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre])
                ###boite hautes gauche
                filtre_boite = (self.df["orient_BH"] == "H") & (self.df["replacement"]!="paysage") & (self.df["orient_GD"] == "G")
                gdf_filtre = self.df[filtre_boite]
                if "limite_x_milieu_boite_superieure_gauche" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["X_centre_boiteREF_apres_empilement"]>df_info_CUSTOM["limite_x_milieu_boite_superieure_gauche"]),"X_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_x_milieu_boite_superieure_gauche"]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre])  
                ###boite basses droite
                filtre_boite = (self.df["orient_BH"] == "B") & (self.df["replacement"]!="paysage") & (self.df["orient_GD"] == "D")
                gdf_filtre = self.df[filtre_boite]
                if "limite_x_milieu_boite_inferieure_droite" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["X_centre_boiteREF_apres_empilement"]<df_info_CUSTOM["limite_x_milieu_boite_inferieure_droite"]),"X_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_x_milieu_boite_inferieure_droite"]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre])
                ###boite basses gauche
                filtre_boite = (self.df["orient_BH"] == "B") & (self.df["replacement"]!="paysage") & (self.df["orient_GD"] == "G")
                gdf_filtre = self.df[filtre_boite]
                if "limite_x_milieu_boite_inferieure_gauche" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["X_centre_boiteREF_apres_empilement"]>df_info_CUSTOM["limite_x_milieu_boite_inferieure_gauche"]),"X_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_x_milieu_boite_inferieure_gauche"]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre]) 

                ###Boites qui depassent
                ###boite qui depassent haut droite
                filtre_boite = (self.df["orient_BH"] == "H") & (self.df["replacement"]=="paysage") & (self.df["orient_GD"] == "D")
                gdf_filtre = self.df[filtre_boite]
                if "limite_y_milieu_boite_superieure_droite" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["Y_centre_boiteREF_apres_empilement"]<df_info_CUSTOM["limite_y_milieu_boite_superieure_droite"]),"Y_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_y_milieu_boite_superieure_droite"]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre])
                ###boite qui depassent bas droite
                filtre_boite = (self.df["orient_BH"] == "B") & (self.df["replacement"]=="paysage") & (self.df["orient_GD"] == "D")
                gdf_filtre = self.df[filtre_boite]
                if "limite_y_milieu_boite_inferieure_droite" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["Y_centre_boiteREF_apres_empilement"]>df_info_CUSTOM["limite_y_milieu_boite_inferieure_droite"]),"Y_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_y_milieu_boite_inferieure_droite"]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre])      
                ###boite qui depassent haut gauche
                filtre_boite = (self.df["orient_BH"] == "H") & (self.df["replacement"]=="paysage") & (self.df["orient_GD"] == "G")
                gdf_filtre = self.df[filtre_boite]
                if "limite_y_milieu_boite_superieure_gauche" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["Y_centre_boiteREF_apres_empilement"]<df_info_CUSTOM["limite_y_milieu_boite_superieure_gauche"]),"Y_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_y_milieu_boite_superieure_gauche"]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre])
                ###boite qui depassent bas gauche
                filtre_boite = (self.df["orient_BH"] == "B") & (self.df["replacement"]=="paysage") & (self.df["orient_GD"] == "G")
                gdf_filtre = self.df[filtre_boite]
                if "limite_y_milieu_boite_inferieure_gauche" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["Y_centre_boiteREF_apres_empilement"]>df_info_CUSTOM["limite_y_milieu_boite_inferieure_gauche"]),"Y_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_y_milieu_boite_inferieure_gauche"]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre])

            #Paysage
            if (df_info_CUSTOM['orient_CUSTOM'] =='paysage' and self.orientation=='normal'):
                ###Boites normales
                ###boite hautes droite
                filtre_boite = (self.df["orient_BH"] == "H") & (self.df["replacement"]!="portrait") & (self.df["orient_GD"] == "D")
                gdf_filtre = self.df[filtre_boite]
                if "limite_y_milieu_boite_superieure_droite" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["Y_centre_boiteREF_apres_empilement"]<df_info_CUSTOM["limite_y_milieu_boite_superieure_droite"]),"Y_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_y_milieu_boite_superieure_droite"]+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre])
                ###boite hautes gauche
                filtre_boite = (self.df["orient_BH"] == "H") & (self.df["replacement"]!="portrait") & (self.df["orient_GD"] == "G")
                gdf_filtre = self.df[filtre_boite]
                if "limite_y_milieu_boite_superieure_gauche" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["Y_centre_boiteREF_apres_empilement"]<df_info_CUSTOM["limite_y_milieu_boite_superieure_gauche"]),"Y_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_y_milieu_boite_superieure_gauche"]+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre])    
                ###boite basses droite

                filtre_boite = (self.df["orient_BH"] == "B") & (self.df["replacement"]!="portrait") & (self.df["orient_GD"] == "D")
                gdf_filtre = self.df[filtre_boite]
                if "limite_y_milieu_boite_inferieure_droite" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["Y_centre_boiteREF_apres_empilement"]>df_info_CUSTOM["limite_y_milieu_boite_inferieure_droite"]),"Y_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_y_milieu_boite_inferieure_droite"]-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre])
                ###boite basses gauche
                filtre_boite = (self.df["orient_BH"] == "B") & (self.df["replacement"]!="portrait") & (self.df["orient_GD"] == "G")
                gdf_filtre = self.df[filtre_boite]
                if "limite_y_milieu_boite_inferieure_gauche" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["Y_centre_boiteREF_apres_empilement"]>df_info_CUSTOM["limite_y_milieu_boite_inferieure_gauche"]),"Y_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_y_milieu_boite_inferieure_gauche"]-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre]) 

                ###Boites qui depassent
                ###boite qui depassent haut droite
                filtre_boite = (self.df["orient_BH"] == "H") & (self.df["replacement"]=="portrait") & (self.df["orient_GD"] == "D")
                gdf_filtre = self.df[filtre_boite]
                if "limite_x_milieu_boite_superieure_droite" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["X_centre_boiteREF_apres_empilement"]<df_info_CUSTOM["limite_x_milieu_boite_superieure_droite"]),"X_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_x_milieu_boite_superieure_droite"]+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre])
                ###boite qui depassent bas droite
                filtre_boite = (self.df["orient_BH"] == "B") & (self.df["replacement"]=="portrait") & (self.df["orient_GD"] == "D")
                gdf_filtre = self.df[filtre_boite]
                if "limite_x_milieu_boite_inferieure_droite" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["X_centre_boiteREF_apres_empilement"]<df_info_CUSTOM["limite_x_milieu_boite_inferieure_droite"]),"X_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_x_milieu_boite_inferieure_droite"]+dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre])      
                ###boite qui depassent haut gauche
                filtre_boite = (self.df["orient_BH"] == "H") & (self.df["replacement"]=="portrait") & (self.df["orient_GD"] == "G")
                gdf_filtre = self.df[filtre_boite]
                if "limite_x_milieu_boite_superieure_gauche" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["X_centre_boiteREF_apres_empilement"]>df_info_CUSTOM["limite_x_milieu_boite_superieure_gauche"]),"X_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_x_milieu_boite_superieure_gauche"]-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre])
                ###boite qui depassent bas gauche
                filtre_boite = (self.df["orient_BH"] == "B") & (self.df["replacement"]=="portrait") & (self.df["orient_GD"] == "G")
                gdf_filtre = self.df[filtre_boite]
                if "limite_x_milieu_boite_inferieure_gauche" in df_info_CUSTOM:
                    gdf_filtre.loc[(gdf_filtre["X_centre_boiteREF_apres_empilement"]>df_info_CUSTOM["limite_x_milieu_boite_inferieure_gauche"]),"X_centre_boiteREF_apres_empilement"]=df_info_CUSTOM["limite_x_milieu_boite_inferieure_gauche"]-dict_config_espace['espace_sous_boite_complete'][self.taille_globale_carto]
                self.df = self.df[~filtre_boite]
                self.df = pd.concat([self.df,gdf_filtre])
        return self


    def creation_point_unique_par_REF(self,df_info_CUSTOM):
        if self.orientation=='normal':
            if len(self.df)>0:
                self.df = self.df.drop(['geometry_ligne_inter_buffer','liste_point_intersection'],axis=1)
                if (df_info_CUSTOM['orient_CUSTOM'] =='portrait' and self.orientation=='normal'):
                    self.df['geometry_point_interception'] = gpd.points_from_xy(self.df["X_centre_boiteREF_apres_empilement"],self.df['Y_centre_boiteREF' + '_apres_empilement'])
                if (df_info_CUSTOM['orient_CUSTOM'] =='paysage' and self.orientation=='normal'):
                    self.df['geometry_point_interception'] = gpd.points_from_xy(self.df['X_centre_boiteREF_apres_empilement'],self.df["Y_centre_boiteREF_apres_empilement"])
                self.df = self.df.set_geometry('geometry_point_interception')
        #self.df.to_file("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/test/essai_points.shp")        
        return self


    def definition_point_ancrage_eventuel_boite_orthogonal(self,df_info_CUSTOM):
        if self.orientation=='orthogonal':
            if df_info_CUSTOM['cartouche_boite_ortho_separe']==False:
                self.df["tempo_x"] = 0
                self.df["tempo_y"] = 0
                self.df['geometry_point_interception'] = gpd.points_from_xy(self.df.tempo_x, self.df.tempo_y)
                self.df = self.df.set_geometry('geometry_point_interception')
                self.df["gauche_boite_complete"] = 0
                self.df["droite_boite_complete"] = self.df["taille_largeur_boite_droit"]
                self.df["bas_boite_complete"] = 0
                self.df["haut_boite_complete"] = self.df["taille_hauteur_boite_droit"]
        return self

    def actualisation_bas_haut_gauche_droite(self):
        if len(self.df)>0:
            self.df = self.df.set_geometry('geometry_point_interception')
            #Gauche
            self.df.loc[self.df['type_placement_boite_final']=='G','haut_boite_complete'] = self.df['geometry_point_interception'].y+self.df['taille_hauteur_boite_droit']/2
            self.df.loc[self.df['type_placement_boite_final']=='G','bas_boite_complete'] = self.df['geometry_point_interception'].y-self.df['taille_hauteur_boite_droit']/2
            self.df.loc[self.df['type_placement_boite_final']=='G','gauche_boite_complete'] = self.df['geometry_point_interception'].x-self.df['taille_largeur_boite_droit']
            self.df.loc[self.df['type_placement_boite_final']=='G','droite_boite_complete'] = self.df['geometry_point_interception'].x

            #Droite
            self.df.loc[self.df['type_placement_boite_final']=='D','haut_boite_complete'] = self.df['geometry_point_interception'].y+self.df['taille_hauteur_boite_droit']/2
            self.df.loc[self.df['type_placement_boite_final']=='D','bas_boite_complete'] = self.df['geometry_point_interception'].y-self.df['taille_hauteur_boite_droit']/2
            self.df.loc[self.df['type_placement_boite_final']=='D','gauche_boite_complete'] = self.df['geometry_point_interception'].x
            self.df.loc[self.df['type_placement_boite_final']=='D','droite_boite_complete'] = self.df['geometry_point_interception'].x+self.df['taille_largeur_boite_droit']

            #Haut
            self.df.loc[self.df['type_placement_boite_final']=='H','haut_boite_complete'] = self.df['geometry_point_interception'].y+self.df['taille_hauteur_boite_biais']
            self.df.loc[self.df['type_placement_boite_final']=='H','bas_boite_complete'] = self.df['geometry_point_interception'].y
            self.df.loc[self.df['type_placement_boite_final']=='H','gauche_boite_complete'] = self.df['geometry_point_interception'].x-self.df['taille_largeur_boite_biais']/2
            self.df.loc[self.df['type_placement_boite_final']=='H','droite_boite_complete'] = self.df['geometry_point_interception'].x+self.df['taille_largeur_boite_biais']/2

            #Bas
            self.df.loc[self.df['type_placement_boite_final']=='B','haut_boite_complete'] = self.df['geometry_point_interception'].y
            self.df.loc[self.df['type_placement_boite_final']=='B','bas_boite_complete'] = self.df['geometry_point_interception'].y-self.df['taille_hauteur_boite_biais']
            self.df.loc[self.df['type_placement_boite_final']=='B','gauche_boite_complete'] = self.df['geometry_point_interception'].x-self.df['taille_largeur_boite_biais']/2
            self.df.loc[self.df['type_placement_boite_final']=='B','droite_boite_complete'] = self.df['geometry_point_interception'].x+self.df['taille_largeur_boite_biais']/2

        return self

    def recuperation_bas_haut_gauche_droite_dans_df_contour(self):
        if len(self.df)>0:
            self.df_contour = pd.merge(self.df_contour,self.df[["CODE_REF",'haut_boite_complete','bas_boite_complete','gauche_boite_complete','droite_boite_complete']],on="CODE_REF")
        return self

    def ecartement_finale(self):
        self.df = DictBoiteComplete.creation_contour_simple(self.df)
        return self

    def actualisation_type_placement_boite_final(self,df_info_CUSTOM):
        if self.orientation=='normal':
            if len(self.df)>0:
                #On change l'orientation de toutes les boites é replacer sauf la premiere
                self.df.loc[self.df['replacement']=='paysage','type_placement_boite_final'] = self.df['orient_BH']
                self.df.loc[self.df['replacement']=='portrait','type_placement_boite_final'] = self.df['orient_GD']
        return self

    def actualisation_gauche_bas_droite_gauche_df_contour(self):
        self.df_contour = pd.concat([self.df_contour, self.df_contour.bounds], axis=1)
        self.df_contour.loc[self.df_contour['type_placement_boite_final'].isin(['G','D']),'haut_boite_complete'] = self.df_contour['maxy']
        self.df_contour.loc[self.df_contour['type_placement_boite_final'].isin(['G','D']),'bas_boite_complete'] = self.df_contour['miny']
        self.df_contour.loc[self.df_contour['type_placement_boite_final'].isin(['G','D']),'gauche_boite_complete'] = self.df_contour['minx']
        self.df_contour.loc[self.df_contour['type_placement_boite_final'].isin(['G','D']),'droite_boite_complete'] = self.df_contour['maxx']

        #Haut
        self.df_contour.loc[self.df_contour['type_placement_boite_final']=='H','haut_boite_complete'] = self.df_contour['miny']+self.df_contour['taille_hauteur_boite_biais']
        self.df_contour.loc[self.df_contour['type_placement_boite_final']=='H','bas_boite_complete'] = self.df_contour['miny']
        self.df_contour.loc[self.df_contour['type_placement_boite_final']=='H','gauche_boite_complete'] = self.df_contour['minx']
        self.df_contour.loc[self.df_contour['type_placement_boite_final']=='H','droite_boite_complete'] = self.df_contour['minx']+self.df_contour['taille_largeur_boite_biais']

        #Bas
        self.df_contour.loc[self.df_contour['type_placement_boite_final']=='B','haut_boite_complete'] = self.df_contour['maxy']
        self.df_contour.loc[self.df_contour['type_placement_boite_final']=='B','bas_boite_complete'] = self.df_contour['maxy']-self.df_contour['taille_hauteur_boite_biais']
        self.df_contour.loc[self.df_contour['type_placement_boite_final']=='B','gauche_boite_complete'] = self.df_contour['minx']
        self.df_contour.loc[self.df_contour['type_placement_boite_final']=='B','droite_boite_complete'] = self.df_contour['minx']+self.df_contour['taille_largeur_boite_biais']
        return self

    def decalage_contour_si_contact(self,type_boite_placement):
        for nom_boite_maitre,dict_boite_complete in self.items():
            if dict_boite_complete.orientation in type_boite_placement:
                dict_boite_complete.df_contour = dict_boite_complete.df_contour.sort_values(by="X_centre_boiteREF_apres_empilement")
                gdf_boite = dict_boite_complete.df_contour
                dict_boite = gdf_boite.to_dict('index')
                #juste pour dire que certains geom_boite se chevauchent
                #while any([x for xs in [gdf_boite['geom_boite'].overlaps(x) for x in gdf_boite['geom_boite'].to_list()] for x in xs])
                while any(any(x) for x in [gdf_boite['geom_boite'].overlaps(x) for x in gdf_boite['geom_boite'].to_list()])==True:
                    for index,boite in dict_boite.items():
                        if any(boite['geom_boite'].overlaps(gdf_boite['geom_boite']))==True:
                            if boite['type_placement_boite_final']=="G":
                                boite['geom_boite'] = translate(boite['geom_boite'],-2000,0)
                            if boite['type_placement_boite_final']=="D":
                                boite['geom_boite'] = translate(boite['geom_boite'],+2000,0)            
                            if boite['type_placement_boite_final']=="H":
                                boite['geom_boite'] = translate(boite['geom_boite'],0,+2000)
                            if boite['type_placement_boite_final']=="B":
                                boite['geom_boite'] = translate(boite['geom_boite'],0,-2000)
                            gdf_boite['geom_boite'] = [v['geom_boite'] for k,v in dict_boite.items()]
                            break
                dict_boite_complete.df_contour = gdf_boite
                dict_boite_complete = DictBoiteComplete.actualisation_gauche_bas_droite_gauche_df_contour(dict_boite_complete)

        return self
    
    def transfert_info_geom_dans_df(self,type_boite_placement):
        def actualisation_geometry_point_intereception(x):
            if x['type_placement_boite_final']=='G':
                x['geometry_point_interception'] = Point(x['droite_boite_complete'],(x['haut_boite_complete']+x['bas_boite_complete'])/2)
            if x['type_placement_boite_final']=='D':
                x['geometry_point_interception'] = Point(x['gauche_boite_complete'],(x['haut_boite_complete']+x['bas_boite_complete'])/2)
            if x['type_placement_boite_final']=='H':
                x['geometry_point_interception'] = Point((x['gauche_boite_complete']+x['droite_boite_complete'])/2,x['bas_boite_complete'])
            if x['type_placement_boite_final']=='B':
                x['geometry_point_interception'] = Point((x['gauche_boite_complete']+x['droite_boite_complete'])/2,x['haut_boite_complete'])               
            return x

        for nom_boite_maitre,dict_boite_complete in self.items():
            if dict_boite_complete.orientation in type_boite_placement:
                dict_boite_complete.df = dict_boite_complete.df[[x for x in list(dict_boite_complete.df) if x not in ["haut_boite_complete","bas_boite_complete","gauche_boite_complete","droite_boite_complete"]]]
                dict_boite_complete.df = pd.merge(dict_boite_complete.df,dict_boite_complete.df_contour[['CODE_REF',"haut_boite_complete","bas_boite_complete","gauche_boite_complete","droite_boite_complete"]],on='CODE_REF')
                dict_boite_complete.df = dict_boite_complete.df.apply(lambda x:actualisation_geometry_point_intereception(x),axis=1)
        return self
    
    def actualisation_haut_bas(self,type_boite_placement):
        for nom_boite_maitre,dict_boite_complete in self.items():
            if dict_boite_complete.orientation in type_boite_placement:
                #dict_boite_complete.df.to_file("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/test/point_inter_test.shp")
                dict_boite_complete.df.loc[dict_boite_complete.df["type_placement_boite_final"]=="H",'bas_boite_complete'] = dict_boite_complete.df['geometry_point_interception'].y
                dict_boite_complete.df.loc[dict_boite_complete.df["type_placement_boite_final"]=="H",'haut_boite_complete'] = dict_boite_complete.df['geometry_point_interception'].y + dict_boite_complete.df['hauteur_boite_complete']
                dict_boite_complete.df.loc[dict_boite_complete.df["type_placement_boite_final"]=="B",'haut_boite_complete'] = dict_boite_complete.df['geometry_point_interception'].y
                dict_boite_complete.df.loc[dict_boite_complete.df["type_placement_boite_final"]=="B",'bas_boite_complete'] = dict_boite_complete.df['geometry_point_interception'].y - dict_boite_complete.df['hauteur_boite_complete']
        return self

    ##########################################################################################
    #Placement interieur boite
    ##########################################################################################
    def ajout_info_point_interception_et_cote(self,type_boite_placement:list=['normal']):
        if self.orientation in type_boite_placement:
            for type_bloc,entite_bloc in self.items():
                entite_bloc.df = pd.merge(entite_bloc.df,self.df[["CODE_REF",'type_placement_boite_final','orient_BH','orient_GD','geometry_point_interception',"haut_boite_complete","bas_boite_complete","gauche_boite_complete","droite_boite_complete"]],on="CODE_REF")
        return self
    
    
    def creation_dict_hauteur_largeur_blocs_dans_meme_boite(self,type_boite_placement:list=['normal']):
        if self.orientation =="normal":
            #df_info_geom_boite = self.df[['CODE_REF','orient_BH','orient_GD','type_placement_boite_final','geometry_point_interception','haut_boite_complete','bas_boite_complete','gauche_boite_complete','droite_boite_complete']]
            df_info_geom_boite = self.df[['CODE_REF','orient_BH','orient_GD']]
        if self.orientation =="orthogonal":
            df_info_geom_boite = self.df[['CODE_REF']]
        if self.orientation in type_boite_placement:
            for type_bloc,entite_bloc in self.items():
                entite_bloc.df = pd.merge(entite_bloc.df,df_info_geom_boite,on='CODE_REF')
        return self

    def ajout_ecart_origine_et_numero_bloc(self,type_boite_placement:list=['normal']):
        if self.orientation in type_boite_placement:
            numero_bloc = 1
            for type_bloc,entite_bloc in self.items():
                entite_bloc.numero_bloc = numero_bloc
                numero_bloc = numero_bloc + 1
            for type_bloc,entite_bloc in self.items():
                if entite_bloc.numero_bloc == 1:
                    entite_bloc.df['ecart_hauteur_origine'] = 1
                    entite_bloc.df['ecart_largeur_origine'] = 1
                if entite_bloc.numero_bloc != 1:
                    numero_bloc_actuel = entite_bloc.numero_bloc
                    list_df_bloc_precedent = list({k:v.df for k,v in self.items() if v.numero_bloc<numero_bloc_actuel}.values())
                    df_tempo_bloc_precedent = pd.concat(list_df_bloc_precedent)
                    #En fait, ici, il faudraitn, dans l'idéal faire en fonction de l'orientation. Si un jour DORA devient célèbre, bon courage à toi Mr le programmeur :-P
                    df_tempo_bloc_precedent = df_tempo_bloc_precedent[['CODE_REF','taille_hauteur_bloc_droit']]
                    df_tempo_bloc_precedent = df_tempo_bloc_precedent.groupby('CODE_REF').agg({'taille_hauteur_bloc_droit':"sum"})
                    df_tempo_bloc_precedent['taille_hauteur_bloc_droit'] = df_tempo_bloc_precedent['taille_hauteur_bloc_droit'] +(numero_bloc_actuel-1)*dict_config_espace['espace_entre_bloc'][self.taille_globale_carto]
                    df_tempo_bloc_precedent= df_tempo_bloc_precedent.rename({"taille_hauteur_bloc_droit":"ecart_hauteur_origine"},axis=1)
                    df_tempo_bloc_precedent = df_tempo_bloc_precedent.reset_index()
                    entite_bloc.df = pd.merge(entite_bloc.df,df_tempo_bloc_precedent,on="CODE_REF")
        return self

    def placement_des_blocs_interieur_boite_complete(self,type_boite_placement:list=['normal']):
        #ATTENTION : Les blocs sont "déroulés" de haut en bas pour les blocs à gauche, à droite et en bas, mais du bas vers le haut pour les blocs en haut
        if self.orientation in type_boite_placement:
            for nom_bloc,dict_bloc in self.items():
                if dict_bloc.type=='bloc_texte_simple':
                    dict_bloc = BlocTexteSimple.placement_bloc_texte_simple_dans_boite(dict_bloc)
                if dict_bloc.type=='bloc_icone':
                    dict_bloc = BlocIcone.placement_bloc_icone_dans_boite(dict_bloc)
                if dict_bloc.type=='bloc_lignes_multiples':
                    dict_bloc = BlocLignesMultiples.placement_bloc_lm_dans_boite(dict_bloc)
        return self

    def placement_objets_interieur_blocs(self,type_boite_placement:list=['normal']):
        if self.orientation in type_boite_placement:
            for nom_bloc,dict_bloc in self.items():
                if dict_bloc.type=='bloc_texte_simple':
                    dict_bloc = BlocTexteSimple.placement_texte_simple_dans_bloc_texte_simple(dict_bloc)
                if dict_bloc.type=='bloc_icone':
                    dict_bloc = BlocIcone.placement_icones_indiv_dans_bloc_icone(dict_bloc)
                if dict_bloc.type=='bloc_lignes_multiples':
                    dict_bloc = BlocLignesMultiples.placement_point_icone_dans_bloc_lm(dict_bloc)
        return self
    
    def ajout_colonne_pour_orientation_et_alignement_objet(self):
        dict_alignement = {'G': "Right", 'D': "Left",'H': "Follow",'B': "Follow"}
        for type_bloc,contenu_bloc in self.items():
            #Gauche
            contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='G','Quadrant'] = "3"
            contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='G','sens'] = 'droit'
            contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='G','alignement'] = 'G'

            #Droite
            contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='D','Quadrant'] = "5"
            contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='D','sens'] = 'droit'
            contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='D','alignement'] = 'D'

            #Haut
            contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='H','Quadrant'] = "2"
            contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='H','sens'] = 'biais'
            contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='H','alignement'] = 'H'

            #Bas
            contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='B','Quadrant'] = "0"
            contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='B','sens'] = 'biais'
            contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='B','alignement'] = 'B'

            contenu_bloc.df = contenu_bloc.df.replace({'alignement': dict_alignement})

            if contenu_bloc.type=='bloc_texte_simple':
                pass
            if contenu_bloc.type=='bloc_icone':
                pass
            if contenu_bloc.type=='bloc_lignes_multiples':
                contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='G','xallmind'] = (-1)*dict_config_espace['alineaX_point_lm_et_phrase_lm_portrait'][self.taille_globale_carto]
                contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='G','angle'] = dict_config_espace['angle_rotation_lm_portrait'][self.taille_globale_carto]
                contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='D','xallmind'] = dict_config_espace['alineaX_point_lm_et_phrase_lm_portrait'][self.taille_globale_carto]
                contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='D','angle'] = dict_config_espace['angle_rotation_lm_portrait'][self.taille_globale_carto]
                contenu_bloc.df.loc[(contenu_bloc.df['type_placement_boite_final']=='D')|(contenu_bloc.df['type_placement_boite_final']=='G'),'yallmind'] = 0

                contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='H','yallmind'] = -dict_config_espace['alineaY_point_lm_et_phrase_lm_paysage'][self.taille_globale_carto]
                contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='H','angle'] = dict_config_espace['angle_rotation_lm_paysage'][self.taille_globale_carto]
                contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='H','xallmind'] = dict_config_espace['alineaX_point_lm_et_phrase_lm_paysage_haut'][self.taille_globale_carto]
                contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='B','yallmind'] = dict_config_espace['alineaY_point_lm_et_phrase_lm_paysage'][self.taille_globale_carto]
                contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='B','angle'] = 360-dict_config_espace['angle_rotation_lm_paysage'][self.taille_globale_carto]
                contenu_bloc.df.loc[contenu_bloc.df['type_placement_boite_final']=='B','xallmind'] = dict_config_espace['alineaX_point_lm_et_phrase_lm_paysage_bas'][self.taille_globale_carto]
                contenu_bloc.df['al_lm_ind'] = contenu_bloc.df['xallmind'].astype(str) + "," + contenu_bloc.df['yallmind'].astype(str)        
        return self

    def transfert_info_df_vers_df_indiv(self):
        for type_bloc,contenu_bloc in self.items():
            if contenu_bloc.type == "bloc_lignes_multiples":
                list_col_a_transferer = ['id_atlas','angle','al_lm_ind','Quadrant','sens','alignement']
                contenu_bloc.df_indiv = pd.merge(contenu_bloc.df_indiv,contenu_bloc.df[["CODE_REF"]+list_col_a_transferer],on="CODE_REF")
        return self

    def conversion_colonne_hauteur_largeur_boite_complete_vers_bloc(self,type_boite_placement:list=['normal']):
        if self.orientation in type_boite_placement:
            for nom_bloc,dict_bloc in self.items():
                dict_bloc = Bloc.conversion_hauteur_largeur_boite_complete_to_bloc(dict_bloc)
        return self

    def placement_bloc_texte_dans_boite(self,dict_dict_info_CUSTOM):
        for nom_bloc,dico_boite in self.items():
            dico_boite.placement_bloc_texte(dict_dict_info_CUSTOM)
        for nom_bloc,dico_boite in self.items():
            dico_boite.actualisation_point_geometry_bloc_texte()
        return self
    
    ##########################################################################################
    #PARTIE placement boite ortho
    ##########################################################################################
    def placement_boite_ortho(self,dict_info_CUSTOM,contenu_CUSTOM):
        list_df_contour_boite_normal = [v.df_contour for k,v in contenu_CUSTOM.items() if v.orientation=="normal"]
        if len(list_df_contour_boite_normal)>0:
            df_contour_boite_normal = list_df_contour_boite_normal[0]
        
        haut_CUSTOM = max([dict_info_CUSTOM['max_y_CUSTOM'],max(df_contour_boite_normal['haut_boite_complete'].to_list())])
        bas_CUSTOM = min([dict_info_CUSTOM['min_y_CUSTOM'],min(df_contour_boite_normal['bas_boite_complete'].to_list())])
        gauche_CUSTOM = min([dict_info_CUSTOM['min_x_CUSTOM'],min(df_contour_boite_normal['gauche_boite_complete'].to_list())])
        droite_CUSTOM = max([dict_info_CUSTOM['max_x_CUSTOM'],max(df_contour_boite_normal['droite_boite_complete'].to_list())])          
        espace_esthetique = (haut_CUSTOM - bas_CUSTOM)*0.02

        hauteur_boite_ortho = self.df_contour['taille_hauteur_boite_droit'].iloc[0]
        largeur_boite_ortho = self.df_contour['taille_largeur_boite_droit'].iloc[0]            
        if dict_info_CUSTOM['orient_CUSTOM']=="portrait" or dict_info_CUSTOM['orient_CUSTOM']=="paysage":
            
            dict_tempo_decalage = {}
            #On essaie de placer la boite en haut à gauche ou en bas à gauche. Puis on ecarte vers la gauche
            Essai_boite_haut_gauche = Polygon([(gauche_CUSTOM, haut_CUSTOM), (gauche_CUSTOM+largeur_boite_ortho, haut_CUSTOM), (gauche_CUSTOM+largeur_boite_ortho, haut_CUSTOM-hauteur_boite_ortho), (gauche_CUSTOM, haut_CUSTOM-hauteur_boite_ortho)])
            Essai_boite_haut_gauche = translate(Essai_boite_haut_gauche,0,-espace_esthetique)
            nb_decalage_haut_gauche = 0
            while any(df_contour_boite_normal.overlaps(Essai_boite_haut_gauche)):
                Essai_boite_haut_gauche = translate(Essai_boite_haut_gauche,-200)
                nb_decalage_haut_gauche = nb_decalage_haut_gauche+1
            #Encore un petit coup pour l'esthetique
            Essai_boite_haut_gauche = translate(Essai_boite_haut_gauche,-200)
            dict_tempo_decalage["HG"] = nb_decalage_haut_gauche

            ####Presence de la legende avec l'avancement, qui fait environ 10% de la hauteur
            Essai_boite_bas_gauche = Polygon([(gauche_CUSTOM, bas_CUSTOM), (gauche_CUSTOM+largeur_boite_ortho, bas_CUSTOM), (gauche_CUSTOM+largeur_boite_ortho, bas_CUSTOM+hauteur_boite_ortho), (gauche_CUSTOM, bas_CUSTOM+hauteur_boite_ortho)])
            Essai_boite_bas_gauche = translate(Essai_boite_bas_gauche,yoff=(haut_CUSTOM-bas_CUSTOM)*13/100)
            Essai_boite_bas_gauche = translate(Essai_boite_bas_gauche,0,-espace_esthetique)
            nb_decalage_bas_gauche = 0
            while any(df_contour_boite_normal.overlaps(Essai_boite_bas_gauche)):
                Essai_boite_bas_gauche = translate(Essai_boite_bas_gauche,-200)
                nb_decalage_bas_gauche = nb_decalage_bas_gauche+1
            #Encore un petit coup pour l'esthetique
            Essai_boite_bas_gauche = translate(Essai_boite_bas_gauche,-200)
            dict_tempo_decalage["BG"] = nb_decalage_bas_gauche

            position_finale = min(dict_tempo_decalage, key=dict_tempo_decalage.get)
            if position_finale=="HG":
                self.df_contour['geom_boite'] = [Essai_boite_haut_gauche]
            if position_finale=="BG":
                self.df_contour['geom_boite'] = [Essai_boite_bas_gauche]
            self.df_contour = self.df_contour.set_geometry("geom_boite")
            self.df_contour = self.df_contour.set_crs("epsg:2154")
        return self

    def actualisation_info_boite_ortho(self):
        self.df = self.df.set_geometry('geom_boite')
        self.df['type_placement_boite_final']="D"
        self.df['orient_BH']="B"
        self.df['orient_GD']="D"
        self.df['geometry_point_interception']=gpd.points_from_xy(self.df.set_geometry('geom_boite').representative_point().x-self.df["taille_largeur_boite_droit"]/2,self.df.set_geometry('geom_boite').representative_point().y)
        self.df = self.df.drop(['geom_boite'],axis=1)
        self.df = self.df.set_geometry('geometry_point_interception')
        return self
    
    def augmentation_esthetique_df_contour(self):
        self.df_contour['geom_boite'] = self.df_contour['geom_boite'].apply(lambda x:affinity.scale(x, xfact=1.0, yfact=1.1))
        return self
   
    ##########################################################################################
    #function sur boite complete
    ##########################################################################################
    def changement_nom_colonne_boite_et_liste_a_garder(self):
        df_reduction_nom_colonne_BDD = pd.read_csv('G:/travail/carto/projets basiques/PAOT global 5.0/fichier_reduction_nom_colonne.csv')
        dict_reduction_nom_colonne = pd.Series(df_reduction_nom_colonne_BDD.nom_colonne_court.values,index=df_reduction_nom_colonne_BDD.nom_colonne_long).to_dict()
        for nom_boite_maitre,dict_boite_maitre in self.items():
            if hasattr(dict_boite_maitre,"liste_nom_colonne_a_garder")==True:
                dict_boite_maitre.liste_nom_colonne_a_garder = [dict_reduction_nom_colonne[i] if i in dict_reduction_nom_colonne else i for i in dict_boite_maitre.liste_nom_colonne_a_garder ]
                for CODE_CUSTOM,df_CUSTOM in dict_boite_maitre.boite_complete.items():
                    dict_boite_maitre.boite_complete[CODE_CUSTOM] = dict_boite_maitre.boite_complete[CODE_CUSTOM].rename(columns = {i: dict_reduction_nom_colonne[i] for i in dict_boite_maitre.boite_complete[CODE_CUSTOM].columns if i in dict_reduction_nom_colonne})
            if hasattr(dict_boite_maitre,"liste_nom_colonne_a_garder")==False:
                liste_nom_colonne_a_garder = []
                for CODE_CUSTOM,df_CUSTOM in dict_boite_maitre.boite_complete.items():
                    dict_boite_maitre.boite_complete[CODE_CUSTOM] = dict_boite_maitre.boite_complete[CODE_CUSTOM].rename(columns = {i: dict_reduction_nom_colonne[i] for i in dict_boite_maitre.boite_complete[CODE_CUSTOM].columns if i in dict_reduction_nom_colonne})

        return self

    def garder_colonne_de_attributs_colonne_a_garder_boite(self):
        for nom_boite_maitre,dict_boite_maitre in self.items():
            for CODE_CUSTOM,df_CUSTOM in dict_boite_maitre.boite_complete.items():
                if len(df_CUSTOM)>0:
                    dict_boite_maitre.boite_complete[CODE_CUSTOM] = dict_boite_maitre.boite_complete[CODE_CUSTOM][dict_boite_maitre.liste_nom_colonne_a_garder]
        return self

    def definir_geometry_et_crs_boite(self):
        for nom_entite_CUSTOM,contenu_CUSTOM in self.items():
            for type_boite,contenu_boite in contenu_CUSTOM.items():
                contenu_boite.df_contour = contenu_boite.df_contour.set_crs('epsg:2154')
        for nom_entite_CUSTOM,contenu_CUSTOM in self.items():
            for type_boite,contenu_boite in contenu_CUSTOM.items():
                    for type_boite,contenu_boite in contenu_CUSTOM.items():
                        for type_bloc,contenu_bloc in contenu_boite.items():
                            if hasattr(contenu_bloc,"df_indiv"):
                                contenu_bloc.df_indiv = contenu_bloc.df_indiv.set_geometry('geom_point_bloc')
                                contenu_bloc.df_indiv = contenu_bloc.df_indiv.set_crs('epsg:2154')
                            if not hasattr(contenu_bloc,"df_indiv"):
                                contenu_bloc.df = contenu_bloc.df.set_geometry('geom_bloc')
                                contenu_bloc.df = contenu_bloc.df.set_crs('epsg:2154')  
        return self

    def export_boite(self,un_projet):
        dict_sans_tableau_vide = {}
        dict_nom_boite_maitre = {}
        for nom_boite_maitre,dict_boite_maitre in self.items():
            dict_sans_tableau_vide[nom_boite_maitre] = {}
            dict_nom_boite_maitre[nom_boite_maitre] = {}
            dict_nom_boite_maitre[nom_boite_maitre]['nom_boite'] = nom_boite_maitre
            for CODE_CUSTOM,df_CUSTOM in dict_boite_maitre.boite_complete.items():
                if len(df_CUSTOM) > 0:
                    dict_sans_tableau_vide[nom_boite_maitre][CODE_CUSTOM] = df_CUSTOM
        for nom_boite_maitre,dict_boite in dict_sans_tableau_vide.items():
            if len(dict_boite)>0:
                df_issu_dict_avec_info_placement_par_boite = pd.concat([v for k,v in dict_boite.items()])
                df_issu_dict_avec_info_placement_par_boite.to_file("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/" + un_projet.nom_dossier_maitre + '/couche_boite/boite_' + dict_nom_boite_maitre[nom_boite_maitre]['nom_boite'] + '.shp', encoding='utf-8')
            if len(dict_boite)==0:
                #On envoie un truc vide histoire d'actualiser quand méme le shp
                schema = {"geometry": "Polygon", "properties": {"id": "int"}}
                crs = "EPSG:2154"
                df = gpd.GeoDataFrame(geometry=[])
                df.to_file("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/" + un_projet.nom_dossier_maitre + '/couche_boite/boite_' + dict_nom_boite_maitre[nom_boite_maitre]['nom_boite'] + '.shp', driver='ESRI Shapefile', schema=schema, crs=crs)
                df_issu_dict_avec_info_placement_par_boite
        return self
