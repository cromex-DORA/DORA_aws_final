# -*- coding: utf-8 -*-
import pandas as pd
import shapely.geometry as geom
import geopandas as gpd
import textwrap
import numpy as np
import copy

from app.DORApy.classes.modules import texte,custom,lignes_multiples
from app.DORApy.classes.modules import config_DORA


###Fichiers config
dict_config_espace,dict_config_police = config_DORA.creation_dicts_config()
df_csv_x_icone_bloc_icone,df_csv_y_icone_bloc_icone = config_DORA.import_csv_placement_icone_bloc_icone()
dict_config_actions_MIA_DORA = config_DORA.import_dict_config_actions_MIA_DORA()


class Bloc:
    def __init__(self,taille_globale_carto):
        self.type = 'bloc'
        self.taille_globale_carto = taille_globale_carto

    ####################################################
    #bloc globaux
    ####################################################
    def conversion_hauteur_largeur_bloc_to_boite_complete(self,dict_dict_info_custom):
        self.df = self.df.rename({'hauteur_' + self.type + '_' + self.sous_type:'hauteur_boite_complete','largeur_' + self.type + '_' + self.sous_type:'largeur_boite_complete'},axis=1)
        return self

    def conversion_hauteur_largeur_boite_complete_to_bloc(self):
        self.df = self.df.rename({'largeur_boite_complete':'hauteur_' + self.type,'hauteur_boite_complete':'largeur_' + self.type},axis=1)
        return self

    ####################################################
    #bloc texte
    ####################################################
    def decoupage_bloc_texte_ligne_simple(self):
        liste_texte_ligne_simple = self.df['ALIAS'].to_list()
        liste_texte_ligne_simple = ["non-def" if x!=x else x for x in liste_texte_ligne_simple]
        liste_texte_ligne_simple = [textwrap.wrap(x, width=int(dict_config_espace['nombre_caracteres_decoupage_ligne_simple'][self.taille_globale_carto])) for x in liste_texte_ligne_simple]
        #On ajoute un signe pour le passage de ligne sur Qgis
        liste_texte_ligne_simple = [[x+'$' for x in liste] for liste in liste_texte_ligne_simple]
        liste_texte_ligne_simple = [[x[:-1]if x is liste[-1] else x for x in liste ] for liste in liste_texte_ligne_simple]
        self.df['ls_decoup_texte_simple'] = [''.join(morceau_liste_texte_ligne_simple) for morceau_liste_texte_ligne_simple in liste_texte_ligne_simple]
        return self


    def conversion_hauteur_largeur_bloc_texte_simple_to_boite_complete(self):
        for custom in self:
            self[custom]['hauteur_boite_complete_portrait'] = self[custom]['hauteur_' + self.type + '_' + self.sous_type]
            self[custom]['largeur_boite_complete_portrait'] = self[custom]['largeur_' + self.type + '_' + self.sous_type]
            self[custom]['hauteur_boite_complete_paysage'] = self[custom]['hauteur_' + self.type + '_' + self.sous_type]
            self[custom]['largeur_boite_complete_paysage'] = self[custom]['largeur_' + self.type + '_' + self.sous_type]
        return self

    def placement_bloc_texte(self,dict_dict_info_custom):
        if len(self.df)>0:
            self.df = self.df.set_geometry('geometry_point_interception')
            #Gauche
            self.df.loc[self.df['type_placement_boite_final']=='G','gauche_bloc']= self.df['droite_boite_complete']-self.df['largeur_bloc_texte_simple']
            self.df.loc[self.df['type_placement_boite_final']=='G','droite_bloc']= self.df['droite_boite_complete']   
            self.df.loc[self.df['type_placement_boite_final']=='G','bas_bloc']= self.df['haut_boite_complete']-self.df['hauteur_bloc_texte_simple']-self.df['ecart_hauteur_origine']
            self.df.loc[self.df['type_placement_boite_final']=='G','haut_bloc']= self.df['haut_boite_complete']-self.df['ecart_hauteur_origine']

            #Droite
            self.df.loc[self.df['type_placement_boite_final']=='D','gauche_bloc']= self.df['gauche_boite_complete']
            self.df.loc[self.df['type_placement_boite_final']=='D','droite_bloc']= self.df['gauche_boite_complete']+self.df['largeur_bloc_texte_simple']
            self.df.loc[self.df['type_placement_boite_final']=='D','bas_bloc']= self.df['haut_boite_complete']-self.df['hauteur_bloc_texte_simple']-self.df['ecart_hauteur_origine']
            self.df.loc[self.df['type_placement_boite_final']=='D','haut_bloc']= self.df['haut_boite_complete']-self.df['ecart_hauteur_origine']

            #Haut
            self.df.loc[self.df['type_placement_boite_final']=='H','gauche_bloc']= self.df['geometry_point_interception'].x-self.df['largeur_bloc_texte_simple']/2
            self.df.loc[self.df['type_placement_boite_final']=='H','droite_bloc']= self.df['geometry_point_interception'].x+self.df['largeur_bloc_texte_simple']/2   
            self.df.loc[self.df['type_placement_boite_final']=='H','bas_bloc']= self.df['bas_boite_complete']+self.df['ecart_hauteur_origine']
            self.df.loc[self.df['type_placement_boite_final']=='H','haut_bloc']= self.df['bas_boite_complete']+self.df['hauteur_bloc_texte_simple']-self.df['ecart_hauteur_origine'] 

            #Bas
            self.df.loc[self.df['type_placement_boite_final']=='B','gauche_bloc']= self.df['geometry_point_interception'].x-self.df['largeur_bloc_texte_simple']/2
            self.df.loc[self.df['type_placement_boite_final']=='B','droite_bloc']= self.df['geometry_point_interception'].x+self.df['largeur_bloc_texte_simple']/2   
            self.df.loc[self.df['type_placement_boite_final']=='B','bas_bloc']= self.df['haut_boite_complete']-self.df['hauteur_bloc_texte_simple']-self.df['ecart_hauteur_origine']
            self.df.loc[self.df['type_placement_boite_final']=='B','haut_bloc']= self.df['haut_boite_complete']-self.df['ecart_hauteur_origine']
        return self

    def actualisation_texte_simple_dans_bloc_texte_simple(self):
        if len(self.df.index)>0:
            self.df = self.df.drop(['geometry_point_interception'],axis=1)
            self.df['geometry_bloc_texte_simple'] = gpd.points_from_xy((self.df['gauche_bloc']+self.df['droite_bloc'])/2,(self.df['haut_bloc']+self.df['bas_bloc'])/2)
            self.df = self.df.set_geometry('geometry_bloc_texte_simple')
        return self

    ####################################################
    #bloc icone
    ####################################################
    def creation_liste_type_icone_nombres_actions_MIA(self):
        if self.thematique == 'MIA':
            if self.public_cible=="elu" or self.public_cible=='prefet':
                liste_categorie = ['hyd','mor','con','ino','gou']
            if self.public_cible=='tech':
                liste_categorie = ['rip','mor','con','mob', 'ZH','rui','ino','gou']
        if self.thematique == 'ASS':
            liste_categorie = ['etu','plu','tra','ANC','con','aut']
        return(liste_categorie)

    def conversion_niveau_avancement_tableau_actions(self,annee_actuelle):
        liste_etape = ["annee_action_ini","annee_action_eng","annee_action_term"]
        for etape in liste_etape:
            self.df[etape] = self.df[etape].astype(str)
            self.df[etape] = self.df[etape].str.findall(r'\d+\/\d+\/\d+|\d+').str[0]
            self.df[etape] = self.df[etape].fillna(0)
            self.df[etape] = self.df[etape].astype(int)
            self.df.loc[(self.df[etape]>annee_actuelle),etape] = 0
        #self.df['Avancement'] = self.df[["annee_action_prev","annee_action_ini","annee_action_eng","annee_action_term"]].idxmax(axis=1)
        #ATTENTION, on considére les actions sans niveau d'avancement comme prévisionnelles
        dict_conv_avancement = {"Prévisionnelle":1,"Initiée":2,"Engagée":3,"Terminée":4,"Abandonnée":5}
        self.df['Avancement'] = self.df['Avancement'].map(lambda x : dict_conv_avancement[x])
        self.df = self.df.drop(["annee_action_ini","annee_action_eng","annee_action_term","action_aba"],axis=1)
        return self

    def creation_liste_type_icone_toutes_pressions(self):
        if self.thematique == "global":
            liste_categorie = ['DOM','IND','N2','PHY','IRR','HYDT']
            #liste_categorie = ['DOM','IND']
        return liste_categorie
        

    ##########################################################################################
    #Actions MIA
    ##########################################################################################
    def conversion_typologie_actions_MIA(self,public_cible,liste_categorie):
        dict_config_actions_MIA_DORA = config_DORA.import_dict_config_actions_MIA_DORA()
        dict_config_actions_MIA_Osmose = config_DORA.import_dict_config_actions_MIA_Osmose()

        df_BDD_DORA = self.df.loc[self.df["NOM_TYPE_ACTION_DORA"]!='nan']
        df_BDD_OSMOSE = self.df.loc[self.df["NOM_TYPE_ACTION_DORA"]=='nan']
        if public_cible == "elu" or public_cible == 'prefet':
            #Les tableaux de conversion
            df_conv_MIA = dict_config_actions_MIA_DORA['df_actions_MIA_elu']
        if public_cible == 'tech':
            #Les tableaux de conversion 
            df_conv_MIA = dict_config_actions_MIA_DORA['df_actions_MIA_tech']
        for col in list(df_conv_MIA):
            try:
                df_conv_MIA[col] = df_conv_MIA[col].str.strip()
                df_conv_MIA[col] = df_conv_MIA[col].replace('\n',' ', regex=True)
            except:
                pass
    #merge pour le type d'action en fonction de la pression
        df_conv_MIA.columns = ["NOM_TYPE_ACTION_DORA"] + ['action_' + x for x in liste_categorie]
        df_conv_MIA = df_conv_MIA[["NOM_TYPE_ACTION_DORA"] + ['action_' + x for x in liste_categorie]]

        df_BDD_DORA = pd.merge(df_BDD_DORA,df_conv_MIA,on="NOM_TYPE_ACTION_DORA",how='left')

        if public_cible == "elu" or public_cible == 'prefet':
            #Les tableaux de conversion
            df_conv_MIA = dict_config_actions_MIA_Osmose['df_actions_MIA_elu']
        if public_cible == 'tech':
            #Les tableaux de conversion 
            df_conv_MIA = dict_config_actions_MIA_Osmose['df_actions_MIA_tech']

        for col in list(df_conv_MIA):
            try:
                df_conv_MIA[col] = df_conv_MIA[col].str.strip()
                df_conv_MIA[col] = df_conv_MIA[col].replace('\n',' ', regex=True)
            except:
                pass
    #merge pour le type d'action en fonction de la pression
        df_conv_MIA.columns = ["CODE_TYPE_ACTION_OSMOSE"] + ['action_' + x for x in liste_categorie]
        df_conv_MIA = df_conv_MIA[["CODE_TYPE_ACTION_OSMOSE"] + ['action_' + x for x in liste_categorie]]
        
        df_BDD_OSMOSE = pd.merge(df_BDD_OSMOSE,df_conv_MIA,on="CODE_TYPE_ACTION_OSMOSE",how='left')                    

        self.df = pd.concat([df_BDD_DORA,df_BDD_OSMOSE])
        self.df.to_csv("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MIA/MO/tableaux_tempo/df_brouillon_apres_conv_type_action.csv")
        return self

    def conversion_hauteur_largeur_bloc_icone_to_boite_complete(self):
        for custom in self:
            self[custom]['hauteur_boite_complete_portrait'] = self[custom]['hauteur_' + self.type + '_' + self.sous_type]
            self[custom]['largeur_boite_complete_portrait'] = self[custom]['largeur_' + self.type + '_' + self.sous_type]
            self[custom]['hauteur_boite_complete_paysage'] = self[custom]['hauteur_' + self.type + '_' + self.sous_type]
            self[custom]['largeur_boite_complete_paysage'] = self[custom]['largeur_' + self.type + '_' + self.sous_type]
        return self

    def placement_bloc_icone(self):
        if len(self.df)>0:
            self.df = self.df.set_geometry('geometry_point_interception')
            #Gauche
            self.df.loc[self.df['type_placement_boite_final']=='G','droite_bloc_' + self.type] = self.df['droite_boite_complete']-dict_config_espace['alinea_bloc_icone_portrait'][self.taille_globale_carto]
            self.df.loc[self.df['type_placement_boite_final']=='G','gauche_bloc_' + self.type] = self.df['droite_boite_complete']-self.df['largeur' + '_' + self.type]-dict_config_espace['alinea_bloc_icone_portrait'][self.taille_globale_carto]
            self.df.loc[self.df['type_placement_boite_final']=='G','haut_bloc_' + self.type] = self.df['haut_boite_complete']-self.df['ecart_hauteur_origine']
            self.df.loc[self.df['type_placement_boite_final']=='G','bas_bloc_' + self.type] = self.df['haut_boite_complete']-self.df['taille_hauteur_bloc_droit']-self.df['ecart_hauteur_origine']

            #Droite
            self.df.loc[self.df['type_placement_boite_final']=='D','droite_bloc_' + self.type] = self.df['gauche_boite_complete']+dict_config_espace['alinea_bloc_icone_portrait'][self.taille_globale_carto]
            self.df.loc[self.df['type_placement_boite_final']=='D','gauche_bloc_' + self.type] = self.df['gauche_boite_complete']+self.df['largeur' + '_' + self.type]+dict_config_espace['alinea_bloc_icone_portrait'][self.taille_globale_carto]
            self.df.loc[self.df['type_placement_boite_final']=='D','haut_bloc_' + self.type] = self.df['haut_boite_complete']-self.df['ecart_hauteur_origine']
            self.df.loc[self.df['type_placement_boite_final']=='D','bas_bloc_' + self.type] = self.df['haut_boite_complete']-self.df['taille_hauteur_bloc_droit']-self.df['ecart_hauteur_origine']

            #Haut
            self.df.loc[self.df['type_placement_boite_final']=='H','droite_bloc_' + self.type] = self.df['geometry_point_interception'].x+self.df['largeur' + '_' + self.type]/2
            self.df.loc[self.df['type_placement_boite_final']=='H','gauche_bloc_' + self.type] = self.df['geometry_point_interception'].x-self.df['largeur' + '_' + self.type]/2
            self.df.loc[self.df['type_placement_boite_final']=='H','haut_bloc_' + self.type] = self.df['bas_boite_complete']+self.df['taille_hauteur_bloc_biais']+self.df['ecart_hauteur_origine']
            self.df.loc[self.df['type_placement_boite_final']=='H','bas_bloc_' + self.type] = self.df['bas_boite_complete']+self.df['ecart_hauteur_origine']

            #Bas
            self.df.loc[self.df['type_placement_boite_final']=='B','droite_bloc_' + self.type] = self.df['geometry_point_interception'].x+self.df['largeur' + '_' + self.type]/2
            self.df.loc[self.df['type_placement_boite_final']=='B','gauche_bloc_' + self.type] = self.df['geometry_point_interception'].x-self.df['largeur' + '_' + self.type]/2
            self.df.loc[self.df['type_placement_boite_final']=='B','haut_bloc_' + self.type] = self.df['haut_boite_complete']-self.df['ecart_hauteur_origine']
            self.df.loc[self.df['type_placement_boite_final']=='B','bas_bloc_' + self.type] = self.df['haut_boite_complete']-self.df['taille_hauteur_bloc_biais']-self.df['ecart_hauteur_origine']
        return self

        ########################################################################################################
        #bloc icone - presion (classique),nombres actions(avec nombre en dessous et avancement sous l'icéne)
        ########################################################################################################

    def creation_dict_placement_position():
        df_x_icone_bloc_icone = df_csv_x_icone_bloc_icone.set_index('num')
        df_y_icone_bloc_icone = df_csv_y_icone_bloc_icone.set_index('num')
        dict_x_icone_bloc_icone = df_x_icone_bloc_icone.to_dict('index')
        dict_y_icone_bloc_icone = df_y_icone_bloc_icone.to_dict('index')

        df_x_icone_bloc_icone = pd.json_normalize(dict_x_icone_bloc_icone, sep='_')
        df_y_icone_bloc_icone = pd.json_normalize(dict_y_icone_bloc_icone, sep='_')
        dict_x_icone_bloc_icone = df_x_icone_bloc_icone.to_dict(orient='records')[0]
        dict_y_icone_bloc_icone = df_y_icone_bloc_icone.to_dict(orient='records')[0]
        return dict_x_icone_bloc_icone,dict_y_icone_bloc_icone

    def placement_icone_simple(self,dict_x_icone_bloc_icone,dict_y_icone_bloc_icone,liste_categorie):
        ###♦ATTENTION, QGIS EST DEBILE,  LE DECALAGE EST EN NEGATIF ! Ex : Si on veut décaler en haut à gauche, c'est double négatif
        def placement_x_bloc_icone(x,categorie,espace_entre_icone):
            nb_icone = x['NB_type_icone']
            placement = x['placement_' + categorie]
            if x['num_'+categorie]!=0:
                x['x_'+categorie] = dict_x_icone_bloc_icone[placement]*(x['largeur_bloc_icone_indiv']+espace_entre_icone/2)
            if x['num_'+categorie]==0:
                x['x_'+categorie] = 0
            return x        

        def placement_y_bloc_icone(x,categorie):
            nb_icone = x['NB_type_icone']
            placement = x['placement_' + categorie]
            if x['num_'+categorie]!=0:
                if nb_icone>0 and nb_icone<4:
                    x['y_'+categorie] = 0
                if nb_icone>3:
                    if dict_y_icone_bloc_icone[placement]>0:
                        x['y_'+categorie] = (-1)*(x['hauteur_bloc_icone_indiv']+(dict_config_espace['espace_entre_lignes_bloc_icone'][self.taille_globale_carto])/2)*dict_y_icone_bloc_icone[placement]       
                    if dict_y_icone_bloc_icone[placement]<0:
                        x['y_'+categorie] = (-1)*(x['hauteur_bloc_icone_indiv']+(dict_config_espace['espace_entre_lignes_bloc_icone'][self.taille_globale_carto])/2)*dict_y_icone_bloc_icone[placement]  
            if x['num_'+categorie]==0:
                x['y_'+categorie] = 0
            return x

        for categorie in liste_categorie:
            self.df['placement_' + categorie] = self.df['num_'+categorie].astype(str) + "_parmi_" + self.df['NB_type_icone'].astype(str)
            espace_entre_icone = dict_config_espace['espace_entre_icone_bloc'][self.taille_globale_carto]
            self.df = self.df.apply(lambda x:placement_x_bloc_icone(x,categorie,espace_entre_icone),axis=1)
            self.df = self.df.apply(lambda x:placement_y_bloc_icone(x,categorie),axis=1)
            '''self.df['pos_'+categorie] = self.df['x_'+categorie].astype(str) + "," + self.df['y_'+categorie].astype(str)
            self.df['pos_'+categorie] = self.df['pos_'+categorie].fillna(0)'''
        return self


    def ajout_dict_df_icone_nombre_actions(self,liste_categorie,liste_sous_type):
        #On pousse l'icone de la moitié de l'espace pour l'avancement
        espace_nb_actions = dict_config_espace['espace_pour_nb_action_et_avancement_sous_icone_bloc_nombre_actions'][self.taille_globale_carto]
        for categorie in liste_categorie:
            self.df['y_' + categorie] = self.df['y_' + categorie] - espace_nb_actions/2
            self.df['x_posnb' + categorie] = self.df['x_'+categorie]
            self.df['y_posnb' + categorie] = self.df['y_'+categorie]+self.df['hauteur_icone']/2+espace_nb_actions/2
        return self

    def ajout_df_icone_avancement_info_barre(self,liste_categorie,liste_sous_type):
        for categorie in liste_categorie:
            if "avancement" in liste_sous_type:
                self.df['x_posnb' + categorie] = self.df['x_posnb' + categorie] - dict_config_espace['largeur' + '_' + self.type][self.taille_globale_carto]/2 + dict_config_espace['alinea_nombre_action'][self.taille_globale_carto]
            self.df['x_gposav' + categorie] = (self.df['x_'+categorie]-dict_config_espace['largeur' + '_' + self.type][self.taille_globale_carto]/2+dict_config_espace['alinea_nombre_action'][self.taille_globale_carto]*2)
            self.df['x_dposav' + categorie] = (self.df['x_'+categorie]+dict_config_espace['largeur' + '_' + self.type][self.taille_globale_carto]/2-dict_config_espace['alinea_nombre_action'][self.taille_globale_carto])
            self.df['y_posav' + categorie] = ((self.df['y_'+categorie]+dict_config_espace['hauteur_' + self.type][self.taille_globale_carto]/2+dict_config_espace['espace_pour_nb_action_et_avancement_sous_icone_bloc_nombre_actions'][self.taille_globale_carto]/2-dict_config_espace['alinea_rehausseY_nombre_action'][self.taille_globale_carto]))
        return self
    
    def ajout_df_icone_pressions_MIA_info_barre(self,liste_categorie,liste_sous_type):
        largeur_barre_pression = dict_config_espace['espace_droite_icone_pour_pression'][self.taille_globale_carto]
        for categorie in liste_categorie:
            if categorie in ["hyd","con","mor"]:
                self.df['x_' + categorie] = self.df['x_' + categorie] - largeur_barre_pression/2
                if "avancement" in liste_sous_type:
                    self.df['x_gposav' + categorie] = self.df['x_gposav' + categorie] - largeur_barre_pression/2
                    self.df['x_dposav' + categorie] = self.df['x_dposav' + categorie] - largeur_barre_pression/2
                if "nombre_actions" in liste_sous_type:
                    self.df['x_posnb' + categorie] = self.df['x_posnb' + categorie] - largeur_barre_pression/2
                self.df['x_pospress' + categorie] = self.df['x_' + categorie] + self.df['largeur_icone']/2 + largeur_barre_pression/2.2
                self.df['y_bpres' + categorie] = self.df['y_' + categorie] + self.df['hauteur_icone']/2
                self.df['y_hpres' + categorie] = self.df['y_' + categorie] + self.df['hauteur_icone']/2 - (self.df['P_'+categorie]/self.df['nb_total_CODE_ME'])*self.df['hauteur_icone']
        return self
    
    def passage_en_str_position(self,liste_categorie):
        for sous_type in self.sous_type:
            for categorie in liste_categorie:
                self.df['pos_'+categorie] = self.df['x_'+categorie].astype(str) + "," + self.df['y_'+categorie].astype(str)
                if sous_type=="nombre_actions":
                    self.df['posnb'+categorie] = self.df['x_posnb'+categorie].astype(str) + "," + self.df['y_posnb'+categorie].astype(str)
                if sous_type=="avancement":
                    self.df['xgposav'+categorie] = self.df['x_gposav'+categorie].astype(str)
                    self.df['xdposav'+categorie] = self.df['x_dposav'+categorie].astype(str)
                    self.df['yposav'+categorie] = self.df['y_posav'+categorie].astype(str)
                if sous_type=="pressions_MIA":
                    if categorie in ["mor","con","hyd"]:
                        self.df['xpre'+categorie] = self.df['x_pospress'+categorie].astype(str)
                        self.df['ybpre'+categorie] = self.df['y_bpres'+categorie].astype(str)
                        self.df['yhpre'+categorie] = self.df['y_hpres'+categorie].astype(str)
        return self


    def ajout_attributs_class_colonne_a_garder_bloc_icone(self,liste_categorie):
        for categorie in liste_categorie:
            self.liste_nom_colonne_a_garder.append('pos_' + categorie)

        if "nombre_actions" in self.sous_type:
            for categorie in liste_categorie:
                self.liste_nom_colonne_a_garder.append('posnb' + categorie)
        if "avancement" in self.sous_type:
            for categorie in liste_categorie:
                self.liste_nom_colonne_a_garder.append('xgposav' + categorie)
                self.liste_nom_colonne_a_garder.append('xdposav' + categorie)
                self.liste_nom_colonne_a_garder.append('yposav' + categorie)
        if "pressions_MIA" in self.sous_type:
            for categorie in ["hyd","mor","con"]:
                self.liste_nom_colonne_a_garder.append('xpre' + categorie)
                self.liste_nom_colonne_a_garder.append('ybpre' + categorie)
                self.liste_nom_colonne_a_garder.append('yhpre' + categorie)
        return self


    def actualisation_point_geometry_bloc_icone_nombres_actions(self):
        if len(self.df)>0:
            self.df = self.df.drop(['geometry_point_interception'],axis=1)
            self.df['geometry_bloc_icone'] =  gpd.points_from_xy((self.df['gauche_bloc_'+self.type]+self.df['droite_bloc_'+self.type])/2,(self.df['haut_bloc_'+self.type]+self.df['bas_bloc_'+self.type]+dict_config_espace['espace_pour_nb_action_et_avancement_sous_icone_bloc_nombre_actions'][self.taille_globale_carto])/2)
            self.df = self.df.set_geometry('geometry_bloc_icone')
        return self


    ####################################################
    #bloc icone - pression
    ####################################################

    def actualisation_point_geometry_bloc_icone_pression_global(self):
        if len(self.df.index)>0:
            self.df = self.df.drop(['geometry_point_interception'],axis=1)
            self.df['geometry_bloc_icone'] =  gpd.points_from_xy((self.df['gauche_bloc_'+self.type]+self.df['droite_bloc_'+self.type])/2,(self.df['haut_bloc_'+self.type]+self.df['bas_bloc_'+self.type]+dict_config_espace['espace_pour_nb_action_et_avancement_sous_icone_bloc_nombre_actions'][self.taille_globale_carto])/2)
            self.df = self.df.set_geometry('geometry_bloc_icone')
        return self

    ####################################################
    #bloc lignes texte multiples
    ####################################################
    def conversion_hauteur_largeur_bloc_lignes_multiples_to_boite_complete(self,dict_dict_info_custom):
        self.df['hauteur_boite_complete_portrait'] = self.df['hauteur_' + self.type + '_' + self.sous_type]
        self.df['largeur_boite_complete_portrait'] = self.df['largeur_' + self.type + '_' + self.sous_type]
        self.df['hauteur_boite_complete_paysage'] = self.df['largeur_' + self.type + '_' + self.sous_type]
        self.df['largeur_boite_complete_paysage'] = self.df['hauteur_' + self.type + '_' + self.sous_type]
        return self



    #Niveau 2
    def placement_bloc_lm_avec_calcul_coordonnees_bloc_lm(self):
        if len(self.df.index)>0:
            self.df = self.df.set_geometry('geometry_point_interception')
            ###Un alinéa simple ne suffit pas, il faut faire un fonction de la hauteur de la premiére ligne de chaque REF
            #On calcul les Y et les X
            self.df.loc[self.df['type_placement_boite_final']=='H','bas_bloc_lm']=self.df['bas_boite_complete']+self.df['ecart_hauteur_origine']
            self.df.loc[self.df['type_placement_boite_final']=='H','haut_bloc_lm']=self.df['bas_boite_complete']+self.df['ecart_hauteur_origine']+self.df['taille_hauteur_bloc_droit']
            self.df.loc[self.df['type_placement_boite_final'].isin(['B','G','D']),'bas_bloc_lm']=self.df['bas_boite_complete']-self.df['ecart_hauteur_origine']-self.df['taille_hauteur_bloc_droit']
            self.df.loc[self.df['type_placement_boite_final'].isin(['B','G','D']),'haut_bloc_lm']=self.df['haut_boite_complete']-self.df['ecart_hauteur_origine']
            
            self.df.loc[self.df['type_placement_boite_final']=='H','Y_bloc_lm'] = self.df['bas_bloc_lm']
            self.df.loc[self.df['type_placement_boite_final'].isin(['B','G','D']),'Y_bloc_lm'] = self.df['haut_bloc_lm']
            
            self.df.loc[self.df['type_placement_boite_final']=='G','X_bloc_lm'] = self.df['droite_boite_complete']
            self.df.loc[self.df['type_placement_boite_final']=='D','X_bloc_lm'] = self.df['gauche_boite_complete']
            self.df.loc[self.df['type_placement_boite_final'].isin(['B','H']),'X_bloc_lm'] = self.df['geometry_point_interception'].x

            '''self.df.loc[self.df['type_placement_boite_final']=='B','Y_bloc_lm'] = self.df['Y_haut_bloc_lm_'+self.sous_type + '_biais']-dict_config_espace['alineaY_entre_boite_et_point_lm_paysage'][self.taille_globale_carto]
            
            self.df.loc[self.df['type_placement_boite_final']=='H','Y_bloc_lm'] = self.df['Y_bas_bloc_lm_'+self.sous_type + '_biais']+dict_config_espace['alineaY_entre_boite_et_point_lm_paysage'][self.taille_globale_carto]'''
        return self
    
    def actualisation_point_geometry_bloc_lm(self):
        if len(self.df.index)>0:
            self.df = self.df[[x for x in list(self.df) if x!="geometry_point_interception"]]
            self.df['geometry_bloc_lm'] =  gpd.points_from_xy(self.df["X_bloc_lm"],self.df["Y_bloc_lm"])
            self.df = self.df.set_geometry('geometry_bloc_lm')
        return self    

    def ajout_info_geom_boite_dans_df_indiv(self):
        self.df = pd.merge(self.df,self.df_indiv.groupby("CODE_REF").agg({'hauteur_ligne_indiv_droit':'first'}).rename(columns={'hauteur_ligne_indiv_droit':'hauteur_premiere_lm'}),on="CODE_REF")
        self.df_indiv = pd.merge(self.df_indiv,self.df,on="CODE_REF",suffixes=[None,'_a_supprimer'])
        self.df_indiv = self.df_indiv.loc[:,~self.df_indiv.columns.str.endswith('_a_supprimer')]
        return self

    def calcul_origine_phrases_bloc_lignes_multiples(self):
        liste_REF_dans_custom = list(set((self.df_indiv['CODE_REF'].tolist())))
        def calcul_coordonnees_point_bloc_lm(df):
            alinea = dict_config_espace['alineaY_entre_boite_et_point_lm_paysage'][self.taille_globale_carto]
            orientation = df['type_placement_boite_final'].to_list()[0]
            if orientation == "G" or orientation == "D":
                if orientation == "G":
                    df['X_point_bloc_lm'] = df['X_bloc_lm'] - alinea
                if orientation == "D":
                    df['X_point_bloc_lm'] = df['X_bloc_lm'] + alinea
                df['Y_point_bloc_lm_origine_haut'] = df['Y_bloc_lm']-alinea
                df['Y_point_bloc_lm'] = df['Y_point_bloc_lm_origine_haut']-df['hauteur_ligne_indiv_droit'].cumsum()+df['hauteur_ligne_indiv_droit']-df['hauteur_ligne_indiv_droit']/2                    
            if orientation == "B" or orientation == "H":
                if orientation == "B":
                    df['Y_point_bloc_lm'] = df['haut_bloc_lm'] - alinea - dict_config_espace['espace_entre_haut_bloc_lm_et_icone_lm'][self.taille_globale_carto]
                    
                if orientation == "H":
                    df['Y_point_bloc_lm'] = df['bas_bloc_lm'] + alinea + dict_config_espace['espace_entre_haut_bloc_lm_et_icone_lm'][self.taille_globale_carto]
                df['X_point_bloc_lm_origine_gauche'] = df['X_bloc_lm']-sum(df['largeur_ligne_indiv_biais'])/2
                df['X_point_bloc_lm'] = df['X_point_bloc_lm_origine_gauche']+df['largeur_ligne_indiv_biais'].cumsum()-df['largeur_ligne_indiv_biais']+df['largeur_ligne_indiv_biais']/2
                
            return df
        def allo(df):
            df['allo'] = "allo"
            return df
        liste_tempo = []
        for CODE_REF in liste_REF_dans_custom:
            liste_tempo.append(calcul_coordonnees_point_bloc_lm(self.df_indiv.loc[self.df_indiv["CODE_REF"]==CODE_REF]))
        self.df_indiv = pd.concat(liste_tempo)
        return self

    def actualisation_point_geometry_point_bloc_lm(self):
        if len(self.df_indiv.index)>0:
            self.df_indiv = self.df_indiv[[x for x in list(self.df_indiv) if x!="geometry_bloc_lm"]]
            self.df_indiv['geometry_point_bloc_lignes_multiples'] = gpd.points_from_xy(self.df_indiv['X_point_bloc_lm'],self.df_indiv['Y_point_bloc_lm'])
            self.df_indiv = self.df_indiv.set_geometry('geometry_point_bloc_lignes_multiples')
        return self

##########################################################################################
#bloc_texte_simple (nom des ME, nom PPG)
##########################################################################################
class BlocTexteSimple(Bloc):
    def __init__(self,taille_globale_carto):
        super().__init__(taille_globale_carto=taille_globale_carto)
        self.taille_globale_carto = taille_globale_carto
        self.type = 'bloc_texte_simple'
        

    def calcul_taille_bloc_texte_simple(self):
        self = texte.extraire_hauteur_largeur_tableau_texte(self,"NOM_REF",self.type)
        self = texte.calcul_nb_liste_texte(self,"NOM_REF",self.type)
        #self = self.rename({'hauteur_' + type_bloc + '_' + "nom_simple_REF":'hauteur_' + type_bloc + '_' + self.sous_type,'largeur_' + type_bloc + '_' + "nom_simple_REF":'largeur_' + type_bloc + '_' + self.sous_type},axis=1)
        return self

    def conversion_bloc_texte_to_boite_complete(self):
        for custom in self:
            self[custom] = self[custom].rename({'hauteur_' + self.type + '_' + self.sous_type:'hauteur_boite_complete','largeur_' + self.type + '_' + self.sous_type:'largeur_boite_complete'},axis=1)
        return self

    def conversion_boite_complete_to_bloc_texte(self):
        for custom in self:
            self[custom] = self[custom].rename({'hauteur_boite_complete':'hauteur_' + self.type + '_' + self.sous_type,'largeur_boite_complete':'largeur_' + self.type + '_' + self.sous_type},axis=1)
        return self

    def placement_bloc_texte_simple_dans_boite(self,dict_dict_info_custom):
        self = Bloc.placement_bloc_texte(self,dict_dict_info_custom)
        return self

    def placement_texte_simple_dans_bloc_texte_simple(self):
        self = Bloc.actualisation_texte_simple_dans_bloc_texte_simple(self)
        return self

#########################################################################################
#bloc_icone
##########################################################################################
class BlocIcone(Bloc):
    def __init__(self,taille_globale_carto):
        super().__init__(taille_globale_carto=taille_globale_carto)
        self.taille_globale_carto = taille_globale_carto        
        self.type = 'bloc_icone'

    def set_config_bloc_icone(self,boite_complete_maitre,type_icone,thematique,sous_type,colonne_nb_icone):
        self._liste_contenu_boite.append(self)
        self.type_icone = type_icone
        self.thematique = thematique
        self.type = 'bloc_icone'
        self.avancement_max = 4
        self.sous_type = sous_type
        self.colonne_nb_icone = colonne_nb_icone
        self.boite_complete_maitre = boite_complete_maitre
        self.echelle_carto = boite_complete_maitre.echelle_carto
        self.colonne_carto = boite_complete_maitre.colonne_carto
        self.orientation = boite_complete_maitre.orientation
        self.nom_boite_maitre = boite_complete_maitre.nom_boite_maitre
        self.liste_nom_colonne_a_garder = []

    def creation_dict_compte_chaque_categorie_et_avancement_nombres_actions(self,liste_categorie,avancement_max):
        liste_total_av = ['av_' + prefixe + "_" + str(i) for prefixe in liste_categorie for i in range(1,avancement_max+1)]
        df_tempo_avancement=self.groupby(['CODE_REF','Avancement']).agg({'action_'+categorie: 'count' for categorie in liste_categorie}).reset_index()
        df_tempo_avancement.columns = ['CODE_REF','Avancement'] + ['av_'+categorie for categorie in liste_categorie]
        df_tempo_avancement = df_tempo_avancement.pivot(index='CODE_REF', columns='Avancement', values=['av_'+categorie for categorie in liste_categorie])
        df_tempo_avancement.columns = [c[0] + "_" + str(c[1]) for c in df_tempo_avancement.columns]
        #Le pivot n'ajoute pas toutes les colonnes. Pour la suite, il faut ajouter les colonnes manquantes.
        df_tempo_avancement = df_tempo_avancement.reindex(columns=list(liste_total_av), fill_value=0)
        #Et remplir le graph avec des 0 si NA
        df_tempo_avancement = df_tempo_avancement.fillna(0)
        df_tempo_avancement =df_tempo_avancement.astype(int)
        for categorie in liste_categorie:
            df_tempo_avancement[['av_' + categorie + '_' + str(numero_avancement) for numero_avancement in range (1,avancement_max+1)]] = df_tempo_avancement[['av_' + categorie + '_' + str(numero_avancement) for numero_avancement in range (1,avancement_max+1)]].replace(0, np.nan)
            df_tempo_avancement[['av_' + categorie + '_' + str(numero_avancement) for numero_avancement in range (1,avancement_max+1)]] = df_tempo_avancement[['av_' + categorie + '_' + str(numero_avancement) for numero_avancement in range (1,avancement_max+1)]].cumsum(axis=1)
        df_tempo_avancement['CODE_REF'] = df_tempo_avancement.index
        df_tempo_avancement = df_tempo_avancement.reset_index(drop=True)
        for col in list(df_tempo_avancement):
            if col.startswith("av_"):
                df_tempo_avancement[col] = df_tempo_avancement[col].fillna(0)
                df_tempo_avancement[col] = df_tempo_avancement[col].astype(int)
        return df_tempo_avancement

    def ajout_si_icone_par_categorie(self,liste_categorie,type_icone):
        if type_icone=="icone_action_MIA":
            for categorie in liste_categorie:
                self.loc[self['action_' + categorie]>0,'icone_'+categorie]=1
            for nom_col in list(self):
                if nom_col.startswith('nb_ico') or nom_col.startswith('av_') or nom_col.startswith('icone_'):
                    self[nom_col] = self[nom_col].fillna(0)
                    self[nom_col] = self[nom_col].astype(int)
        if type_icone=="icone_pression":    
            for categorie in liste_categorie:
                self.loc[self['P_' + categorie]>0,'icone_'+categorie]=1 
            self[[x for x in list(self) if x.startswith("icone_")]] = self[[x for x in list(self) if x.startswith("icone_")]].fillna(0)                           
        for categorie in liste_categorie:
            self['icone_'+ categorie] = self['icone_'+ categorie].astype(int)
        return self

    def ajout_numero_par_binome_categorie(self,liste_categorie,liste_contenu_bloc):
        df_tempo = self[['icone_' + categorie for categorie in liste_categorie]]
        #On replace les 0 par des NA, pour permettre un cumsum 
        df_tempo.replace(0, np.nan, inplace=True)
        if "pressions_MIA" in liste_contenu_bloc:
            df_tempo['icone_hyd'] = 1
            df_tempo['icone_mor'] = 1
            df_tempo['icone_con'] = 1
        df_tempo[['num_' + categorie for categorie in liste_categorie]] = df_tempo[['icone_' + categorie for categorie in liste_categorie]].cumsum(axis = 1)
        #On isole les colonnes num pour le merge
        df_tempo = df_tempo[['num_' + categorie for categorie in liste_categorie]]
        df_tempo.replace(np.nan, 0, inplace=True)
        df_tempo = df_tempo.astype(int)
        self = pd.merge(self,df_tempo,left_index=True, right_index=True)
        self['NB_type_icone'] = self[['icone_' + categorie for categorie in liste_categorie]].sum(axis=1)
        return self
    
    def garder_type_specifique_action(self,liste_categorie):
        list_col_P_a_garder = ["P_" + categorie for categorie in liste_categorie]
        if "P_HYDT" in list_col_P_a_garder:
            list_col_P_a_garder = list_col_P_a_garder + ["P_HYDRO","P_MORPHO","P_CONTI"]
        list_col_sans_P = [x for x in list(self) if not x.startswith("P_")]
        list_col_total = list_col_sans_P + list_col_P_a_garder
        self=self[list_col_total]
        return self

    def indications_nombre_echelle_REF_avec_pression(self,liste_categorie,dict_df_donnees,df_CODE_REF,dict_relation_shp_liste):
        df_pression = dict_df_donnees['df_pression']
        liste_echelle_REF = list(set(df_CODE_REF['echelle_REF'].to_list()))
        liste_echelle_REF = [x for x in liste_echelle_REF if x not in ['SME','ME']]
        dict_nb_CODE_ME = {}
        for echelle_REF in liste_echelle_REF:
            dict_tempo_nb_CODE_ME = {k:len(dict_relation_shp_liste['dict_liste_ME_par_'+echelle_REF][k]) for k in df_CODE_REF.loc[df_CODE_REF['echelle_REF']==echelle_REF]['CODE_REF'].to_list()}
            dict_nb_CODE_ME = dict_nb_CODE_ME|dict_tempo_nb_CODE_ME
            df_CODE_REF.loc[df_CODE_REF['echelle_REF']==echelle_REF,"CODE_ME"] = df_CODE_REF['CODE_REF'].map(dict_relation_shp_liste['dict_liste_ME_par_'+echelle_REF])
            
        df_CODE_REF.loc[df_CODE_REF['echelle_REF']=="ME","CODE_ME"] = df_CODE_REF['CODE_REF']
        df_CODE_REF.loc[df_CODE_REF['echelle_REF']=="SME","CODE_ME"] = df_CODE_REF['CODE_REF'].map({value: [key] for key in dict_relation_shp_liste['dict_liste_SME_par_ME'] for value in dict_relation_shp_liste['dict_liste_SME_par_ME'][key]})
        df_CODE_REF = df_CODE_REF.explode('CODE_ME')
        df_pression_CODE_ME = pd.merge(df_CODE_REF,df_pression,on="CODE_ME")
        df_pression_CODE_ME = df_pression_CODE_ME[['CODE_ME','CODE_REF',"P_MORPHO","P_HYDRO","P_CONTI"]]
        for pression in ["P_MORPHO","P_HYDRO","P_CONTI"]:
            df_pression_CODE_ME.loc[df_pression_CODE_ME[pression]<3,pression] = 0
            df_pression_CODE_ME.loc[df_pression_CODE_ME[pression]==3,pression] = 1
        df_pression_CODE_ME = df_pression_CODE_ME.groupby("CODE_REF").agg({"P_MORPHO":"sum","P_HYDRO":"sum","P_CONTI":"sum"})
        df_pression_CODE_ME['CODE_REF'] = df_pression_CODE_ME.index
        df_pression_CODE_ME["nb_total_CODE_ME"] = df_pression_CODE_ME['CODE_REF'].map(dict_nb_CODE_ME)
        df_pression_CODE_ME["nb_total_CODE_ME"].fillna(1)
        df_pression_CODE_ME = df_pression_CODE_ME.reset_index(drop=True)
        df_pression_CODE_ME = df_pression_CODE_ME.rename({"P_MORPHO":"P_mor","P_HYDRO":"P_hyd","P_CONTI":"P_con"},axis=1)
        return df_pression_CODE_ME

    def rassemblement_et_ajout_df_sup(dict_bloc,liste_categorie,liste_df_info_sup_icone,liste_contenu_bloc):
        dict_tempo_echelle_REF = dict(zip(dict_bloc.df['CODE_REF'].to_list(),dict_bloc.df['echelle_REF'].to_list()))
        dict_bloc.df = dict_bloc.df.groupby(['CODE_REF']).agg({'action_'+categorie: 'count' for categorie in liste_categorie}).reset_index()
        dict_bloc.df['echelle_REF'] = dict_bloc.df['CODE_REF'].map(dict_tempo_echelle_REF)
        if "pressions_MIA" in liste_contenu_bloc:
            liste_categorie_sans_icone_hydromorpho = [x for x in liste_categorie if x not in ['hyd','con','mor']]
            dict_bloc.df['NB_type_icone'] = dict_bloc.df[['action_'+ categorie for categorie in liste_categorie_sans_icone_hydromorpho]].astype(bool).sum(axis=1) + 3
            for categorie in liste_categorie:
                dict_bloc.df['nb_ico_' + categorie] = dict_bloc.df['action_'+categorie]  
     
        if "pressions_MIA" not in liste_contenu_bloc:   
            dict_bloc.df['NB_type_icone'] = dict_bloc.df[['action_'+ categorie for categorie in liste_categorie]].astype(bool).sum(axis=1)
            for categorie in liste_categorie:
                dict_bloc.df['nb_ico_' + categorie] = dict_bloc.df['action_'+categorie]
        for df_sup in liste_df_info_sup_icone:
            dict_bloc.df = pd.merge(dict_bloc.df,df_sup,on="CODE_REF",how="left")
        return dict_bloc


    def ajout_taille_icone(self):
        if "nombre_actions" in self.sous_type:
            self.df["hauteur_icone"] = dict_config_espace['hauteur_bloc_icone_nombre_actions'][self.taille_globale_carto]
            self.df["largeur_icone"] = dict_config_espace['largeur_bloc_icone_nombre_actions'][self.taille_globale_carto]
        if "pressions_MIA" in self.sous_type:
            self.df["largeur_icone"] = dict_config_espace['largeur_colonne_pression_icone'][self.taille_globale_carto]           
        return self


    def actualisation_liste_nom_colonne_a_garder_bloc_icone_nombres_actions(self,liste_categorie):
        for categorie in liste_categorie:
            self.liste_nom_colonne_a_garder.extend(['icone_' + categorie])
            self.liste_nom_colonne_a_garder.extend(['num_' + categorie])
            self.liste_nom_colonne_a_garder.extend(['nb_ico_' + categorie])
            self.liste_nom_colonne_a_garder = list(set(self.liste_nom_colonne_a_garder))
        return self
    
    def actualisation_liste_nom_colonne_a_garder_bloc_icone_avancement(self,liste_categorie):
        for categorie in liste_categorie:
            self.liste_nom_colonne_a_garder.extend(['av_' + categorie + '_' + str(numero_avancement) for numero_avancement in range (1,self.avancement_max+1)])
            self.liste_nom_colonne_a_garder = list(set(self.liste_nom_colonne_a_garder))
        return self
    
    def actualisation_liste_nom_colonne_a_garder_bloc_icone_pressions(self,liste_categorie):
        for categorie in liste_categorie:
            self.liste_nom_colonne_a_garder.extend(['icone_' + categorie])
            self.liste_nom_colonne_a_garder.extend(['num_' + categorie])
            if "HYDT" in liste_categorie:
                self.liste_nom_colonne_a_garder.extend(["P_MORPHO","P_HYDRO","P_CONTI"])
            
            self.liste_nom_colonne_a_garder = list(set(self.liste_nom_colonne_a_garder))

        return self

    def calcul_taille_bloc_icone(self):
        #Calcul de la hauteur
        self.df['hauteur_icone'] = dict_config_espace['hauteur_bloc_icone'][self.taille_globale_carto]
        self.df['largeur_icone'] = dict_config_espace['largeur_bloc_icone'][self.taille_globale_carto]         
        self.df['hauteur_bloc_icone_indiv'] = dict_config_espace['hauteur_bloc_icone'][self.taille_globale_carto]
        self.df['largeur_bloc_icone_indiv'] = dict_config_espace['largeur_bloc_icone'][self.taille_globale_carto]        

        if "nombre_actions" in self.sous_type or "avancement" in self.sous_type:
            self.df['hauteur_bloc_icone_indiv'] = self.df['hauteur_bloc_icone_indiv']+dict_config_espace['espace_sous_icone_pour_nombre_et_avancement'][self.taille_globale_carto]
        if "pressions_MIA" in self.sous_type:
            self.df['largeur_bloc_icone_indiv']=self.df['largeur_bloc_icone_indiv']+dict_config_espace['espace_droite_icone_pour_pression'][self.taille_globale_carto]

        #Calcul de la largeur
        
        self.df.loc[(self.df[self.colonne_nb_icone]>0)&(self.df[self.colonne_nb_icone]<4),'hauteur_bloc_icone']=self.df['hauteur_bloc_icone_indiv']
        self.df.loc[(self.df[self.colonne_nb_icone]>3),'hauteur_bloc_icone']=2*(self.df['hauteur_bloc_icone_indiv']) + dict_config_espace['espace_entre_lignes_bloc_icone'][self.taille_globale_carto]        

        self.df.loc[(self.df[self.colonne_nb_icone]==0),'largeur_bloc_icone']=0
        self.df.loc[(self.df[self.colonne_nb_icone]==1),'largeur_bloc_icone']=self.df['largeur_bloc_icone_indiv']+dict_config_espace['espace_entre_icone_bloc'][self.taille_globale_carto]
        self.df.loc[(self.df[self.colonne_nb_icone]==2),'largeur_bloc_icone']=2*self.df['largeur_bloc_icone_indiv']+dict_config_espace['espace_entre_icone_bloc'][self.taille_globale_carto]
        self.df.loc[(self.df[self.colonne_nb_icone]==3),'largeur_bloc_icone']=3*self.df['largeur_bloc_icone_indiv']+2*dict_config_espace['espace_entre_icone_bloc'][self.taille_globale_carto]
        self.df.loc[(self.df[self.colonne_nb_icone]==4),'largeur_bloc_icone']=2*self.df['largeur_bloc_icone_indiv']+dict_config_espace['espace_entre_icone_bloc'][self.taille_globale_carto]
        self.df.loc[(self.df[self.colonne_nb_icone]==5),'largeur_bloc_icone']=3*self.df['largeur_bloc_icone_indiv']+2*dict_config_espace['espace_entre_icone_bloc'][self.taille_globale_carto]
        self.df.loc[(self.df[self.colonne_nb_icone]==6),'largeur_bloc_icone']=3*self.df['largeur_bloc_icone_indiv']+2*dict_config_espace['espace_entre_icone_bloc'][self.taille_globale_carto]
        self.df.loc[(self.df[self.colonne_nb_icone]==7),'largeur_bloc_icone']=4*self.df['largeur_bloc_icone_indiv']+3*dict_config_espace['espace_entre_icone_bloc'][self.taille_globale_carto]
        self.df.loc[(self.df[self.colonne_nb_icone]==8),'largeur_bloc_icone']=4*self.df['largeur_bloc_icone_indiv']+3*dict_config_espace['espace_entre_icone_bloc'][self.taille_globale_carto]

        self.df.loc[(self.df[self.colonne_nb_icone]==0),'hauteur_bloc_icone']=0
        self.df.loc[(self.df[self.colonne_nb_icone]==0),'largeur_bloc_icone']=0

        self.df['largeur_bloc_icone_droit'] = self.df['largeur_bloc_icone']
        self.df['largeur_bloc_icone_biais'] = self.df['largeur_bloc_icone']
        self.df['hauteur_bloc_icone_droit'] = self.df['hauteur_bloc_icone']
        self.df['hauteur_bloc_icone_biais'] = self.df['hauteur_bloc_icone']        
        return self

    def conversion_bloc_icone_to_boite_complete(self):
        for custom in self:
            self[custom] = self[custom].rename({'hauteur_' + self.type + '_' + self.sous_type:'hauteur_boite_complete','largeur_' + self.type + '_' + self.sous_type:'largeur_boite_complete'},axis=1)
        return self

    def conversion_hauteur_largeur_boite_complete_vers_bloc(self):
        for custom in self:
            self[custom] = self[custom].rename({'hauteur_boite_complete':'hauteur_' + self.type + '_' + self.sous_type,'largeur_boite_complete':'largeur_' + self.type + '_' + self.sous_type},axis=1)
        return self

    def placement_bloc_icone_dans_boite(self):
        if len(self.df)>0:
            self.df = self.df.set_geometry('geometry_point_interception')

            #Gauche
            self.df.loc[self.df['type_placement_boite_final']=='G','droite_bloc_' + self.type] = self.df['droite_boite_complete']-dict_config_espace['alinea_bloc_icone_portrait'][self.taille_globale_carto]
            self.df.loc[self.df['type_placement_boite_final']=='G','gauche_bloc_' + self.type] = self.df['droite_boite_complete']-self.df['largeur' + '_' + self.type]-dict_config_espace['alinea_bloc_icone_portrait'][self.taille_globale_carto]
            self.df.loc[self.df['type_placement_boite_final']=='G','haut_bloc_' + self.type] = self.df['haut_boite_complete']-self.df['ecart_hauteur_origine']
            self.df.loc[self.df['type_placement_boite_final']=='G','bas_bloc_' + self.type] = self.df['haut_boite_complete']-self.df['taille_hauteur_bloc_droit']-self.df['ecart_hauteur_origine']

            #Droite
            self.df.loc[self.df['type_placement_boite_final']=='D','droite_bloc_' + self.type] = self.df['gauche_boite_complete']+dict_config_espace['alinea_bloc_icone_portrait'][self.taille_globale_carto]
            self.df.loc[self.df['type_placement_boite_final']=='D','gauche_bloc_' + self.type] = self.df['gauche_boite_complete']+self.df['largeur' + '_' + self.type]+dict_config_espace['alinea_bloc_icone_portrait'][self.taille_globale_carto]
            self.df.loc[self.df['type_placement_boite_final']=='D','haut_bloc_' + self.type] = self.df['haut_boite_complete']-self.df['ecart_hauteur_origine']
            self.df.loc[self.df['type_placement_boite_final']=='D','bas_bloc_' + self.type] = self.df['haut_boite_complete']-self.df['taille_hauteur_bloc_droit']-self.df['ecart_hauteur_origine']

            #Haut
            self.df.loc[self.df['type_placement_boite_final']=='H','droite_bloc_' + self.type] = self.df['geometry_point_interception'].x+self.df['largeur' + '_' + self.type]/2
            self.df.loc[self.df['type_placement_boite_final']=='H','gauche_bloc_' + self.type] = self.df['geometry_point_interception'].x-self.df['largeur' + '_' + self.type]/2
            self.df.loc[self.df['type_placement_boite_final']=='H','haut_bloc_' + self.type] = self.df['bas_boite_complete']+self.df['taille_hauteur_bloc_biais']+self.df['ecart_hauteur_origine']
            self.df.loc[self.df['type_placement_boite_final']=='H','bas_bloc_' + self.type] = self.df['bas_boite_complete']+self.df['ecart_hauteur_origine']

            #Bas
            self.df.loc[self.df['type_placement_boite_final']=='B','droite_bloc_' + self.type] = self.df['geometry_point_interception'].x+self.df['largeur' + '_' + self.type]/2
            self.df.loc[self.df['type_placement_boite_final']=='B','gauche_bloc_' + self.type] = self.df['geometry_point_interception'].x-self.df['largeur' + '_' + self.type]/2
            self.df.loc[self.df['type_placement_boite_final']=='B','haut_bloc_' + self.type] = self.df['haut_boite_complete']-self.df['ecart_hauteur_origine']
            self.df.loc[self.df['type_placement_boite_final']=='B','bas_bloc_' + self.type] = self.df['haut_boite_complete']-self.df['taille_hauteur_bloc_biais']-self.df['ecart_hauteur_origine']

            self.df = self.df.drop(['geometry_point_interception'],axis=1)
            self.df['geometry_bloc_icone'] =  gpd.points_from_xy((self.df['gauche_bloc_' + self.type]+self.df['droite_bloc_' + self.type])/2,(self.df['haut_bloc_' + self.type]+self.df['bas_bloc_' + self.type])/2)
            self.df = self.df.set_geometry('geometry_bloc_icone')      
        return self

    def placement_icones_indiv_dans_bloc_icone(self):
        #La logique est de décaler chaque morceau d'icone indiv au fur et à mesure qu'on les rajoute
        liste_categorie = [x.split("icone_")[1] for x in list(self.df) if x.startswith('icone')]
        df_x_icone_bloc_icone,df_y_icone_bloc_icone = Bloc.creation_dict_placement_position()
        self = Bloc.placement_icone_simple(self,df_x_icone_bloc_icone,df_y_icone_bloc_icone,liste_categorie)
        #Les différents types d'ajout sur le bloc icone
        liste_sous_type = self.sous_type
        for sous_type in liste_sous_type:
            if sous_type=="nombre_actions":
                self = Bloc.ajout_dict_df_icone_nombre_actions(self,liste_categorie,liste_sous_type)
            if sous_type=="avancement":
                self = Bloc.ajout_df_icone_avancement_info_barre(self,liste_categorie,liste_sous_type)
            if sous_type=="pressions_MIA":
                self = Bloc.ajout_df_icone_pressions_MIA_info_barre(self,liste_categorie,liste_sous_type)

        self = Bloc.passage_en_str_position(self,liste_categorie)
        self = Bloc.ajout_attributs_class_colonne_a_garder_bloc_icone(self,liste_categorie)
        return self

##########################################################################################
#bloc_lignes_multiples
##########################################################################################
class BlocLignesMultiples(Bloc):
    def __init__(self,taille_globale_carto):
        super().__init__(taille_globale_carto=taille_globale_carto)
        self.taille_globale_carto = taille_globale_carto   
        self.type = 'bloc_lignes_multiples'

    def set_config_bloc_lignes_multiples(self,boite_complete_maitre,type_icone,thematique,sous_type,colonne_texte):
        self._liste_contenu_boite.append(self)
        self.type_icone = type_icone
        self.thematique = thematique
        self.avancement_max = 4
        self.type = 'bloc_lignes_multiples'
        self.sous_type = sous_type
        self.colonne_texte = colonne_texte
        self.boite_complete_maitre = boite_complete_maitre
        self.echelle_carto = boite_complete_maitre.echelle_carto
        self.colonne_carto = boite_complete_maitre.colonne_carto
        self.orientation = boite_complete_maitre.orientation
        self.nom_boite_maitre = boite_complete_maitre.nom_boite_maitre
        self.liste_nom_colonne_a_garder = []

##########################################################################################
#Fonctions AVANT calcul taille
##########################################################################################
    def garder_actions_phares(self,colonne_texte):
        self = self[self[colonne_texte]!='nan']
        return self

    def casse_lignes_multiples(self):
        #De nice
        colonne_texte = self.colonne_texte
        self.df[colonne_texte] = self.df[colonne_texte].apply(lambda x: x.capitalize())
        return self

    def decoupage_ligne_texte_indiv(self):
        colonne_texte = self.colonne_texte
        liste_texte_indiv = self.df[colonne_texte].to_list()
        liste_texte_indiv = [textwrap.wrap(x, width=dict_config_espace['nombre_caracteres_decoupage_lm'][self.taille_globale_carto]) for x in liste_texte_indiv]
        #On ajoute un signe pour le passage de ligne sur Qgis
        liste_texte_indiv = [[x+'$' for x in liste] for liste in liste_texte_indiv]
        liste_texte_indiv = [[x[:-1]if x is liste[-1] else x for x in liste ] for liste in liste_texte_indiv]
        self.df['lm_decoup_bloc_ligne_multiples'] = [''.join(morceau_liste_texte_lm) for morceau_liste_texte_lm in liste_texte_indiv]
        return self

    def actualisation_nom_colonne_a_garder_bloc_lm_ap(self):
        self.liste_nom_colonne_a_garder.append('Avancement')
        self.liste_nom_colonne_a_garder = list(set(self.liste_nom_colonne_a_garder))
        return self

##########################################################################################
#Fonctions calcul taille
##########################################################################################
    def calcul_taille_lignes_textes_multiples_indiv(self,dict_dict_info_custom):
        self = lignes_multiples.calcul_nb_liste_lignes_multiples(self,self.colonne_texte)
        self = lignes_multiples.extraire_hauteur_largeur_tableau_lignes_multiples(self,self.colonne_texte,self.type,self.sous_type[0])
        self = lignes_multiples.adaptation_hauteur_largeur_lm_indiv_fonction_nb_lignes(self,self.colonne_texte)
        self = lignes_multiples.adaptation_hauteur_largeur_lm_indiv_fonction_orientation(self,self.colonne_texte,dict_dict_info_custom)
        return self

    def calcul_taille_bloc_lignes_multiples(self):
        #Il ne faut pas faire une simple somme des hauteuers en portrait, il faut aussi considérer le nombre de lm par REF et l'espace entre le bloc précedent et le bloc lm, qui dépend du nb de ligne de la premiere lm
        sous_type = self.sous_type[0]
        dict_tempo_portrait = {}
        dict_tempo_paysage = {}
        self.df['nombre_' + sous_type] = 1
        df_temp_portrait = copy.deepcopy(self.df)
        df_temp_paysage = copy.deepcopy(self.df)
        nombre = 'nombre_' + sous_type
        hauteur_droit = 'hauteur_ligne_indiv_droit'
        largeur_droit = 'largeur_ligne_indiv_droit'
        hauteur_biais = 'hauteur_ligne_indiv_biais'
        largeur_biais = 'largeur_ligne_indiv_biais'        
        
        #Ici, c'est technique. Il faut ajouter TOUS les espace en plus qui seront ajoutés plus tard. Cad Chaque lignes indiv, aliné, espace spécial entre bloc et moitié de la premiere lm
        df_temp_portrait_total = df_temp_portrait.groupby("CODE_REF").agg({hauteur_droit : 'sum',largeur_droit:'max',nombre:'sum'})
        df_temp_portrait_total['hauteur_premiere_ligne'] = df_temp_portrait.groupby("CODE_REF").agg({hauteur_droit : 'first'})
        df_temp_portrait_total[hauteur_droit] = df_temp_portrait_total[hauteur_droit] + (df_temp_portrait_total[nombre]-1)*dict_config_espace['espace_entre_actions_phares_portrait'][self.taille_globale_carto] + dict_config_espace['espace_entre_haut_bloc_lm_et_icone_lm'][self.taille_globale_carto]+df_temp_portrait_total['hauteur_premiere_ligne']/2
        df_temp_portrait_total = df_temp_portrait_total.rename({hauteur_droit:"hauteur_bloc_lm_droit",largeur_droit:"largeur_bloc_lm_droit"},axis=1)
        df_temp_portrait_total = df_temp_portrait_total[[x for x in list(df_temp_portrait_total) if x!="hauteur_premiere_ligne"]]
        
        df_temp_paysage_total = df_temp_paysage.groupby("CODE_REF").agg({hauteur_biais : 'max',largeur_biais:'sum',nombre:'sum'})
        df_temp_paysage_total[largeur_biais] = df_temp_paysage_total[largeur_biais] + (df_temp_paysage_total[nombre]-1)*dict_config_espace['espace_entre_actions_phares_paysage'][self.taille_globale_carto] + dict_config_espace['espace_entre_haut_bloc_lm_et_icone_lm'][self.taille_globale_carto]
        df_temp_paysage_total = df_temp_paysage_total.rename({hauteur_biais:"hauteur_bloc_lm_biais",largeur_biais:"largeur_bloc_lm_biais"},axis=1)
        
        self.df = pd.DataFrame(list(set([x for x in self.df['CODE_REF'].to_list()])),columns=["CODE_REF"])
        self.df = pd.merge(self.df,df_temp_portrait_total,left_on='CODE_REF',right_index=True)
        self.df = pd.merge(self.df,df_temp_paysage_total[[x for x in list(df_temp_paysage_total) if x!=nombre]],left_on='CODE_REF',right_index=True)
        return self

    def conversion_bloc_lm_to_boite_complete(self):
        for custom in self:
            self[custom] = self[custom].rename({'hauteur_' + self.type + '_' + self.sous_type:'largeur_boite_complete','largeur_' + self.type + '_' + self.sous_type:'hauteur_boite_complete'},axis=1)
        return self

    def conversion_boite_complete_to_bloc_lm(self):
        for custom in self:
            self[custom] = self[custom].rename({'hauteur_boite_complete':'hauteur_' + self.type + '_' + self.sous_type,'largeur_boite_complete':'largeur_' + self.type + '_' + self.sous_type},axis=1)
        return self

    def placement_bloc_lm_dans_boite(self,dict_dict_info_custom):
        self = Bloc.placement_bloc_lm_avec_calcul_coordonnees_bloc_lm(self)
        self = Bloc.actualisation_point_geometry_bloc_lm(self)
        return self

    def placement_point_icone_dans_bloc_lm(self):
        self = Bloc.ajout_info_geom_boite_dans_df_indiv(self)
        self = Bloc.calcul_origine_phrases_bloc_lignes_multiples(self)
        self = Bloc.actualisation_point_geometry_point_bloc_lm(self)
        self.df_indiv = self.df_indiv[[x for x in list(self.df_indiv) if x!='CODE_ROE']]
        #self.df_indiv.to_file("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/test/test_bloc_lm.shp", encoding='utf-8')        
        return self
