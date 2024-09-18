# -*- coding: utf-8 -*-
import pandas as pd
import geopandas as gpd
import glob

from app.DORApy.classes.modules import custom,dataframe,tableau_excel
from app.DORApy.classes import Class_NGdfREF

from app.DORApy.classes.Class_DictBoiteComplete import DictBoiteComplete
from app.DORApy.classes.Class_Bloc import BlocTexteSimple,BlocIcone,BlocLignesMultiples
from app.DORApy.classes.Class_dictGdfCompletREF import dictGdfCompletREF
from app.DORApy.classes.Class_GdfCompletREF import ListGdfCustom,GdfFondCarte,GdfCompletREF
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes.Class_DictDFTableauxActionsMIA import DictDFTableauxActionsMIA
from app.DORApy.classes.modules import config_DORA
dict_config_espace,dict_config_police = config_DORA.creation_dicts_config()

import os.path
import itertools
import numpy as np
from copy import copy
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import numpy as np
from openpyxl.worksheet.datavalidation import DataValidationList
from openpyxl.styles import NamedStyle
from datetime import date
import os 
ENVIRONMENT = os.getenv('ENVIRONMENT')
import time
start_time = time.time()
import datetime
annee_actuelle = datetime.date.today().year

chemin_dossier = "/mnt/g/travail/carto/projets basiques/PAOT global 5.0/"

##########################################################################################
#Config_projet
##########################################################################################
class DictCustomMaitre(dict):
    @property
    def _constructor(self):
        return DictCustomMaitre
    
    ##########################################################################################
    #Projet : Partie initiation
    ##########################################################################################
    def set_config_type_projet(self,type_rendu,type_donnees=None,thematique=None,public_cible=None,
                               liste_echelle_shp_custom_a_check=None,liste_grand_bassin=['AG'],info_fond_carte=None,echelle_REF=None,echelle_base_REF=None):
        self.type_rendu = type_rendu
        self.type_donnees = type_donnees
        self.thematique = thematique
        self.public_cible = public_cible
        self.liste_echelle_shp_custom_a_check = liste_echelle_shp_custom_a_check
        self.liste_grand_bassin = liste_grand_bassin
        self.info_fond_carte = info_fond_carte
        self.echelle_REF = echelle_REF
        self.echelle_base_REF = echelle_base_REF
        if self.liste_echelle_shp_custom_a_check==['MO']:
            self.taille_carto = 'petite'
        if self.liste_echelle_shp_custom_a_check==['DEP']:
            self.taille_carto = 'grande'
        if type_donnees!=None and thematique!=None and public_cible!=None:
            self.nom_dossier_maitre = type_donnees + '_' + thematique + '_' + public_cible
        return self

    def creation_dict_boite_complete_normal(self,nom_boite_maitre,avancement_max=5,taille_globale_carto='petite'):
        dict_boite_complete = DictBoiteComplete(taille_globale_carto)
        dict_boite_complete.nom_boite_maitre = nom_boite_maitre
        self['dict_boite_maitre_normal'] = dict_boite_complete
        self['dict_boite_maitre_normal'].orientation = 'normal'
        return self

    def creation_dict_boite_complete_orthogonal(self,nom_boite_maitre,avancement_max=5,taille_globale_carto='petite'):
        dict_boite_complete = DictBoiteComplete(taille_globale_carto)
        dict_boite_complete.nom_boite_maitre = nom_boite_maitre
        self['dict_boite_maitre_ortho'] = dict_boite_complete
        self['dict_boite_maitre_ortho'].orientation = 'orthogonal'
        return self    

    def remplissage_bloc_REF_dict_dict_boite_maitre(self,dict_relation_shp_liste,dict_dict_info_custom):
        for nom_custom,entite_custom in self.items():
            CODE_custom = entite_custom.CODE_custom
            for nom_boite,dict_boite in entite_custom.items():
                liste_echelle_base_REF = dict_boite.liste_echelle_REF
                list_tempo_df = [] 
                for echelle_REF in liste_echelle_base_REF:
                    if echelle_REF!='custom':
                        df_tempo = pd.DataFrame(dict_relation_shp_liste['dict_liste_'+ echelle_REF +'_par_custom'][CODE_custom], columns=['CODE_REF'])
                    if echelle_REF=='custom':
                        df_tempo = pd.DataFrame([CODE_custom], columns=['CODE_REF'])
                    df_tempo['echelle_REF'] = echelle_REF
                    list_tempo_df.append(df_tempo)
                df_normal_CODE_REF_du_custom = pd.concat(list_tempo_df)
                dict_boite.df_CODE_REF = df_normal_CODE_REF_du_custom
                for nom_bloc,bloc in dict_boite.items():
                    bloc.df = df_normal_CODE_REF_du_custom
        return self

    def remplissage_boite_REF_dict_dict_boite_maitre(self,dict_relation_shp_liste,dict_dict_info_custom):
        for nom_entite_custom,contenu_custom in self.items():
            for nom_custom,dict_boite in contenu_custom.items():
                liste_df_CODE_REF_tempo = []
                for nom_bloc,dict_bloc in dict_boite.items():
                    liste_df_CODE_REF_tempo.append(dict_bloc.df[['CODE_REF','echelle_REF']])
                df_CODE_REF_tempo = pd.concat(liste_df_CODE_REF_tempo)
                df_CODE_REF_tempo = df_CODE_REF_tempo.drop_duplicates(subset="CODE_REF", keep='first')
                dict_boite.df = df_CODE_REF_tempo
        return self

    def attributs_liste_echelle_REF_projet(self):
        def ajouter_echelle_REF(self,liste_echelle_REF_projet):
            if hasattr(self,"liste_echelle_custom"):
                liste_echelle_REF_projet.extend(self.liste_echelle_custom) 
            for nom_custom,entite_custom in self.items():
                if hasattr(entite_custom,"echelle_REF"):
                    liste_echelle_REF_projet.append(entite_custom.echelle_REF)
                if hasattr(entite_custom,"echelle_base_REF"):
                    liste_echelle_REF_projet.append(entite_custom.echelle_base_REF)  
                for type_boite,dict_boite in entite_custom.items():
                    if hasattr(dict_boite,"liste_echelle_REF"):
                        liste_echelle_REF_projet.extend(dict_boite.liste_echelle_REF)
            return liste_echelle_REF_projet
        
        liste_echelle_REF_projet = []
        if (self.type_rendu=='carte' and self.type_donnees=='action') or self.type_rendu=='verif_tableau_DORA':
            liste_echelle_REF_projet = ['SAGE','MO','PPG','BVG','ME','SME']
            liste_echelle_REF_projet.extend(self.liste_echelle_shp_custom_a_check)
            liste_echelle_REF_projet = list(set(liste_echelle_REF_projet))

        if (self.type_rendu=='carte' and self.type_donnees=='toutes_pressions'):
            liste_echelle_REF_projet = ['ME']

        if self.type_rendu=='tableau_vierge' and self.type_donnees=='action':
            liste_echelle_REF_projet = ['MO','SAGE','PPG','BVG','ME','ROE']
            liste_echelle_REF_projet = ajouter_echelle_REF(self,liste_echelle_REF_projet)
            for nom_custom,entite_custom in self.items():
                if hasattr(entite_custom,"echelle_REF"):
                    liste_echelle_REF_projet.append(entite_custom.echelle_base_REF)
        if self.type_rendu=='tableau_DORA_vers_BDD' and self.type_donnees=='action':
            liste_echelle_REF_projet = ['SAGE','MO','PPG','BVG','ME','SME']
            for nom_custom,entite_custom in self.items():
                if hasattr(entite_custom,"echelle_REF"):
                    liste_echelle_REF_projet.append(entite_custom.echelle_base_REF)             
        if self.type_rendu=='tableau_MAJ_Osmose':
            liste_echelle_REF_projet = ['MO','SAGE','PPG','BVG','ME','ROE']            
            
        self.liste_echelle_REF_projet = list(set(liste_echelle_REF_projet))
        return self

    def attributs_liste_echelle_base_REF(self):
        if self.type_rendu=='carte':
            liste_echelle_base_REF = list({k:v.echelle_base_REF for k,v in self.items()}.values())
            liste_echelle_base_REF = list(set(liste_echelle_base_REF))
            self.liste_echelle_base_REF = liste_echelle_base_REF
        return self

    def definition_attributs_liste_echelle_boite_par_custom(self,dict_dict_info_custom):
        if self.type_rendu=='carte' and self.type_donnees=='action' and self.thematique=='MIA':
            if self.liste_echelle_custom == ['MO']:
                for nom_custom,entite_custom in self.items():
                    CODE_custom = entite_custom.CODE_custom
                    for type_boite,dict_boite in entite_custom.items():
                        if dict_dict_info_custom[CODE_custom]['PPG_inclus_dans_integral_custom'] == True:
                            if dict_boite.orientation=="normal":
                                dict_boite.liste_echelle_boite = [entite_custom.echelle_base_REF]
                            if dict_boite.orientation=="orthogonal":
                                dict_boite.liste_echelle_boite = ['PPG','custom']
                        if dict_dict_info_custom[CODE_custom]['PPG_inclus_dans_integral_custom'] == False:
                            if dict_boite.orientation=="normal":
                                dict_boite.liste_echelle_boite = [entite_custom.echelle_base_REF,"PPG"]
                            if dict_boite.orientation=="orthogonal":
                                dict_boite.liste_echelle_boite = ['custom']
            if self.liste_echelle_custom == ['DEP']:
                for nom_custom,entite_custom in self.items():
                    CODE_custom = entite_custom.CODE_custom
                    for type_boite,dict_boite in entite_custom.items():
                        dict_boite.liste_echelle_boite = ["MO"]
            
        if self.type_donnees!='action':
            for nom_custom,entite_custom in self.items():
                CODE_custom = entite_custom.CODE_custom
                for nom_boite_maitre,dict_boite_complete in self.items():
                    self[CODE_custom]['liste_echelle_boite_normal'] = [self.echelle_base_REF]
        return self
    ##########################################################################################
    #Projet : Création des boites
    ##########################################################################################
    def creation_boite_projet_carto(self):
        if self.type_rendu=='carte':
            if self.liste_echelle_shp_custom_a_check==['MO']:
                taille_globale_carto = "petite"
            if self.liste_echelle_shp_custom_a_check==['DEP']:
                taille_globale_carto = "grande"

            if self.type_donnees=='toutes_pressions' and self.liste_echelle_base_REF==['ME']:
                for nom_custom,entite_custom in self.items():
                    entite_custom = DictCustomMaitre.creation_dict_boite_complete_normal(entite_custom,nom_boite_maitre='dict_boite_complete_pressions_globales')
                for nom_custom,entite_custom in self.items():
                    entite_custom = NomCustomMaitre.creation_bloc_texte_simple(entite_custom,orientation="normal",type_icone='texte_simple',sous_type=['NOM_REF'],colonne_texte='nom_simple_REF',nom_custom=nom_custom)
                    entite_custom = NomCustomMaitre.creation_bloc_icone(entite_custom,orientation="normal",type_icone='icone_pression',sous_type=["pressions"],colonne_nb_icone='NB_type_icone',nom_custom=nom_custom)

            if self.type_donnees=='action' and self.liste_echelle_shp_custom_a_check==['MO'] and any(x in self.liste_echelle_base_REF for x in ['ME','SME']):
                for nom_custom,entite_custom in self.items():
                    entite_custom = DictCustomMaitre.creation_dict_boite_complete_normal(entite_custom,nom_boite_maitre='dict_boite_complete_action_MIA')
                    entite_custom = DictCustomMaitre.creation_dict_boite_complete_orthogonal(entite_custom,nom_boite_maitre='dict_boite_complete_action_ortho',taille_globale_carto=taille_globale_carto)
                for nom_custom,entite_custom in self.items():
                    entite_custom = NomCustomMaitre.creation_bloc_texte_simple(entite_custom,orientation="normal",type_icone='texte_simple',sous_type=['NOM_REF'],colonne_texte='nom_simple_REF',nom_custom=nom_custom)
                    entite_custom = NomCustomMaitre.creation_bloc_texte_simple(entite_custom,orientation="orthogonal",type_icone='texte_simple',sous_type=['NOM_REF'],colonne_texte='nom_simple_REF',nom_custom=nom_custom)
                    entite_custom = NomCustomMaitre.creation_bloc_icone(entite_custom,orientation="normal",type_icone='icone_action_MIA',sous_type=['nombre_actions','avancement'],colonne_nb_icone='NB_type_icone',nom_custom=nom_custom)
                    entite_custom = NomCustomMaitre.creation_bloc_icone(entite_custom,orientation="orthogonal",type_icone='icone_action_MIA',sous_type=['nombre_actions','avancement'],colonne_nb_icone='NB_type_icone',nom_custom=nom_custom) 
                    entite_custom = NomCustomMaitre.creation_bloc_lignes_multiples(entite_custom,orientation="normal",type_icone='ap_MIA',sous_type=['actions_phares'],colonne_texte='description_action_phare',nom_custom=nom_custom)
                    entite_custom = NomCustomMaitre.creation_bloc_lignes_multiples(entite_custom,orientation="orthogonal",type_icone='ap_MIA',sous_type=['actions_phares'],colonne_texte='description_action_phare',nom_custom=nom_custom)
            if self.type_donnees=='action' and self.liste_echelle_shp_custom_a_check==['DEP'] and self.liste_echelle_base_REF==['MO']:
                for nom_custom,entite_custom in self.items():
                    entite_custom = DictCustomMaitre.creation_dict_boite_complete_normal(entite_custom,nom_boite_maitre='dict_boite_complete_action_MIA',taille_globale_carto=taille_globale_carto)
                    entite_custom = DictCustomMaitre.creation_dict_boite_complete_orthogonal(entite_custom,nom_boite_maitre='dict_boite_complete_action_ortho',taille_globale_carto=taille_globale_carto)
                for nom_custom,entite_custom in self.items():
                    entite_custom = NomCustomMaitre.creation_bloc_texte_simple(entite_custom,orientation="normal",type_icone='texte_simple',sous_type=['NOM_REF'],colonne_texte='nom_simple_REF',nom_custom=nom_custom,taille_globale_carto=taille_globale_carto)
                    entite_custom = NomCustomMaitre.creation_bloc_icone(entite_custom,orientation="normal",type_icone='icone_action_MIA',sous_type=['nombre_actions','pressions_MIA'],colonne_nb_icone='NB_type_icone',nom_custom=nom_custom,taille_globale_carto=taille_globale_carto)
                    entite_custom = NomCustomMaitre.creation_bloc_texte_simple(entite_custom,orientation="orthogonal",type_icone='texte_simple',sous_type=['NOM_REF'],colonne_texte='nom_simple_REF',nom_custom=nom_custom,taille_globale_carto=taille_globale_carto)
                    entite_custom = NomCustomMaitre.creation_bloc_icone(entite_custom,orientation="orthogonal",type_icone='icone_action_MIA',sous_type=['nombre_actions','pressions_MIA'],colonne_nb_icone='NB_type_icone',nom_custom=nom_custom,taille_globale_carto=taille_globale_carto) 
        return self
    
    def definition_liste_echelle_boite_projet_carto(self,dict_relation_shp_liste):
        if self.type_rendu=='carte':
            for nom_custom,entite_custom in self.items():
                if self.type_donnees=='action' and self.liste_echelle_shp_custom_a_check==['MO'] and any(x in self.liste_echelle_base_REF for x in ['ME','SME']):
                    for type_boite,dict_boite in entite_custom.items():
                        if len(dict_relation_shp_liste['dict_liste_PPG_par_custom'][entite_custom.CODE_custom])>1:
                            if dict_boite.orientation == "normal":
                                self[nom_custom][type_boite].liste_echelle_REF = ["PPG",entite_custom.echelle_base_REF]
                            if dict_boite.orientation == "orthogonal":
                                self[nom_custom][type_boite].liste_echelle_REF = ["MO"]   
                        if len(dict_relation_shp_liste['dict_liste_PPG_par_custom'][entite_custom.CODE_custom])<2:
                            if dict_boite.orientation == "normal":
                                self[nom_custom][type_boite].liste_echelle_REF = [entite_custom.echelle_base_REF]
                            if dict_boite.orientation == "orthogonal":
                                self[nom_custom][type_boite].liste_echelle_REF = ["PPG","MO"]                                                                                         
                if self.type_donnees=='action' and self.liste_echelle_shp_custom_a_check==['DEP'] and self.liste_echelle_base_REF==['MO']:
                    for type_boite,dict_boite in entite_custom.items():
                        if dict_boite.orientation == "normal":
                            dict_boite.liste_echelle_REF = ['MO']
                        if dict_boite.orientation == "orthogonal":
                            dict_boite.liste_echelle_REF = ['DEP']       
                if self.type_donnees=='toutes_pressions':
                    for type_boite,dict_boite in entite_custom.items():
                        if dict_boite.orientation == "normal":
                            dict_boite.liste_echelle_REF = ['ME']
        return self    

    def initialisation_bloc_avec_liste_entite_base_REF(dict_custom_maitre,dict_relation_shp_liste):
        for nom_custom,entite_custom in dict_custom_maitre.items():
            CODE_custom = entite_custom.CODE_custom
            if 'dict_boite_maitre_normal' in entite_custom:
                liste_echelle_boite_normal = entite_custom['dict_boite_maitre_normal'].liste_echelle_REF
                liste_df_boite_normal = []                
                for echelle_boite_normal in liste_echelle_boite_normal:
                    df_normal_CODE_REF_du_custom = pd.DataFrame(dict_relation_shp_liste['dict_liste_'+ echelle_boite_normal +'_par_custom'][CODE_custom], columns=['CODE_'+echelle_boite_normal])
                    df_normal_CODE_REF_du_custom = df_normal_CODE_REF_du_custom.rename({'CODE_'+echelle_boite_normal:'CODE_REF'},axis=1)
                    df_normal_CODE_REF_du_custom['echelle_REF']=echelle_boite_normal
                    liste_df_boite_normal.append(df_normal_CODE_REF_du_custom)
                df_normal_CODE_REF_du_custom = pd.concat(liste_df_boite_normal)
                for nom_boite_maitre,bloc in entite_custom['dict_boite_maitre_normal'].items():
                    bloc.df = df_normal_CODE_REF_du_custom

            
            if 'dict_boite_maitre_ortho' in entite_custom:
                liste_echelle_boite_ortho = entite_custom['dict_boite_maitre_ortho'].liste_echelle_REF
                liste_df_boite_ortho = []
                for echelle_boite_ortho in liste_echelle_boite_ortho:
                    if echelle_boite_ortho==entite_custom.echelle_REF:
                        df_ortho_CODE_REF_du_custom = pd.DataFrame([entite_custom.CODE_custom],columns=['CODE_REF'])
                    if echelle_boite_ortho!=entite_custom.echelle_REF:
                        df_ortho_CODE_REF_du_custom = pd.DataFrame(dict_relation_shp_liste['dict_liste_'+ echelle_boite_ortho +'_par_custom'][CODE_custom], columns=['CODE_'+echelle_boite_ortho])
                        df_ortho_CODE_REF_du_custom = df_ortho_CODE_REF_du_custom.rename({'CODE_'+echelle_boite_ortho:'CODE_REF'},axis=1)
                    df_ortho_CODE_REF_du_custom['echelle_REF']=echelle_boite_ortho
                    liste_df_boite_ortho.append(df_ortho_CODE_REF_du_custom)
                df_ortho_CODE_REF_du_custom = pd.concat(liste_df_boite_ortho)
                for nom_boite_maitre,bloc in entite_custom['dict_boite_maitre_ortho'].items():
                    bloc.df = df_ortho_CODE_REF_du_custom
        return dict_custom_maitre

    def repartition_df_donnees_dans_bloc(self,dict_df_donnees,dict_dict_info_REF,dict_decoupREF,dict_relation_shp_liste):
        for nom_custom,entite_custom in self.items():
            for nom_boite,dict_boite in entite_custom.items():
                for nom_bloc,dict_bloc in dict_boite.items():
                    if dict_bloc.type=='bloc_texte_simple':
                        dict_bloc.df = pd.merge(dict_bloc.df,dict_df_donnees['df_nom_REF_simple'],on='CODE_REF')
                    if dict_bloc.type=='bloc_icone' or dict_bloc.type=='bloc_lignes_multiples':
                        if self.type_donnees=="actions":
                            df_BDD_DORA_custom = DictDFTableauxActionsMIA.selection_actions_BDD_DORA(dict_df_donnees,entite_custom,dict_dict_info_REF,dict_decoupREF,dict_relation_shp_liste)
                            dict_bloc.df = pd.merge(dict_bloc.df,df_BDD_DORA_custom,on='CODE_REF')
                        if self.type_donnees=="toutes_pressions":
                            dict_bloc.df = pd.merge(dict_bloc.df,dict_df_donnees['df_pression'],on='CODE_REF')
                        if len(dict_bloc.df)==0:
                            print("attention, le "+ nom_bloc + " est vide pour le " + nom_boite)
        return self

    def traitement_special_bloc_ortho_si_plusieurs_echelle(self,dict_relation_shp_liste):
        for nom_custom,entite_custom in self.items():
            for nom_boite,dict_boite in entite_custom.items():
                if dict_boite.orientation=="orthogonal" and len(dict_boite.liste_echelle_REF)>1:
                    liste_echelle_REF = dictGdfCompletREF.hierarchisation_liste_echelle(dict_boite.liste_echelle_REF)
                    for nom_bloc,dict_bloc in dict_boite.items():
                        if dict_bloc.type=='bloc_texte_simple':
                            dict_bloc.df = dict_bloc.df.loc[dict_bloc.df["echelle_REF"]==liste_echelle_REF[-1]]
                        if dict_bloc.type=='bloc_icone' or dict_bloc.type=='bloc_lignes_multiples':
                            dict_bloc.df["echelle_REF"]==liste_echelle_REF[-1]
                            dict_bloc.df["CODE_REF"] = dict_relation_shp_liste['dict_liste_' + liste_echelle_REF[-1] + '_par_custom'][entite_custom.CODE_custom][0]
        return self    
    

    def traitement_bloc_avant_calcul_taille(self,dict_df_donnees,dict_relation_shp_liste):
        ##########################################################################################
        #Dict info bloc icone : fonction pour tableau pression
        ##########################################################################################
        def creation_liste_type_icone_toutes_pressions_toutes_pressions(self,public_cible):
            liste_categorie = ['dom','ind','azo','phy','irr','hyd']
            return(liste_categorie)

        def ajout_num_par_categorie_pression_toutes_pressions(self,liste_categorie):
            self[['icone_' + categorie for categorie in liste_categorie]] = self[['icone_' + categorie for categorie in liste_categorie]].replace(0, np.nan)
            self[['num_' + categorie for categorie in liste_categorie]] = self[['icone_' + categorie for categorie in liste_categorie]].cumsum(axis = 1)
            self[['icone_' + categorie for categorie in liste_categorie]] = self[['icone_' + categorie for categorie in liste_categorie]].replace(np.nan, 0)
            self[['num_' + categorie for categorie in liste_categorie]] = self[['num_' + categorie for categorie in liste_categorie]].replace(np.nan, 0)
            self[['num_' + categorie for categorie in liste_categorie]] = self[['num_' + categorie for categorie in liste_categorie]].astype(int)
            return self

        ##########################################################################################
        #Dict info bloc icone : fonction pour pression global
        ##########################################################################################
        def actualisation_liste_nom_colonne_a_garder_bloc_icone_pression_global(self,liste_categorie):
            self.liste_nom_colonne_a_garder.extend(['P_MORPHO','P_HYDRO','P_CONTI'])
            for categorie in liste_categorie:
                self.liste_nom_colonne_a_garder.extend(['icone_' + categorie])
            self.liste_nom_colonne_a_garder = list(set(self.liste_nom_colonne_a_garder))
            return self

        ##########################################################################################
        #Dict info bloc texte simple : Fonctions tableau texte simple
        ##########################################################################################
        for nom_entite_custom,contenu_custom in self.items():
            for nom_custom,dict_boite in contenu_custom.items():
                for nom_bloc,dict_bloc in dict_boite.items():
                    if dict_bloc.type == "bloc_texte_simple":
                        dict_bloc = BlocTexteSimple.decoupage_bloc_texte_ligne_simple(dict_bloc)

                ##########################################################################################
                #Dict info bloc icone : Fonctions bloc icone
                ##########################################################################################
                    if dict_bloc.type == "bloc_icone":
                        if dict_bloc.type_icone=="icone_action_MIA":
                            liste_categorie = BlocIcone.creation_liste_type_icone_nombres_actions_MIA(self)
                            dict_bloc = BlocIcone.conversion_typologie_actions_MIA(dict_bloc,self.public_cible,liste_categorie)    

                        if dict_bloc.type_icone=="icone_pression":
                            liste_categorie = BlocIcone.creation_liste_type_icone_toutes_pressions(self)

                        if "avancement" in dict_bloc.sous_type and self.thematique == "MIA":
                            dict_bloc = BlocIcone.conversion_niveau_avancement_tableau_actions(dict_bloc,annee_actuelle)
                        
                        liste_df_info_sup_icone = []
                        if "nombre_actions" in dict_bloc.sous_type and self.thematique == "MIA":  
                            df_bloc_avancement = BlocIcone.creation_dict_compte_chaque_categorie_et_avancement_nombres_actions(dict_bloc.df,liste_categorie,dict_bloc.avancement_max)
                            liste_df_info_sup_icone.append(df_bloc_avancement)

                        if "pressions_MIA" in dict_bloc.sous_type and self.thematique == "MIA":  
                            df_bloc_pressions_MIA = BlocIcone.indications_nombre_echelle_REF_avec_pression(dict_bloc,liste_categorie,dict_df_donnees,dict_boite.df_CODE_REF,dict_relation_shp_liste)                        
                            liste_df_info_sup_icone.append(df_bloc_pressions_MIA)

                        if dict_bloc.type_icone=="icone_action_MIA":
                            dict_bloc = BlocIcone.rassemblement_et_ajout_df_sup(dict_bloc,liste_categorie,liste_df_info_sup_icone,self.liste_contenu_bloc)
                        dict_bloc.df = BlocIcone.ajout_si_icone_par_categorie(dict_bloc.df,liste_categorie,dict_bloc.type_icone)
                        dict_bloc.df = BlocIcone.ajout_numero_par_binome_categorie(dict_bloc.df,liste_categorie,self.liste_contenu_bloc)
                        if dict_bloc.type_icone=="icone_pression":
                            dict_bloc.df = BlocIcone.garder_type_specifique_action(dict_bloc.df,liste_categorie)

                        if "nombre_actions" in dict_bloc.sous_type:
                            dict_bloc = BlocIcone.actualisation_liste_nom_colonne_a_garder_bloc_icone_nombres_actions(dict_bloc,liste_categorie)
                        if "avancement" in dict_bloc.sous_type:
                            dict_bloc = BlocIcone.actualisation_liste_nom_colonne_a_garder_bloc_icone_avancement(dict_bloc,liste_categorie) 
                        if "pressions" in dict_bloc.sous_type:
                            dict_bloc = BlocIcone.actualisation_liste_nom_colonne_a_garder_bloc_icone_pressions(dict_bloc,liste_categorie)                                                              

                    ##########################################################################################
                    #Dict info bloc phrases multiples : Fonctions bloc multiples lignes
                    ##########################################################################################
                    if dict_bloc.type == "bloc_lignes_multiples":
                        if "actions_phares" in dict_bloc.sous_type:
                            dict_bloc.df = BlocLignesMultiples.garder_actions_phares(dict_bloc.df,dict_bloc.colonne_texte)
                        if "actions_phares" in dict_bloc.sous_type and self.thematique == "MIA":
                            dict_bloc = BlocLignesMultiples.conversion_niveau_avancement_tableau_actions(dict_bloc,annee_actuelle)
                            dict_bloc = BlocLignesMultiples.conversion_typologie_actions_MIA(dict_bloc,self.public_cible,liste_categorie)
                            dict_bloc = BlocLignesMultiples.casse_lignes_multiples(dict_bloc)
                            dict_bloc = BlocLignesMultiples.decoupage_ligne_texte_indiv(dict_bloc)
                            dict_bloc = BlocLignesMultiples.actualisation_nom_colonne_a_garder_bloc_lm_ap(dict_bloc)
        return self

##########################################################################################
#Focntions travail geometries
##########################################################################################
    def suppression_blocs_vides(self):
        for nom_entite_custom in list(self):
            for nom_custom in list(self[nom_entite_custom]):
                for nom_bloc in list(self[nom_entite_custom][nom_custom]):
                    if len(self[nom_entite_custom][nom_custom][nom_bloc].df)==0:
                        del self[nom_entite_custom][nom_custom][nom_bloc]
        return self

    def ajout_infos_geometriques_decoupREF_boite_normal(self,dict_decoupREF,dict_df_buffer_custom,df_info_custom):
        if self.type_rendu=='carte':
            for nom_entite_custom,contenu_custom in self.items():
                for nom_boite,dict_boite in contenu_custom.items():
                    if dict_boite.orientation == 'normal':
                        liste_tempo_REF = []
                        for echelle_REF in dict_boite.liste_echelle_REF:
                            df_info_decoupREF = dict_decoupREF['gdf_decoup' + echelle_REF + '_custom']
                            df_info_decoupREF = df_info_decoupREF.gdf.rename({x:x.replace(echelle_REF, 'REF') for x in list(df_info_decoupREF.gdf) if echelle_REF in x},axis=1)
                            liste_tempo_REF.append(df_info_decoupREF)
                        df_info_decoupREF_total = pd.concat(liste_tempo_REF)
                        
                        dict_boite.df = pd.merge(dict_boite.df,df_info_decoupREF_total.loc[df_info_decoupREF_total["NOM_custom"]==nom_entite_custom],on='CODE_REF',how='left',suffixes=[None,'_a_supprimer'])
                        dict_boite.df = dict_boite.df.loc[:,~dict_boite.df.columns.str.endswith('_a_supprimer')]
                        dict_boite.df = dict_boite.df.set_geometry('geometry')
                        dict_boite.df['centre_decoupREF'] = dict_boite.df.representative_point()
                        dict_boite.df['X_centre_decoupREF']=dict_boite.df['centre_decoupREF'].x
                        dict_boite.df['Y_centre_decoupREF']=dict_boite.df['centre_decoupREF'].y
                        dict_boite.df = pd.merge(dict_boite.df,df_info_custom,on='NOM_custom',suffixes=[None,'_a_supprimer'])
                        dict_boite.df = dict_boite.df.loc[:,~dict_boite.df.columns.str.endswith('_a_supprimer')]
                        dict_boite = dictGdfCompletREF.definition_gauche_droite_haut_bas_decoupREF_par_rapport_au_custom(dict_boite,dict_df_buffer_custom,contenu_custom.CODE_custom)
                        liste_colonne_info_geom = ['NOM_custom','echelle_REF','orient_custom','X_centre_decoupREF','Y_centre_decoupREF','orient_GD','orient_BH','X_centre_custom','Y_centre_custom']
                        dict_boite.liste_colonne_info_geom = liste_colonne_info_geom
                        dict_boite.df = dict_boite.df[liste_colonne_info_geom + ['CODE_REF']]
            return self
        else:
            return None
        
    def ajout_infos_boite_ortho(self,dict_decoupREF,dict_dict_info_custom,df_info_custom,projet):
        if projet.type_rendu=='carte':
            for nom_entite_custom,contenu_custom in self.items():
                for nom_boite,dict_boite in contenu_custom.items():
                    if dict_boite.orientation == 'orthogonal':
                        liste_tempo_REF = []
                        liste_echelle_ortho_sans_custom = dict_boite.liste_echelle_boite
                        liste_echelle_ortho_sans_custom = [x for x in liste_echelle_ortho_sans_custom if x !='custom']
                        if len(liste_echelle_ortho_sans_custom)>0:
                            for echelle_REF in liste_echelle_ortho_sans_custom:
                                df_info_decoupREF = dict_decoupREF['gdf_decoup' + echelle_REF + '_custom']
                                df_info_decoupREF = df_info_decoupREF.rename({x:x.replace(echelle_REF, 'REF') for x in list(df_info_decoupREF) if echelle_REF in x},axis=1)
                                liste_tempo_REF.append(df_info_decoupREF)
                            df_info_decoupREF_total = pd.concat(liste_tempo_REF)
                            dict_boite.df = pd.merge(dict_boite.df,df_info_decoupREF_total,on='CODE_REF',how='left')
                        df_info_custom_avec_CODE_REF = df_info_custom.rename({'CODE_custom':'CODE_REF'},axis=1)
                        dict_boite.df = pd.merge(dict_boite.df,df_info_custom_avec_CODE_REF,on='CODE_REF',suffixes=[None,'_a_supprimer'],how='left')
                        dict_boite.df = dict_boite.df.loc[:,~dict_boite.df.columns.str.endswith('_a_supprimer')]
                        liste_colonne_info_geom = ['NOM_custom','echelle_REF','orient_custom','X_centre_custom','Y_centre_custom']
                        dict_boite.liste_colonne_info_geom = liste_colonne_info_geom
                        dict_boite.df = dict_boite.df[liste_colonne_info_geom + ['CODE_REF']]
            return self
        
    def calcul_taille_bloc(self,dict_dict_info_custom):
        for nom_entite_custom,contenu_custom in self.items():
            for nom_boite_maitre,dict_boite_maitre in contenu_custom.items():
                for nom_bloc,dict_bloc in dict_boite_maitre.items():
                    if dict_bloc.type == 'bloc_texte_simple':
                        if "NOM_REF" in dict_bloc.sous_type:
                            dict_bloc = BlocTexteSimple.calcul_taille_bloc_texte_simple(dict_bloc)
                    if dict_bloc.type == 'bloc_icone':
                        dict_bloc = BlocIcone.calcul_taille_bloc_icone(dict_bloc)
                    if dict_bloc.type == 'bloc_lignes_multiples':
                        dict_bloc = BlocLignesMultiples.calcul_taille_lignes_textes_multiples_indiv(dict_bloc,dict_dict_info_custom)
                        #Dedoublement du df pour avoir ap indiv ET ap en groupe par REF de base
                        dict_bloc.df_indiv = dict_bloc.df
                        dict_bloc = BlocLignesMultiples.calcul_taille_bloc_lignes_multiples(dict_bloc)
        return self

    def calcul_taille_boite_complete(self,dict_dict_info_custom):
        for nom_entite_custom,contenu_custom in self.items():
            contenu_custom = DictBoiteComplete.rassemblement_par_boite_complete(contenu_custom)
            contenu_custom = DictBoiteComplete.suppression_boite_complete_vide(contenu_custom)
        return self
    
    def ajout_contour_geometry_boite_complete(self,type_boite_placement:list=['normal']):
        for nom_entite_custom,contenu_custom in self.items():
            contenu_custom = DictBoiteComplete.creation_df_contour(contenu_custom,type_boite_placement)
            contenu_custom = DictBoiteComplete.import_hauteur_deviation(contenu_custom,type_boite_placement)
            contenu_custom= DictBoiteComplete.creation_contour_boite_complete(contenu_custom,type_boite_placement)
        return self   
    
    def replacement_eventuel_boite(self,type_boite_placement:list=['normal']):
        for nom_entite_custom,contenu_custom in self.items():
            contenu_custom = DictBoiteComplete.decalage_contour_si_contact(contenu_custom,type_boite_placement)
            contenu_custom = DictBoiteComplete.transfert_info_geom_dans_df(contenu_custom,type_boite_placement)
            '''for nom_boite_maitre,dict_boite_maitre in contenu_custom.items():
                if dict_boite_maitre.orientation=="normal":
                    dict_boite_maitre = DictBoiteComplete.actualisation_bas_haut_gauche_droite(dict_boite_maitre)
                    dict_boite_maitre = DictBoiteComplete.recuperation_bas_haut_gauche_droite_dans_df_contour(dict_boite_maitre)'''
        return self

    def actualisation_info_geom_dans_bloc(self,type_boite_placement:list=['normal']):
        #Faut actualiser gauche,droite et point interception par boite
        for nom_entite_custom,contenu_custom in self.items():
            for nom_boite_maitre,dict_boite_maitre in contenu_custom.items():
                if dict_boite_maitre.orientation in type_boite_placement:
                    df_boite_normal = dict_boite_maitre.df
                    for nom_bloc,dict_bloc in dict_boite_maitre.items():
                        dict_bloc.df = pd.merge(dict_bloc.df,df_boite_normal[["CODE_REF",'geometry_point_interception','haut_boite_complete','bas_boite_complete','gauche_boite_complete','droite_boite_complete']],on="CODE_REF",suffixes=['_a_supprimer',None])
                        dict_bloc.df = dict_bloc.df.loc[:,~dict_bloc.df.columns.str.endswith('_a_supprimer')]
        return self
    
    def suppression_custom_a_reduire_boite_complete(self,dict_dict_info_custom):
        dict_CODE_custom_a_enlever = {}
        for nom_boite_maitre,dict_boite_maitre in self.items():
            dict_CODE_custom_a_enlever[nom_boite_maitre] = []
            for CODE_custom,df_custom in dict_boite_maitre.boite_complete.items():
                if dict_dict_info_custom[CODE_custom]['custom_a_reduire'] == True:
                    dict_CODE_custom_a_enlever[nom_boite_maitre].append(CODE_custom)

        for nom_boite_maitre,dict_boite_maitre in dict_CODE_custom_a_enlever.items():
            for CODE_custom in dict_boite_maitre:
                del self[nom_boite_maitre].boite_complete[CODE_custom]

        dict_CODE_custom_a_enlever = {}
        for nom_boite_maitre,dict_boite_maitre in self.items():
            dict_CODE_custom_a_enlever[nom_boite_maitre] = {}
            for nom_bloc,dict_bloc in dict_boite_maitre.items():
                dict_CODE_custom_a_enlever[nom_boite_maitre][nom_bloc] = []
                for CODE_custom,df_custom in dict_bloc.items():
                    if dict_dict_info_custom[CODE_custom]['custom_a_reduire'] == True:
                        dict_CODE_custom_a_enlever[nom_boite_maitre][nom_bloc].append(CODE_custom)

        for nom_boite_maitre,dict_boite_maitre in dict_CODE_custom_a_enlever.items():
            for nom_bloc,dict_bloc in dict_boite_maitre.items():
                for CODE_custom in dict_bloc:
                    del self[nom_boite_maitre][nom_bloc][CODE_custom]

        return self        
    
#################################################################################################################
#Placement : Le boss niveau
#################################################################################################################
    def definition_point_ancrage_complet_REF_entre_eux(self,dict_dict_info_custom,dict_df_buffer_custom):
        for nom_entite_custom,contenu_custom in self.items():
            df_info_custom = dict_dict_info_custom[contenu_custom.CODE_custom]
            gdf_buffer = dict_df_buffer_custom[contenu_custom.CODE_custom]
            for nom_boite_maitre,dict_boite_maitre in contenu_custom.items():
                if dict_boite_maitre.orientation=="normal":
                    #On trace des lignes verticales si portrait, et horizontales si paysage
                    dict_boite_maitre = DictBoiteComplete.ajout_colonne_placement_boite_final(dict_boite_maitre)
                    dict_boite_maitre = DictBoiteComplete.placement_boite_complet_ME_entre_eux(dict_boite_maitre,df_info_custom,"placement_boite_classique")
                    dict_boite_maitre = DictBoiteComplete.tracer_ligne_pour_intersection_buffer(dict_boite_maitre,df_info_custom,"placement_boite_classique")
                    #On a placé des lignes (méridiens ou paralléles suivants paysage ou portrait)
                    dict_boite_maitre = DictBoiteComplete.intersection_ligne_buffer(dict_boite_maitre,gdf_buffer,df_info_custom,"placement_boite_classique")
                    dict_boite_maitre = DictBoiteComplete.gestion_erreurs_interceptions_ligne_buffer(dict_boite_maitre,df_info_custom,"placement_boite_classique")
                    dict_boite_maitre = DictBoiteComplete.extraction_liste_coord_apres_interception(dict_boite_maitre,df_info_custom,"placement_boite_classique")
                    dict_boite_maitre = DictBoiteComplete.actualisation_orient_GD_et_BH(dict_boite_maitre,df_info_custom)
                    dict_boite_maitre = DictBoiteComplete.calcul_nombre_boite_qui_depassent_a_deplacer(dict_boite_maitre,df_info_custom)
                    dict_boite_maitre = DictBoiteComplete.calcul_valeur_limite_si_boite_a_replacer(dict_boite_maitre,df_info_custom)
                    dict_boite_maitre = DictBoiteComplete.actualisation_hauteur_et_largeur_boites_normales_qui_depassent(dict_boite_maitre,df_info_custom)
                    dict_boite_maitre = DictBoiteComplete.placement_boite_complet_ME_entre_eux(dict_boite_maitre,df_info_custom,"placement_boite_extremite_qui_depassent")
                    dict_boite_maitre = DictBoiteComplete.tracer_ligne_pour_intersection_buffer(dict_boite_maitre,df_info_custom,"placement_boite_extremite_qui_depassent")
                    dict_boite_maitre = DictBoiteComplete.intersection_ligne_buffer(dict_boite_maitre,gdf_buffer,df_info_custom,"placement_boite_extremite_qui_depassent")
                    dict_boite_maitre = DictBoiteComplete.gestion_erreurs_interceptions_ligne_buffer(dict_boite_maitre,df_info_custom,"placement_boite_extremite_qui_depassent")
                    dict_boite_maitre = DictBoiteComplete.extraction_liste_coord_apres_interception(dict_boite_maitre,df_info_custom,"placement_boite_extremite_qui_depassent")
                    dict_boite_maitre = DictBoiteComplete.calcul_limite_boites_extremitees(dict_boite_maitre,df_info_custom)
                    dict_boite_maitre = DictBoiteComplete.replacement_boites_extremitees(dict_boite_maitre,df_info_custom)
                    dict_boite_maitre = DictBoiteComplete.creation_point_unique_par_REF(dict_boite_maitre,df_info_custom)
                    '''dict_boite_maitre = DictBoiteComplete.actualisation_type_placement_boite_final(dict_boite_maitre,df_info_custom)
                    dict_boite_maitre = DictBoiteComplete.actualisation_bas_haut_gauche_droite(dict_boite_maitre)
                    dict_boite_maitre = DictBoiteComplete.decalage_final(dict_boite_maitre)'''

                    dict_boite_maitre = DictBoiteComplete.actualisation_type_placement_boite_final(dict_boite_maitre,df_info_custom)
                    dict_boite_maitre = DictBoiteComplete.actualisation_bas_haut_gauche_droite(dict_boite_maitre)
        return self

    ##########################################################################################
    #Placement intérieur boite
    ##########################################################################################
    def recuperation_infos_geom_dans_bloc(self,type_boite_placement:list=['normal']):
        for nom_entite_custom,contenu_custom in self.items():
            for nom_boite_maitre,dict_boite_maitre in contenu_custom.items():
                dict_boite_maitre = DictBoiteComplete.ajout_info_point_interception_et_cote(dict_boite_maitre,type_boite_placement)
                dict_boite_maitre = DictBoiteComplete.creation_dict_hauteur_largeur_blocs_dans_meme_boite(dict_boite_maitre,type_boite_placement)
                dict_boite_maitre = DictBoiteComplete.ajout_ecart_origine_et_numero_bloc(dict_boite_maitre,type_boite_placement)
        return self

    def placement_bloc_interieur_boite_complete(self,dict_dict_info_custom,type_boite_placement):
        for nom_entite_custom,contenu_custom in self.items():
            for nom_boite_maitre,dict_boite_maitre in contenu_custom.items():
                if dict_boite_maitre.orientation in type_boite_placement:
                    dict_boite_maitre = DictBoiteComplete.placement_des_blocs_interieur_boite_complete(dict_boite_maitre,dict_dict_info_custom,type_boite_placement)
                    dict_boite_maitre = DictBoiteComplete.placement_objets_interieur_blocs(dict_boite_maitre,type_boite_placement)
                    dict_boite_maitre = DictBoiteComplete.ajout_colonne_pour_orientation_et_alignement_objet(dict_boite_maitre)
                    dict_boite_maitre = DictBoiteComplete.conversion_colonne_hauteur_largeur_boite_complete_vers_bloc(dict_boite_maitre,type_boite_placement)
        return self


    ##########################################################################################
    #PARTIE ortho
    ##########################################################################################
    def placement_eventuel_boite_ortho(self,dict_dict_info_custom,type_boite_placement:list=['orthogonal']):
        for nom_entite_custom,contenu_custom in self.items():
            for nom_boite_maitre,dict_boite_maitre in contenu_custom.items():
                if dict_boite_maitre.orientation in type_boite_placement:
                    dict_boite_maitre = DictBoiteComplete.placement_boite_ortho(dict_boite_maitre,dict_dict_info_custom[contenu_custom.CODE_custom],contenu_custom)
                    dict_boite_maitre = DictBoiteComplete.actualisation_info_boite_ortho(dict_boite_maitre)
                    dict_boite_maitre = DictBoiteComplete.actualisation_bas_haut_gauche_droite(dict_boite_maitre)
                    dict_boite_maitre = DictBoiteComplete.recuperation_bas_haut_gauche_droite_dans_df_contour(dict_boite_maitre)
                    dict_boite_maitre = DictBoiteComplete.augmentation_esthetique_df_contour(dict_boite_maitre)
        return self


    ##########################################################################################
    #Projet : Création des dossiers
    ##########################################################################################
    def creation_dossiers_projet(self,liste_echelle_REF_projet):
        for nom_couche_REF in liste_echelle_REF_projet:
            if not os.path.exists("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/" + self.nom_dossier_maitre + '/couche_custom_tempo'):
                os.makedirs("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/" + self.nom_dossier_maitre + '/couche_custom_tempo')
            if not os.path.exists("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/" + self.nom_dossier_maitre + '/couche_geom'):
                os.makedirs("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/" + self.nom_dossier_maitre + '/couche_geom')
            if not os.path.exists("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/" + self.nom_dossier_maitre + '/couche_bloc'):
                os.makedirs("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/" + self.nom_dossier_maitre + '/couche_bloc')
            if not os.path.exists("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/" + self.nom_dossier_maitre + '/couche_boite'):
                os.makedirs("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/" + self.nom_dossier_maitre + '/couche_boite')
            if not os.path.exists("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/" + self.nom_dossier_maitre + '/couche_fleche'):
                os.makedirs("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/" + self.nom_dossier_maitre + '/couche_fleche')

    ##########################################################################################
    #Custom
    ##########################################################################################
    def creation_entite_custom(self,dict_dict_info_REF=None,liste_NOM_custom=None):
        chemin_projet = chemin_dossier + "/" +  self.nom_dossier_maitre
        def extraire_liste_NOM_shp_dossier(chemin_dossier):
            liste_nom_custom = [os.path.basename(f) for f in glob.glob(chemin_dossier + "/*.shp")]
            liste_nom_custom = [x[0:-4] for x in liste_nom_custom]
            return liste_nom_custom

        def import_nom_custom_dossier(self,chemin_dossier_projet):
            liste_NOM_custom = extraire_liste_NOM_shp_dossier(chemin_dossier_projet + "/" + "couche_custom")
            if len(liste_NOM_custom)==0:
                print("je n'ai pas trouvé de shp custom")
            return liste_NOM_custom
        
        def import_tableaux_actions(self,chemin_dossier_projet):
            if self.type_donnees=='action':
                liste_rendu_aller_chercher_tableau_action_rempli = ['verif_tableau_DORA','tableau_MAJ_Osmose']
                liste_rendu_aller_chercher_tableau_action_final = ['carte','tableau_DORA_vers_BDD']
                if self.type_donnees=='action' and self.thematique=='MIA':
                    if self.type_rendu in liste_rendu_aller_chercher_tableau_action_rempli+liste_rendu_aller_chercher_tableau_action_final:
                        if self.type_rendu in liste_rendu_aller_chercher_tableau_action_rempli:
                            get_forme = 'remplis'
                        if self.type_rendu in liste_rendu_aller_chercher_tableau_action_final:
                            get_forme = 'final'
                        print("Je cherche les tableaux d'actions dispo sous forme " + get_forme)
                        dict_dict_df_actions_originaux = DictDFTableauxActionsMIA.recuperation_dict_tableaux_actions_MIA(dict_dict_info_REF,liste_echelle_custom=self.liste_echelle_shp_custom_a_check,forme=get_forme)
                        if len(dict_dict_df_actions_originaux)>0:
                            print("j'ai trouvé les tableaux d'actions de " + ' et '.join(list(dict_dict_df_actions_originaux)))
                    else:
                       dict_dict_df_actions_originaux = {} 
            if self.type_donnees!='action':
                dict_dict_df_actions_originaux = {}
            return dict_dict_df_actions_originaux

        if self.type_rendu=="carte" and self.type_donnees=="action":
            dict_dict_df_actions_originaux = import_tableaux_actions(self,chemin_projet)

        if liste_NOM_custom!=None:
            for NOM_custom_maitre in liste_NOM_custom:
                self[NOM_custom_maitre] = NomCustomMaitre({})
                self[NOM_custom_maitre] = NomCustomMaitre.attribut_NOM_custom(self[NOM_custom_maitre],NOM_custom_maitre)
                for echelle_REF in self.liste_echelle_shp_custom_a_check:
                    if NOM_custom_maitre in dict_dict_info_REF['df_info_'+echelle_REF]['NOM_'+echelle_REF].to_list():
                        self[NOM_custom_maitre].echelle_REF = echelle_REF
                        if echelle_REF=="MO":
                            self[NOM_custom_maitre].echelle_carto_globale = 'petite'                        
                        if echelle_REF=="DEP":
                            self[NOM_custom_maitre].echelle_carto_globale = 'grande'
                if self.type_rendu=="carte" and self.type_donnees=="action":
                    print("Je vérifie les nom custom = nom des fichiers tableaux action")
                    if all(ele in list(self) for ele in dict_dict_df_actions_originaux):
                        print("J'ai les infos qu'il me faut")
                    if not all(ele in list(self) for ele in liste_NOM_custom):
                        print("Attention, travail sur un syndicat sans le tableau d'action associé !")   

        if liste_NOM_custom==None:
            liste_NOM_custom = import_nom_custom_dossier(self,chemin_projet)
            if self.type_donnees=='action':
                for NOM_custom_maitre in dict_dict_df_actions_originaux:
                    self[NOM_custom_maitre] = NomCustomMaitre({})
                    echelle_REF = dict_dict_df_actions_originaux[NOM_custom_maitre].echelle_df
                    self[NOM_custom_maitre] = NomCustomMaitre.attribut_NOM_custom(self[NOM_custom_maitre],NOM_custom_maitre,echelle_REF)
                    self[NOM_custom_maitre].echelle_carto_globale = 'petite'
            if self.type_donnees!='action':
                for NOM_custom_maitre in liste_NOM_custom:
                    self[NOM_custom_maitre] = NomCustomMaitre({})
                    echelle_REF = "MO"
                    self[NOM_custom_maitre] = NomCustomMaitre.attribut_NOM_custom(self[NOM_custom_maitre],NOM_custom_maitre,echelle_REF)
                    self[NOM_custom_maitre].echelle_carto_globale = 'petite'    
                                                 
        return self    

    def attributs_CODE_CUSTOM(self,dict_dict_info_REF):
        self.liste_echelle_custom = list(set(self.gdf_custom.gdf['echelle_REF'].to_list()))
        dict_conv_NOM_CODE = {}
        for echelle_custom in self.liste_echelle_custom:
            if echelle_custom!="custom":
                dict_conv_NOM_CODE.update(dict_dict_info_REF['df_info_' + echelle_custom].dict_NOM_CODE)
            if echelle_custom=="custom":    
                dict_conv_NOM_CODE.update(dict(zip(self.gdf_custom["NOM_custom"].to_list(),self.gdf_custom["CODE_custom"].to_list())))
        for nom_custom,entite_custom in self.items():
            if nom_custom == "BDD_Osmose":
                self[nom_custom].CODE_custom = "CODE_BDD_Osmose"
            if nom_custom != "BDD_Osmose":
                self[nom_custom].CODE_custom = dict_conv_NOM_CODE[entite_custom.NOM_custom]
        return self

    def attributs_echelle_base_REF(self,dict_dict_info_REF):
        if self.echelle_base_REF!=None:
                for nom_custom,entite_custom in self.items():
                    entite_custom.echelle_base_REF = self.echelle_base_REF

        if self.echelle_base_REF==None:
            if (self.type_rendu=='carte' and self.type_donnees=='toutes_pressions'):
                for nom_custom,entite_custom in self.items():
                    entite_custom.echelle_base_REF = 'ME'
            if self.type_rendu=='tableau_MAJ_Osmose':
                for nom_custom,entite_custom in self.items():
                    entite_custom.echelle_base_REF = 'ME'
            if ((self.type_rendu=='carte' or self.type_rendu=='tableau_DORA_vers_BDD' or self.type_rendu=='verif_tableau_DORA' or  self.type_rendu=='tableau_vierge')
                and self.type_donnees=='action'):
                df_info_SME = dict_dict_info_REF['df_info_SME']
                liste_CODE_custom_avec_echelle_SME = list(set(df_info_SME['MO_maitre'].to_list()))
                for nom_custom,entite_custom in self.items():
                    list_echelle_base_REF = []
                    if entite_custom.CODE_custom in liste_CODE_custom_avec_echelle_SME:
                        print("Pour "+nom_custom+", j'ai trouvé des SOUS ME !")
                        entite_custom.echelle_base_REF = "SME"
                    
                    if entite_custom.CODE_custom not in liste_CODE_custom_avec_echelle_SME:
                        print("Pour "+nom_custom+", j'ai pas trouvé des SOUS ME !")
                        entite_custom.echelle_base_REF = "ME"

        return self

    def attributs_gdf_custom(self,dict_geom_REF,dict_dict_info_REF,liste_NOM_custom):
        def get_gdf_custom_issus_dossier_couche_geom(self,liste_NOM_custom):
            chemin_projet_couche_custom = chemin_dossier + "/" +  self.nom_dossier_maitre + "/" + "couche_custom"
            list_tempo_gdf_custom_couche_geom = [gpd.read_file(f, encoding='utf-8') for f in glob.glob(chemin_projet_couche_custom +"/*.shp")]
            liste_nom_shp = [os.path.basename(f)[0:-4] for f in glob.glob(chemin_projet_couche_custom + "/*.shp")]
            list_tempo_gdf_custom_couche_geom = [x.to_crs(epsg=2154) for x in list_tempo_gdf_custom_couche_geom]
            for num,gdf_custom in enumerate(list_tempo_gdf_custom_couche_geom):
                gdf_custom["NOM_custom"] = liste_nom_shp[num]
                gdf_custom["ALIAS"] = liste_nom_shp[num]
                gdf_custom["CODE_custom"] = "CODE_custom_" + str(num)
                list_tempo_gdf_custom_couche_geom[num] = list_tempo_gdf_custom_couche_geom[num].rename({"geometry":"geometry_custom"},axis=1)
                list_tempo_gdf_custom_couche_geom[num] = list_tempo_gdf_custom_couche_geom[num].set_geometry("geometry_custom")
            liste_echelle_custom_couche_geom = ["custom" for x in range(0,len(list_tempo_gdf_custom_couche_geom))]
            return liste_echelle_custom_couche_geom,list_tempo_gdf_custom_couche_geom
                        
        if liste_NOM_custom!=None:
            gdf_custom = Class_NGdfREF.chercher_gdf_custom(self,dict_geom_REF,dict_dict_info_REF)
        if liste_NOM_custom==None:
            liste_echelle_custom,list_tempo_gdf_custom = get_gdf_custom_issus_dossier_couche_geom(self,liste_NOM_custom)
        self.gdf_custom = gdf_custom
        self.gdf_custom.gdf = self.gdf_custom.gdf.set_geometry('geometry_custom')
        return self
    
    
    def import_shp_custom_bis(self,nom_custom_REF=None):
        if self.type_rendu == "carte" and self.type_donnees == "action" and self.thematique == "MIA":
            liste_nom_synd,liste_couche_synd = custom.import_fichiers_custom_carte_actions_MIA(self)
            liste_nom_synd,liste_couche_synd = custom.attribution_NOM_MO(liste_nom_synd,liste_couche_synd)
            gdf_gros_custom = custom.concatenation_liste_synd(liste_nom_synd,liste_couche_synd)
            gdf_gros_custom = gdf_gros_custom.reset_index()
            gdf_gros_custom['index'] = [x for x in range(0,len(gdf_gros_custom))]
            if "CODE_custom" not in list(gdf_gros_custom):
                gdf_gros_custom["CODE_custom"] = ""
            gdf_gros_custom = gdf_gros_custom[['index',"CODE_custom",'NOM_custom',"geometry_custom",'issu_BDD']]
            gdf_gros_custom = ListGdfCustom(gdf_gros_custom)
            gdf_gros_custom.echelle_shp_custom = "custom"
        if self.type_rendu == "tableau" and self.type_donnees == "action" and self.thematique == "MIA":
            dict_geom_REF = dictGdfCompletREF({})
            dict_geom_REF = dict_geom_REF.ajout_echelle_dict_couche_complet_REF(self,self.liste_echelle_shp_custom_a_check)
            if nom_custom_REF==None:
                dict_dict_df_actions_originaux = DictDFTableauxActionsMIA.recuperation_dict_tableaux_actions_MIA()
                list_echelle_tableaux_action_MIA = list(set([df.echelle_df for nom_custom,df in dict_dict_df_actions_originaux.items()]))
                dict_nom_custom_par_echelle = {k:[] for k in list_echelle_tableaux_action_MIA}
                for nom_custom,df in dict_dict_df_actions_originaux.items():
                    dict_nom_custom_par_echelle[df.echelle_df].append(nom_custom)
                for echelle_gdf,gdf in dict_geom_REF.items():
                    if echelle_gdf.split('_')[-1] in dict_nom_custom_par_echelle:
                        if echelle_gdf.split('_')[-1] == "MO":
                            list_nom_custom = dict_nom_custom_par_echelle[echelle_gdf.split('_')[-1]]
                        if echelle_gdf.split('_')[-1] == "DEP":
                            dict_num_dep_NOM_DEP = dict(zip(dict_geom_REF[echelle_gdf]['CODE_DEP'].to_list(),dict_geom_REF[echelle_gdf]['NOM_DEP'].to_list()))
                            list_nom_custom = [dict_num_dep_NOM_DEP[x] for x in dict_nom_custom_par_echelle[echelle_gdf.split('_')[-1]]]
                        dict_geom_REF[echelle_gdf] = dict_geom_REF[echelle_gdf].loc[gdf[gdf.nom_entite_REF].isin(list_nom_custom)]
                    if echelle_gdf.split('_')[-1] not in dict_nom_custom_par_echelle:
                        dict_geom_REF[echelle_gdf] = dict_geom_REF[echelle_gdf].loc[gdf[gdf.nom_entite_REF].isin(['Vive DORA'])]
            if nom_custom_REF!=None:
                if isinstance(nom_custom_REF,str):
                    for echelle_gdf,gdf in dict_geom_REF.items():
                        dict_geom_REF[echelle_gdf] = dict_geom_REF[echelle_gdf].loc[gdf[gdf.nom_entite_REF]==nom_custom_REF]
                if isinstance(nom_custom_REF,int):
                    for echelle_gdf,gdf in dict_geom_REF.items():
                        dict_geom_REF[echelle_gdf] = dict_geom_REF[echelle_gdf].loc[gdf['CODE_'+gdf.echelle_REF_shp]==str(nom_custom_REF)]                        
            list_gdf = []
            for echelle_gdf,gdf in dict_geom_REF.items():
                dict_renommage = {'CODE_'+echelle_gdf.split('_')[-1]:'CODE_custom','NOM_'+echelle_gdf.split('_')[-1]:'NOM_custom','geometry_'+echelle_gdf.split('_')[-1]:'geometry_custom'}
                dict_geom_REF[echelle_gdf] = dict_geom_REF[echelle_gdf].rename(dict_renommage,axis=1)
                dict_geom_REF[echelle_gdf] = dict_geom_REF[echelle_gdf][list(dict_renommage.values())]
                dict_geom_REF[echelle_gdf] = dict_geom_REF[echelle_gdf].set_geometry("geometry_custom")
                list_gdf.append(dict_geom_REF[echelle_gdf])
            gdf_gros_custom = pd.concat(list_gdf)
            gdf_gros_custom = gdf_gros_custom.set_geometry("geometry_custom")
            gdf_gros_custom = ListGdfCustom(gdf_gros_custom)
            gdf_gros_custom.attribution_GdfCompletREF('custom')
        return gdf_gros_custom


    def attribution_CODE_custom(self,gdf_gros_custom):
        dict_geom_REF = dictGdfCompletREF({})
        dict_geom_REF = dict_geom_REF.ajout_echelle_dict_couche_complet_REF(self,self.liste_echelle_shp_custom_a_check)
        gdf_gros_custom = ListGdfCustom.recherche_CODE_MO_dans_BDD(gdf_gros_custom,dict_geom_REF)
        if gdf_gros_custom['NOM_custom'].isnull().values.any():
            print("Aucun nom trouvé pour les entités suivantes, soit dans le fichier origianal, soient parmis les " + str(self.liste_echelle_shp_custom_a_check).strip('[]'))
            list_nom_a_degager = gdf_gros_custom.loc[gdf_gros_custom['NOM_custom'].isnull()]['CODE_custom'].to_list()
            print("Je dois supprimer " + str(list_nom_a_degager).strip('[]') +  " du gros custom")
        return gdf_gros_custom 

    def attribution_attribut_projet_gdf_shp_custom(self,gdf_gros_custom):
        self.gdf_shp_custom = gdf_gros_custom
        return self

    def ajout_attributs_projet(self):
        def ajout_liste_categorie_icone(self):
            liste_categorie = []
            if self.type_rendu == "carte" and self.type_donnees == "action":
                if self.thematique =="MIA":
                    if self.public_cible == "elu" or self.public_cible == 'prefet':
                        liste_categorie = ['hyd','mor','con','ino','gou']
                    if self.public_cible == 'tech':
                        liste_categorie = ['rip','mor','con','mob', 'ZH','rui','ino','gou']
                if self.thematique =="ASS":
                    liste_categorie = ['etu','plu','tra','ANC','con','aut']
            if self.type_rendu == "carte" and self.type_donnees == "toutes_pressions":
                liste_categorie = ['dom','ind','azo','phy','irr','hyd']
            self.liste_categorie = liste_categorie
            return self

        #Attribution CODE MO pour chaque entite du custom
        self.nom_entite_custom = self.gdf_shp_custom.nom_entite_REF
        self.nom_geometry_custom = self.gdf_shp_custom.colonne_geometry
        self.dict_nom_custom_CODE_custom = dict(zip(self.gdf_shp_custom['NOM_custom'].to_list(),self.gdf_shp_custom['CODE_custom']))
        self.liste_nom_custom = self.gdf_shp_custom['NOM_custom'].to_list()
        self.liste_CODE_custom = self.gdf_shp_custom['CODE_custom'].tolist()
        self = ajout_liste_categorie_icone(self)
        return self

    def creation_df_info_custom(self):
        gdf_custom = self.gdf_custom.gdf
        """ajout des info échelle, centre, bb et orientation"""
        list_colonne_a_garder_issues_gdf_gros_custom = ["CODE_custom","NOM_custom","echelle",'X_centre_custom','Y_centre_custom','orient_custom','min_x_custom','min_y_custom','max_x_custom','max_y_custom']
        df_info_custom_tempo = gdf_custom.join(gdf_custom.bounds)
        df_info_custom_tempo = df_info_custom_tempo.rename({"maxx":'max_x_custom',"maxy":'max_y_custom',"minx":'min_x_custom',"miny":'min_y_custom'},axis=1)
        #BB
        df_info_custom_tempo['taille_GD']=df_info_custom_tempo['max_y_custom']-df_info_custom_tempo['min_y_custom']
        df_info_custom_tempo['taille_BH']=df_info_custom_tempo['max_x_custom']-df_info_custom_tempo['min_x_custom']
        #Orientation
        df_info_custom_tempo.loc[df_info_custom_tempo['taille_GD']>df_info_custom_tempo['taille_BH'],'orient_custom']='portrait'
        df_info_custom_tempo.loc[df_info_custom_tempo['taille_GD']<df_info_custom_tempo['taille_BH'],'orient_custom']='paysage'

        #Echelle
        dict_NOM_custom_echelle = {k:v.echelle_carto_globale for k,v in self.items()}
        df_info_custom_tempo['echelle'] = df_info_custom_tempo['NOM_custom'].map(dict_NOM_custom_echelle)

        #Centre
        df_info_custom_tempo['geometry_centre_custom'] = df_info_custom_tempo.representative_point()
        df_info_custom_tempo['X_centre_custom']=df_info_custom_tempo['geometry_centre_custom'].x
        df_info_custom_tempo['Y_centre_custom']=df_info_custom_tempo['geometry_centre_custom'].y
        df_info_custom = df_info_custom_tempo.reset_index()[list_colonne_a_garder_issues_gdf_gros_custom]
        #ajout de l'ID
        df_info_custom['id_atlas'] = df_info_custom['CODE_custom'] + '%' + self.type_donnees + '%' + self.thematique + '%' + self.public_cible

        #Gestion de l'ALIAS
        liste_nom_potentiellement_alias = ['ALIAS',"Alias","alias"]
        for x in liste_nom_potentiellement_alias:
            df_info_custom = df_info_custom.rename({x:"ALIAS"},axis=1)
        if "ALIAS" in list(df_info_custom):
            df_info_custom.loc[df_info_custom['ALIAS']!=df_info_custom['ALIAS'],"ALIAS"] = df_info_custom['NOM_custom']
        if "ALIAS" not in list(df_info_custom):
            df_info_custom['ALIAS'] = df_info_custom['NOM_custom']

        return df_info_custom

    def actualisation_liste_custom_projet(self,dict_dict_boite_maitre):
        if self.type_rendu=='carte' and self.type_donnees == 'action' and self.thematique == 'MIA':
            self.liste_CODE_custom_tableau_actions = [self.dict_nom_custom_CODE_custom[x] for x in self.liste_nom_custom_tableau_actions if x in self.dict_nom_custom_CODE_custom]
            self.liste_CODE_custom = [x for x in self.liste_CODE_custom if x in self.liste_CODE_custom_tableau_actions]
        return self

    def creation_dict_dict_info_custom(self,df_info_custom):
        dict_dict_info_custom = df_info_custom.set_index('CODE_custom').to_dict('index')
        return dict_dict_info_custom

    def attributs_dict_dict_info_custom(self,dict_dict_info_custom):
        for custom in dict_dict_info_custom:
            dict_dict_info_custom[custom]['custom_a_reduire']=False
            dict_dict_info_custom[custom]['boite_a_replacer']=False
            dict_dict_info_custom[custom]['PPG_inclus_dans_integral_custom']=False
            dict_dict_info_custom[custom]['cartouche_boite_ortho_separe']=False
        return dict_dict_info_custom

    def ajout_info_df_parties_custom(self,dict_decoupcustom,dict_dict_info_custom,dict_dict_info_REF):
        df_nom_ME_simple = dataframe.recuperation_tableaux_nom_ME_simple()
        dict_mapping_geometry = {}
        dict_mapping_nom_partie = {}
        liste_echelle_shp_par_custom = self.gdf_shp_custom.liste_echelle_shp_par_custom
        for CODE_custom,dict_partie_custom in dict_decoupcustom.items():
            dict_mapping_nom_partie[CODE_custom] = dict_decoupcustom[CODE_custom].index.tolist()
            dict_mapping_geometry[CODE_custom]= dict_decoupcustom[CODE_custom]['geometry'].to_list()
            dict_tempo_mapping_CODE_custom = {CODE_custom:dict_decoupcustom[CODE_custom]['CODE_custom'].to_list()}
            self.gdf_shp_custom["CODE_custom_tempo"] = self.gdf_shp_custom["CODE_custom"].map(dict_tempo_mapping_CODE_custom).fillna(self.gdf_shp_custom["CODE_custom"])
            self.gdf_shp_custom = self.gdf_shp_custom.explode("CODE_custom_tempo")
            self.gdf_shp_custom = self.gdf_shp_custom.reset_index(drop=True)
            self.gdf_shp_custom.loc[self.gdf_shp_custom["CODE_custom"]==CODE_custom,"geometry_custom"] = dict_decoupcustom[CODE_custom]['geometry'].to_list()
            self.gdf_shp_custom.loc[self.gdf_shp_custom["CODE_custom"]==CODE_custom,"ALIAS"] = self.gdf_shp_custom["CODE_custom_tempo"]
            self.gdf_shp_custom.loc[self.gdf_shp_custom["CODE_custom"]==CODE_custom,"NOM_MO"] = self.gdf_shp_custom["CODE_custom_tempo"]
            self.gdf_shp_custom.loc[self.gdf_shp_custom["CODE_custom"]==CODE_custom,"CODE_custom"] = self.gdf_shp_custom["CODE_custom"] + "é" + self.gdf_shp_custom["CODE_custom_tempo"]
        self.gdf_shp_custom = ListGdfCustom(self.gdf_shp_custom)
        self.gdf_shp_custom.attribution_GdfCompletREF('custom')
        self.gdf_shp_custom.liste_echelle_shp_par_custom = list(set(liste_echelle_shp_par_custom))
        self.gdf_shp_custom['surface_MO'] = self.gdf_shp_custom.area
        
        '''self.gdf_shp_custom['nom_partie'] = self.gdf_shp_custom.apply(lambda x: dict_map_CODE_ME_nom_simple[x['NOM_MO'].replace("partie_","").split('$')[0]] if x['NOM_MO'].startswith('partie_') else x['ALIAS'], axis=1)
        self.gdf_shp_custom.loc[self.gdf_shp_custom['CODE_custom'].isin(dict_mapping_geometry),'ALIAS'] = self.gdf_shp_custom['ALIAS'] + ' ' + self.gdf_shp_custom['nom_partie']
        self.gdf_shp_custom['NOM_MO'] = self.gdf_shp_custom.apply(lambda x: dict_map_CODE_custom_NOM_MO[x['CODE_custom']] + ' ' + dict_map_CODE_ME_nom_simple[x['NOM_MO'].replace("partie_","").split('$')[0]] if x['NOM_MO'].startswith('partie_') else x['NOM_MO'], axis=1)
        self.gdf_shp_custom.loc[self.gdf_shp_custom['CODE_custom'].isin(dict_mapping_geometry),'CODE_custom'] = self.gdf_shp_custom['CODE_custom'] + '_' + self.gdf_shp_custom['nom_partie']'''
        return self

    def actualisation_attributs_projet_apres_decoupage_custom(self):
        self.liste_nom_custom = self.liste_nom_custom_tableau_actions
        self.liste_CODE_custom = self.liste_CODE_custom_tableau_actions
        return self

    def ajout_attributs_custom_reduit(self,dict_decoupcustom,dict_dict_info_custom,dict_dict_info_REF):
        for CODE_CUSTOM,dict_decoup_custom in dict_decoupcustom.items():
            for nom_custom,dict_df_partie_custom in dict_decoup_custom.items():
                #C'est sale mais chaque gdf n'a qu'une ligne donc bon...
                self.dict_nom_custom_CODE_custom = dict(zip(self.gdf_shp_custom['NOM_MO'].to_list(),self.gdf_shp_custom['CODE_custom'].to_list()))
                self.liste_CODE_custom_tableau_actions = self.gdf_shp_custom['CODE_custom'].to_list()
                self.liste_nom_custom_tableau_actions = self.gdf_shp_custom['NOM_MO'].to_list()
        return self

########################################################################################################
#PARTIE atlas
########################################################################################################
    def definition_colonne_a_garder_pour_export_vers_QGIS_bloc(self):
        for nom_entite_custom,contenu_custom in self.items():
            for type_boite,contenu_boite in contenu_custom.items():
                for nom_bloc,dict_bloc in contenu_boite.items():
                    dict_bloc.liste_nom_colonne_a_garder.extend(['CODE_REF','echelle_REF','id_atlas'])
                    dict_bloc.liste_nom_colonne_a_garder.extend(['sens',"type_placement_boite_final"])
                    if dict_bloc.type=='bloc_texte_simple':
                        dict_bloc.liste_nom_colonne_a_garder.extend(['geometry_bloc_texte_simple','nom_police','taille_police','ls_decoup_texte_simple','gauche_bloc','droite_bloc','haut_bloc','bas_bloc','alignement','Quadrant'])
                    if dict_bloc.type=='bloc_icone':
                        dict_bloc.liste_nom_colonne_a_garder.extend(['geometry_bloc_icone','gauche_bloc_bloc_icone','droite_bloc_bloc_icone','haut_bloc_bloc_icone','bas_bloc_bloc_icone','largeur_icone','hauteur_icone'])
                    if dict_bloc.type=='bloc_lignes_multiples':
                        dict_bloc.liste_nom_colonne_a_garder.extend(['geometry_point_bloc_lignes_multiples','nom_police','taille_police','lm_decoup_bloc_ligne_multiples','alignement','Quadrant','al_lm_ind','angle'])
        return self

   
    def definition_colonne_a_garder_pour_export_vers_QGIS_boite(self):
        for nom_entite_custom,contenu_custom in self.items():
            for type_boite,contenu_boite in contenu_custom.items():
                contenu_boite.liste_nom_colonne_a_garder = []
                contenu_boite.liste_nom_colonne_a_garder.extend(['CODE_REF','echelle_REF','id_atlas','geom_boite','type_placement_boite_final'])
        return self    
    
    def reduction_nom_colonne_pour_export_QGIS(self):
        for nom_entite_custom,contenu_custom in self.items():
            for type_boite,contenu_boite in contenu_custom.items():
                if contenu_boite.orientation=="normal":
                    contenu_boite.df_contour = dataframe.reduction_nom_colonne_via_fichier_csv(contenu_boite.df_contour,"df_contour")
        for nom_entite_custom,contenu_custom in self.items():
            for type_boite,contenu_boite in contenu_custom.items():
                    for type_boite,contenu_boite in contenu_custom.items():
                        for type_bloc,contenu_bloc in contenu_boite.items():
                            if hasattr(contenu_bloc,"df_indiv"):
                                contenu_bloc.df_indiv = dataframe.reduction_nom_colonne_via_fichier_csv(contenu_bloc.df_indiv,contenu_bloc.type)  
                            if not hasattr(contenu_bloc,"df_indiv"):    
                                contenu_bloc.df = dataframe.reduction_nom_colonne_via_fichier_csv(contenu_bloc.df,contenu_bloc.type)                        
        return self

    def generation_col_atlas(self,dict_dict_info_custom):
        self.gdf_custom['id_atlas'] = self.gdf_custom['CODE_custom'] + '%' + self.type_donnees + '%' + self.thematique + '%' + self.public_cible + '%' + self.info_fond_carte
        self.gdf_fond_carte['id_atlas'] = self.gdf_fond_carte['CODE_custom'] + '%' + self.type_donnees + '%' + self.thematique + '%' + self.public_cible + '%' + self.info_fond_carte
        df_info_custom = pd.DataFrame.from_dict(dict_dict_info_custom, orient="index")
        self.gdf_custom = pd.merge(self.gdf_custom,df_info_custom[["min_x_custom","max_x_custom","min_y_custom","max_y_custom"]],left_on="CODE_custom",right_index=True)
        for nom_entite_custom,contenu_custom in self.items():
            for type_boite,contenu_boite in contenu_custom.items():
                contenu_boite.df_contour['id_atlas'] = contenu_custom.CODE_custom + '%' + self.type_donnees + '%' + self.thematique + '%' + self.public_cible + '%' + self.info_fond_carte
        for nom_entite_custom,contenu_custom in self.items():
            for type_boite,contenu_boite in contenu_custom.items():
                for type_bloc,contenu_bloc in contenu_boite.items():                                  
                    contenu_bloc.df['id_atlas'] = contenu_custom.CODE_custom + '%' + self.type_donnees + '%' + self.thematique + '%' + self.public_cible + '%' + self.info_fond_carte
        return self

    def transfert_eventuel_info_bloc_df_vers_bloc_indiv(self):
        for nom_entite_custom,contenu_custom in self.items():
            for nom_boite_maitre,dict_boite_maitre in contenu_custom.items():
                dict_boite_maitre = DictBoiteComplete.transfert_info_df_vers_df_indiv(dict_boite_maitre)
        return self
    
    def garder_colonne_de_attributs_colonne_a_garder(self):
        for nom_entite_custom,contenu_custom in self.items():
            for type_boite,contenu_boite in contenu_custom.items():
                if contenu_boite.orientation=="normal":
                    contenu_boite.df_contour = contenu_boite.df_contour[contenu_boite.liste_nom_colonne_a_garder]
        for nom_entite_custom,contenu_custom in self.items():
            for type_boite,contenu_boite in contenu_custom.items():
                    for type_boite,contenu_boite in contenu_custom.items():
                        for type_bloc,contenu_bloc in contenu_boite.items():
                            if contenu_bloc.type=="bloc_lignes_multiples":
                                contenu_bloc.df_indiv = contenu_bloc.df_indiv[contenu_bloc.liste_nom_colonne_a_garder] 
                            else:
                                contenu_bloc.df = contenu_bloc.df[contenu_bloc.liste_nom_colonne_a_garder]
        return self                               

    def recuperer_donnes_df_info_custom_sur_atlas(self,df_info_custom):
        self.gdf_shp_custom = pd.merge(self.gdf_shp_custom,df_info_custom,on=['CODE_custom','NOM_custom'],suffixes=[None,'_a_supprimer'])
        self.gdf_shp_custom = self.gdf_shp_custom.loc[:,~self.gdf_shp_custom.columns.str.endswith('_a_supprimer')]
        return self

    def garder_colonne_de_attributs_colonne_a_garder_atlas(self):
        liste_colonne_a_garder = ['NOM_custom','ALIAS', 'geometry_custom', 'CODE_custom', 'echelle', 'X_centre_custom', 'Y_centre_custom', 'orient_custom', 'id_atlas', 'geom_princ', 'min_x_custom', 'max_x_custom', 'min_y_custom', 'max_y_custom']
        if len(self.liste_echelle_fond_carte)==2:
            liste_colonne_a_garder.append('geom_sec')
        self.gdf_shp_custom = self.gdf_shp_custom[liste_colonne_a_garder]
        return self
    ##########################################################################################
    #Custom spécial : département
    ##########################################################################################
    def import_shp_custom_departement(self,dep,gdf_BVG,df_info_BVG):
        liste_gdf_tempo = []
        df_info_tempo = df_info_BVG.loc[df_info_BVG.apply(lambda x : dep in x["list_dep"],axis=1)]
        list_BVG_dep = df_info_tempo['CODE_BVG'].to_list()
        gdf_BVG_tempo = gdf_BVG.loc[gdf_BVG['CODE_BVG'].isin(list_BVG_dep)]
        gdf_BVG_tempo = gdf_BVG_tempo.dissolve()
        gdf_BVG_tempo['NOM_custom'] = str(dep)
        gdf_BVG_tempo['CODE_custom'] = "dep " + str(dep)
        gdf_BVG_tempo = gdf_BVG_tempo.rename({"geometry_BVG":'geometry_custom'},axis=1)
        gdf_BVG_tempo = gdf_BVG_tempo.set_geometry('geometry_custom')
        gdf_BVG_tempo = gdf_BVG_tempo[["CODE_custom",'NOM_custom','geometry_custom']]
        liste_gdf_tempo.append(gdf_BVG_tempo)
            
        gdf_gros_custom = pd.concat(liste_gdf_tempo)
        gdf_gros_custom = gdf_gros_custom.set_geometry('geometry_custom')
        gdf_gros_custom = gdf_gros_custom.reset_index()
        gdf_gros_custom = ListGdfCustom(gdf_gros_custom)
        gdf_gros_custom.echelle_shp_custom = "custom"
        gdf_gros_custom.liste_echelle_shp_par_custom = ['DEP']
        return gdf_gros_custom

    ##########################################################################################
    #Reférentiels
    ##########################################################################################
    def creation_dict_couche_geom(self,liste_echelle_REF_projet):
        dict_geom_REF = {}
        self.liste_echelle_REF_projet = liste_echelle_REF_projet
        for echelle_carto_REF in self.liste_echelle_REF_projet:
            if echelle_carto_REF == 'ME':
                perimetre_ME= gpd.read_file("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/couche geom/ME/BV ME AG 2021.shp")
                #On dégage le premier FR
                perimetre_ME[self.colonne_fond_carte] = perimetre_ME[self.colonne_fond_carte].str[2:]
                perimetre_ME = perimetre_ME.rename(columns={'geometry':'geometry_ME'})
                perimetre_ME = perimetre_ME.set_geometry('geometry_ME')
                perimetre_ME['surface_ME'] = perimetre_ME.area
                dict_geom_REF['gdf_ME'] = perimetre_ME
            if echelle_carto_REF == 'PPG':
                perimetre_PPG = PPG.import_shp_PPG(self)
                perimetre_PPG['surface_PPG'] = perimetre_PPG.area
                dict_geom_REF['gdf_PPG'] = perimetre_PPG
        return dict_geom_REF

    def ajout_code_geom_REF(self,dict_geom_REF,dict_code_geom_REF):
        for echelle_carto_REF in self.liste_echelle_REF_projet:
            if echelle_carto_REF == 'PPG':
                dict_geom_REF['gdf_PPG'] = pd.merge(dict_geom_REF['gdf_PPG'],dict_code_geom_REF['info_gdf_PPG'],on='CODE_PPG')
        return dict_geom_REF

    ##########################################################################################
    #Attribution géographique : entre custom et rérentiels
    ##########################################################################################
    def attribution_REF_custom(self,dict_geom_REF,gdf_gros_custom):
        dict_geom_decoupREF = {}
        def creation_decoup_REF_custom(dict_geom_REF,gdf_gros_custom):
            for echelle_carto_REF in self.liste_echelle_REF_projet:
                tempo_gdf_gros_custom = gdf_gros_custom
                tempo_gdf_gros_custom['NOM_MO'] = tempo_gdf_gros_custom.index
                gdf_decoup_REF_custom = gpd.overlay(dict_geom_REF['gdf_' + echelle_carto_REF],tempo_gdf_gros_custom, how='intersection')
                gdf_decoup_REF_custom['surface_decoup' + echelle_carto_REF +'_par_custom'] = gdf_decoup_REF_custom.area
                dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF]=gdf_decoup_REF_custom
            return dict_geom_decoupREF

        def calcul_ratio_surf_REF_custom(dict_geom_decoupREF):
            for echelle_carto_REF in self.liste_echelle_REF_projet:
                dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF]['ratio_surf'] = dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF]['surface_decoup' + echelle_carto_REF +'_par_custom']/dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF]['surface_'+echelle_carto_REF]
            return dict_geom_decoupREF

        def regles_tri_REF_custom(dict_geom_decoupREF):
            #Les régles de tri sont différentes pour le tableaux persos, on est plus laxiste pour le tableau perso par MO
            for echelle_carto_REF in self.liste_echelle_REF_projet:
                if self.type_donnees =='action' or self.type_donnees =='toutes_pressions':
                    if echelle_carto_REF=='ME':
                        dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF] = dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF].loc[(dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF]['ratio_surf'] > 0.3) | (dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF]['surface_decoup' + echelle_carto_REF +'_par_custom']>10000000)]
                    if echelle_carto_REF=='PPG':
                        dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF] = dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF].loc[(dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF]['ratio_surf'] > 0.3)]
                if self.type_donnees =='tableaux_perso_par_MO_ou_dep':
                    if echelle_carto_REF=='ME':
                        dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF] = dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF].loc[(dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF]['ratio_surf'] > 0.2) | (dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF]['surface_decoup' + echelle_carto_REF +'_par_custom']>200000)]
                    if echelle_carto_REF=='PPG':
                        dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF] = dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF].loc[(dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF]['ratio_surf'] > 0.2)]
            return dict_geom_decoupREF

        def creation_dict_dict_custom_listeREF(dict_geom_decoupREF):
            dict_df_listeREF_custom = {}
            dict_dict_listeREF_custom = {}
            for echelle_carto_REF in self.liste_echelle_REF_projet:
                dict_df_listeREF_custom[echelle_carto_REF] = dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF].groupby('NOM_MO').agg({'CODE_'+echelle_carto_REF:lambda x: list(x)})
                dict_df_listeREF_custom[echelle_carto_REF].columns = ["liste_decoup" + echelle_carto_REF + "_custom"]
                dict_dict_listeREF_custom[echelle_carto_REF] = dict_df_listeREF_custom[echelle_carto_REF].to_dict()
            dict_dict_listeREF_custom = {'decoup'+echelle_carto_REF + '_custom': v for echelle_carto_REF,v in dict_dict_listeREF_custom.items()}
            return dict_df_listeREF_custom,dict_dict_listeREF_custom

        def creation_dict_dict_custom_decoupREF(dict_geom_decoupREF):
            dict_dict_decoupREF_custom = {}
            for echelle_carto_REF in self.liste_echelle_REF_projet:
                dict_dict_decoupREF_custom['gdf_decoup' + echelle_carto_REF] = {}
                for custom in self:
                    dict_dict_decoupREF_custom['gdf_decoup' + echelle_carto_REF][custom]=dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF].loc[dict_geom_decoupREF['gdf_decoup' + echelle_carto_REF]['NOM_MO']==custom]
            return dict_dict_decoupREF_custom

            #découpage des REF par le custom
        dict_geom_decoupREF = creation_decoup_REF_custom(dict_geom_REF,gdf_gros_custom)
        dict_geom_decoupREF = calcul_ratio_surf_REF_custom(dict_geom_decoupREF)
        dict_geom_decoupREF = regles_tri_REF_custom(dict_geom_decoupREF)
        dict_df_listeREF_custom,dict_dict_listeREF_custom = creation_dict_dict_custom_listeREF(dict_geom_decoupREF)
        dict_dict_decoupREF_custom = creation_dict_dict_custom_decoupREF(dict_geom_decoupREF)
        return dict_df_listeREF_custom,dict_dict_listeREF_custom,dict_geom_decoupREF,dict_dict_decoupREF_custom
    #gdf_decoupREF_custom,gdf_decoupREF_tried_custom,df_custom_decoup_listeREF,dict_listeREF_custom

    def actualisation_keys_dict_si_custom_vide(self,dict_dict_listeREF_custom):
        for echelle_carto_REF in self.liste_echelle_REF_projet:
            liste_custom_non_vide = list(dict_dict_listeREF_custom["decoup" + echelle_carto_REF + "_custom"]["liste_decoup" + echelle_carto_REF + "_custom"].keys())
        liste_complete_custom = list(self.keys())
        liste_custom_vide = list(set(liste_complete_custom) - set(liste_custom_non_vide))
        for custom_vide in liste_custom_vide:
            self.pop(custom_vide)
        liste_nom_custom = liste_custom_non_vide
        return self

    def actualisation_liste_nom_custom(self):
        for echelle_carto_REF in self.liste_echelle_REF_projet:
            liste_custom_non_vide = list(self.keys())
        liste_nom_custom = liste_custom_non_vide
        return liste_nom_custom

    def creation_dict_dict_listeREF_REF(self,dict_geom_REF):
        dict_geomREF_decoupREF = {}
        def creation_decoup_REF_REF(dict_geom_REF,liste_echelle_REF_projet):
            liste_combinaison_REF = list(itertools.combinations(liste_echelle_REF_projet, 2))
            liste_combinaison_REF = [list(x) for x in liste_combinaison_REF]
            for [REF1,REF2] in liste_combinaison_REF:
                gdf_decoup_REF1_REF2 = gpd.overlay(dict_geom_REF['gdf_' + REF1][['CODE_'+REF1,'geometry_'+REF1]], dict_geom_REF['gdf_' + REF2][['CODE_'+REF2,'geometry_'+REF2,'surface_'+REF2]], how='intersection')
                gdf_decoup_REF2_REF1 = gpd.overlay(dict_geom_REF['gdf_' + REF2][['CODE_'+REF2,'geometry_'+REF2]], dict_geom_REF['gdf_' + REF1][['CODE_'+REF1,'geometry_'+REF1,'surface_'+REF1]], how='intersection')
                dict_geomREF_decoupREF['gdf_decoup' + REF1 +'_' + REF2]=gdf_decoup_REF1_REF2
                dict_geomREF_decoupREF['gdf_decoup' + REF2 +'_' + REF1]=gdf_decoup_REF2_REF1
                dict_geomREF_decoupREF['gdf_decoup' + REF1 +'_' + REF2]['surface_decoup' + REF1] = dict_geomREF_decoupREF['gdf_decoup' + REF1 +'_' + REF2]['geometry'].area
                dict_geomREF_decoupREF['gdf_decoup' + REF2 +'_' + REF1]['surface_decoup' + REF2] = dict_geomREF_decoupREF['gdf_decoup' + REF2 +'_' + REF1]['geometry'].area
                dict_geomREF_decoupREF['gdf_decoup' + REF1 +'_' + REF2]['ratio_surf'] = dict_geomREF_decoupREF['gdf_decoup' + REF1 +'_' + REF2]['surface_decoup' + REF1]/dict_geomREF_decoupREF['gdf_decoup' + REF1 +'_' + REF2]['surface_' + REF2]
                dict_geomREF_decoupREF['gdf_decoup' + REF2 +'_' + REF1]['ratio_surf'] = dict_geomREF_decoupREF['gdf_decoup' + REF2 +'_' + REF1]['surface_decoup' + REF2]/dict_geomREF_decoupREF['gdf_decoup' + REF2 +'_' + REF1]['surface_' + REF1]

            return dict_geomREF_decoupREF,liste_combinaison_REF

        def regle_tri_decoupREF_REF(dict_geomREF_decoupREF):
            #On dégage si un périmétre est clairement plus grand que l'autre (ex : PPG > ME)
            for nom_decoup,df_decoupREF_REF in dict_geomREF_decoupREF.items():
                df_decoupREF_REF = df_decoupREF_REF.loc[df_decoupREF_REF['ratio_surf'] > 0.1]
                dict_geomREF_decoupREF[nom_decoup] = df_decoupREF_REF
            return dict_geomREF_decoupREF

        def apply_dict_dict_REF_listeREF(dict_geomREF_decoupREF):
            dict_dict_listeREF_REF = {}
            for nom_decoup,ddf_decoupREF_REF in dict_geomREF_decoupREF.items():
                REF1 = list(ddf_decoupREF_REF)[0].split('_')[1]
                REF2 = list(ddf_decoupREF_REF)[1].split('_')[1]
                ddf_decoupREF_REF = ddf_decoupREF_REF.groupby('CODE_'+REF1).agg({'CODE_'+REF2:lambda x: list(x)})
                ddf_decoupREF_REF.columns = ['liste_decoup' + REF2 +'_' + REF1]
                dict_dict_listeREF_REF['decoup' + REF2 + '_' + REF1] = ddf_decoupREF_REF.to_dict()
            return dict_dict_listeREF_REF


            #découpage des REF par le custom
        dict_geomREF_decoupREF,liste_combinaison_REF = creation_decoup_REF_REF(dict_geom_REF,self.liste_echelle_REF_projet)
        dict_geomREF_decoupREF = regle_tri_decoupREF_REF(dict_geomREF_decoupREF)
        dict_dict_listeREF_REF = apply_dict_dict_REF_listeREF(dict_geomREF_decoupREF)
        return dict_dict_listeREF_REF

    ##########################################################################################
    #Couches de fond de carte (toujours é la ME pour l'eau)
    ##########################################################################################
    def creation_gdf_fond_carte_REF(self,dict_decoup_REF,dict_relation_shp_liste):
        list_gdf_fond_carte = []
        for nom_custom,entite_custom in self.items():
            CODE_custom = entite_custom.CODE_custom
            echelle_REF = entite_custom.echelle_base_REF
            gdf_fond_carte = GdfFondCarte(dict_decoup_REF['gdf_decoup'+echelle_REF+"_custom"].gdf)
            gdf_fond_carte = gdf_fond_carte.loc[gdf_fond_carte["CODE_"+echelle_REF].isin(dict_relation_shp_liste["dict_liste_"+ echelle_REF + "_par_custom"][CODE_custom])]
            gdf_fond_carte["echelle_REF"] = echelle_REF
            gdf_fond_carte["CODE_custom"] = CODE_custom
            gdf_fond_carte.columns = gdf_fond_carte.columns.str.replace(echelle_REF, "REF", regex=True)
            list_gdf_fond_carte.append(gdf_fond_carte)
        self.gdf_fond_carte = pd.concat(list_gdf_fond_carte)
        self.gdf_fond_carte = self.gdf_fond_carte.set_crs("epsg:2154")
        return self
    

    def ajout_info_fond_carte(self,dict_dict_info_REF):
        if self.info_fond_carte=="pression_MIA" or self.info_fond_carte=="etat_eco":
            df_pression_AG = dataframe.import_pression()
        if self.type_rendu =="carte":
            if self.info_fond_carte=="pression_MIA":
                if self.thematique=="MIA" and "MO" in self.liste_echelle_shp_custom_a_check:
                    df_pression_AG = df_pression_AG[[x for x in list(df_pression_AG) if x.startswith("P_")]+["CODE_ME"]]
                    df_pression_AG = df_pression_AG[['CODE_ME','P_hydromorpho',"P_MORPHO",'P_HYDRO','P_CONTI']]
                    df_pression_AG = df_pression_AG.rename({"CODE_ME":"CODE_REF"},axis=1)

                    liste_echelle_fond_carte = list(set(self.gdf_fond_carte['echelle_REF'].to_list()))
                    for REF in liste_echelle_fond_carte:
                        if "SME" in liste_echelle_fond_carte:
                            df_tempo_SME_ME = dict_dict_info_REF['df_info_SME'][['CODE_SME',"ME_maitre"]].rename({'ME_maitre':"CODE_REF"},axis=1)
                            df_tempo_SME_ME = df_tempo_SME_ME.groupby('CODE_REF').agg({'CODE_SME':lambda x: list(x)})
                            dict_CODE_ME_CODE_SME = dict(zip(df_tempo_SME_ME.index.to_list(),df_tempo_SME_ME["CODE_SME"].to_list()))
                            df_tempo_pression_AG_SME = copy.deepcopy(df_pression_AG)
                            df_tempo_pression_AG_SME['CODE_REF'] = df_tempo_pression_AG_SME['CODE_REF'].map(dict_CODE_ME_CODE_SME)
                            df_tempo_pression_AG_SME = df_tempo_pression_AG_SME.loc[~df_tempo_pression_AG_SME["CODE_REF"].isnull()]
                            df_tempo_pression_AG_SME = df_tempo_pression_AG_SME.explode("CODE_REF")
                            df_pression_AG = pd.concat([df_pression_AG,df_tempo_pression_AG_SME])
                            
                        self.gdf_fond_carte = pd.merge(self.gdf_fond_carte,df_pression_AG,on="CODE_REF")
                if self.thematique=="MIA" and "DEP" in self.liste_echelle_shp_custom_a_check:
                    pass
            if self.info_fond_carte=="etat_eco":
                df_pression_AG = df_pression_AG.rename({'CODE_ME':"CODE_REF"},axis=1)
                self.gdf_fond_carte = pd.merge(self.gdf_fond_carte,df_pression_AG,on="CODE_REF")

        return self


    def suppression_attributs_liste_CODE_custom(self,dict_dict_info_custom):
        for CODE_custom in dict_dict_info_custom:
            if dict_dict_info_custom[CODE_custom]['custom_a_reduire'] == True:
                self.liste_CODE_custom = [x for x in self.liste_CODE_custom if x!=CODE_custom]
        return self

    def suppression_CODE_custom_du_df_info_custom(self,df_info_custom,dict_dict_info_custom):
        for CODE_custom in dict_dict_info_custom:
            if dict_dict_info_custom[CODE_custom]['custom_a_reduire'] == True:
                df_info_custom = df_info_custom.loc[df_info_custom['CODE_MO']!=CODE_custom]
        return self

    def definition_si_custom_a_reduire(self,dict_special_custom_a_reduire,dict_boite_complete_pour_placement,gdf_custom,dict_dict_info_custom):
        for nom_boite_maitre,dict_boite_maitre in dict_boite_complete_pour_placement.items():
            for CODE_custom,df_custom in dict_boite_maitre.boite_complete.items():

                
                if dict_special_custom_a_reduire[CODE_custom]['df_taille_boite_complete']['surface_boite'].sum()/1000000>dict_config_espace['surface_limite'][self.taille_globale_carto]:
                    dict_special_custom_a_reduire[CODE_custom]['custom_a_reduire'] = True
                '''if gdf_custom.loc[gdf_custom['CODE_custom']==CODE_custom]["surface_custom"].iloc[0]:
                    dict_special_custom_a_reduire[CODE_custom]['custom_a_reduire'] = True'''
        return dict_special_custom_a_reduire

    def actualisation_dict_special_custom_a_reduire(self,dict_special_custom_a_reduire,df_info_custom,dict_dict_info_custom):
        for CODE_custom in dict_special_custom_a_reduire:
            dict_special_custom_a_reduire[CODE_custom]['custom_a_reduire'] = False
        return dict_special_custom_a_reduire

    def suppression_CODE_custom_du_dict_dict_info_custom(self,df_info_custom,dict_dict_info_custom):
        dict_dict_info_custom = {k:v for k,v in dict_dict_info_custom.items() if v['custom_a_reduire'] == False}
        return self

    ############################################################################################################################
    #Actualisation de la bb pour encadrer tout le custom ET les boites
    ############################################################################################################################
    def actualisation_dict_dict_info_custom_avec_bb(self,dict_dict_info_custom):
        def modif_droite_boite_si_bloc_lm_present(self,taille_globale_carto):
            if "hauteur_ligne_indiv_droit" in list(self):
                facteur_angle = np.cos(dict_config_espace['angle_rotation_lm_paysage'][taille_globale_carto] * np.pi / 180. )
                self.loc[(self["type_placement_boite_final"].isin(["H","B"]))&(~self["hauteur_ligne_indiv_droit"].isnull()),"droite_boite_complete"] = self["droite_boite_complete"] + (self["taille_hauteur_boite_biais"]-self["ecart_hauteur_origine"])*facteur_angle
            return self


        list_temp_contour = []
        for nom_custom,entite_custom in self.items():
            for type_boite,dict_boite_complete in entite_custom.items():
                df_contour_tempo = dict_boite_complete.df_contour
                df_contour_tempo['CODE_custom'] = entite_custom.CODE_custom
                if dict_boite_complete.orientation =="normal":
                    df_contour_tempo = modif_droite_boite_si_bloc_lm_present(df_contour_tempo,dict_boite_complete.taille_globale_carto)
                list_temp_contour.append(df_contour_tempo)
        df_contour_global = pd.concat(list_temp_contour)
        df_contour_global = df_contour_global.groupby("CODE_custom").agg({'gauche_boite_complete':'min','droite_boite_complete':'max','haut_boite_complete':'max','bas_boite_complete':'min'})
        self.gdf_custom = DictBoiteComplete.actualisation_cote_bb_custom(self.gdf_custom.gdf,dict_dict_info_custom,df_contour_global)
        dict_tempo = self.gdf_custom[["CODE_custom","min_x_custom","max_x_custom","min_y_custom","max_y_custom"]].set_index("CODE_custom").to_dict('index')
        for nom_custom,entite_custom in self.items():
            dict_dict_info_custom[entite_custom.CODE_custom].update(dict_tempo[entite_custom.CODE_custom])
            dict_info_custom = dict_dict_info_custom[entite_custom.CODE_custom]
            dict_info_custom['ratio_hauteur_largeur'] = (dict_info_custom['max_y_custom']-dict_info_custom['min_y_custom'])/(dict_info_custom['max_x_custom']-dict_info_custom['min_x_custom'])
            if self.format_rendu == 'A3':
                ratio_hauteur_largeur = 310/296
                if dict_info_custom['ratio_hauteur_largeur']>ratio_hauteur_largeur:
                    dict_info_custom['max_x_custom'] = dict_info_custom['X_centre_custom'] + (dict_info_custom['max_y_custom']-dict_info_custom['min_y_custom'])/ratio_hauteur_largeur/2
                    dict_info_custom['min_x_custom'] = dict_info_custom['X_centre_custom'] - (dict_info_custom['max_y_custom']-dict_info_custom['min_y_custom'])/ratio_hauteur_largeur/2
            if (dict_info_custom['max_y_custom']-dict_info_custom['min_y_custom'])>(dict_info_custom['max_x_custom']-dict_info_custom['min_x_custom']):
                dict_info_custom['orient_custom'] = "portrait"
            if (dict_info_custom['max_y_custom']-dict_info_custom['min_y_custom'])<(dict_info_custom['max_x_custom']-dict_info_custom['min_x_custom']):
                dict_info_custom['orient_custom'] = "paysage"             
        return dict_dict_info_custom
    
    ############################################################################################################################
    #Export boite, bloc, atlas
    ############################################################################################################################    
    def export_bloc(self):
        id_projet = self.type_donnees + '_' + self.thematique + '_' + self.public_cible
        for nom_entite_custom,contenu_custom in self.items():
            for type_boite,contenu_boite in contenu_custom.items():
                '''df_faits = pd.read_csv("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/test/repartition_df_faits.csv")
                contenu_boite.df_contour = pd.merge(contenu_boite.df_contour,df_faits[['CODE_MO',"etat"]].rename({'CODE_MO':"CODE_REF"},axis=1),on="CODE_REF",how="left")'''
                contenu_boite.df_contour = contenu_boite.df_contour.to_file("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/"+ id_projet +"/couche_boite/boite_complete_" + id_projet + "_" + contenu_boite.orientation + ".shp",engine="fiona", encoding='utf-8')
        for nom_entite_custom,contenu_custom in self.items():
            for type_boite,contenu_boite in contenu_custom.items():
                for type_bloc,contenu_bloc in contenu_boite.items():
                    if hasattr(contenu_bloc,"df_indiv"):
                        contenu_bloc.df_indiv = contenu_bloc.df_indiv.to_file("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/"+ id_projet +"/couche_bloc/" + contenu_bloc.type + '_' + contenu_boite.orientation + ".shp",engine="fiona", encoding='utf-8') 
                    if not hasattr(contenu_bloc,"df_indiv"):
                        contenu_bloc.df = contenu_bloc.df.to_file("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/"+ id_projet +"/couche_bloc/" + contenu_bloc.type + '_' + contenu_boite.orientation + ".shp",engine="fiona", encoding='utf-8') 
        return self    
    
    def export_atlas(self):
        id_projet = self.type_donnees + '_' + self.thematique + '_' + self.public_cible
        self.gdf_custom = self.gdf_custom.set_geometry('geometry_custom')
        self.gdf_custom['date'] = date.today().strftime("%d/%m/%Y")
        self.gdf_custom.to_file("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/" + id_projet + "/atlas_" + id_projet + ".shp",engine="fiona")
        return self
    

    def export_fond_carte(self):
        id_projet = self.type_donnees + '_' + self.thematique + '_' + self.public_cible
        self.gdf_fond_carte.to_file("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/" + id_projet + "/couche_fond_carte/fond_carte_" + id_projet + ".shp",engine="fiona")
        return self    
    ############################################################################################################################
    #Osmose
    ############################################################################################################################
    def repartition_donnees_dans_nom_custom_maitre(dict_custom_maitre,dict_df_donnees):
        for entite_custom,contenu_custom in dict_custom_maitre.items():
            contenu_custom.df = dict_df_donnees["dict_dict_df_actions_originaux"][entite_custom].df
            contenu_custom.df_Points_de_blocage = dict_df_donnees["dict_dict_df_actions_originaux"][entite_custom].df_Points_de_blocage
            contenu_custom.df_Etapes = dict_df_donnees["dict_dict_df_actions_originaux"][entite_custom].df_Etapes
            contenu_custom.df_Financeurs = dict_df_donnees["dict_dict_df_actions_originaux"][entite_custom].df_Financeurs
            contenu_custom.df_attributs = dict_df_donnees["dict_dict_df_actions_originaux"][entite_custom].df_attributs
        return dict_custom_maitre

    ############################################################################################################################
    #Tableaux excel
    ############################################################################################################################
    def export_fichier_excel_perso(self,dict_relation_shp_liste,dict_dict_info_REF,dict_decoupREF):
        #Remplissage des onglets
        dict_dict_info_REF['df_info_ME'] = DictDfInfoShp.ajout_surface_ME(dict_dict_info_REF['df_info_ME'],dict_decoupREF)
        dict_dict_info_REF = DictDfInfoShp.boost_df_info_ME(dict_dict_info_REF,dict_relation_shp_liste,self)
        if "df_info_SME" in list(dict_dict_info_REF):
            dict_dict_info_REF = DictDfInfoShp.boost_df_info_SME(dict_dict_info_REF)

        for entite_custom,contenu_custom in self.items():
            contenu_custom = NomCustomMaitre.definition_liste_REF_hors_echelle_base_REF(contenu_custom)
            
        for entite_custom,contenu_custom in self.items():
            #Creation fichier tableaux excel avec onglets vierges
            if contenu_custom.echelle_REF == "MO":
                excel_modif = config_DORA.recuperation_excel_MIA_MO_vierge_DORA()
                worksheet= excel_modif['tableau a remplir']
                worksheet['A1']='Tableau DORA actions MIA MO ' + entite_custom
            if contenu_custom.echelle_REF == "DEP":
                excel_modif = config_DORA.recuperation_excel_MIA_DEP_vierge_DORA()
                worksheet= excel_modif['tableau a remplir']
                worksheet['A1']='Tableau DORA actions MIA DEP ' + entite_custom                
            #excel_modif = tableau_excel.ajout_onglet_AIDE_liste_ME(excel_modif,contenu_custom.CODE_custom,dict_relation_shp_liste,dict_dict_info_REF)
            excel_modif = tableau_excel.ajout_onglet_AIDE_liste_REF(self,excel_modif,contenu_custom.CODE_custom,dict_relation_shp_liste,dict_dict_info_REF,contenu_custom)
            excel_modif = tableau_excel.ajout_onglet_info_PPG(excel_modif,contenu_custom.CODE_custom,dict_relation_shp_liste,dict_dict_info_REF)
            
            excel_modif = tableau_excel.ajout_onglet_Lien_REF_ME(self,excel_modif,contenu_custom.CODE_custom,dict_relation_shp_liste,dict_dict_info_REF,contenu_custom)
            '''if ENVIRONMENT=="developpement":
                excel_modif.save("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MIA/" + contenu_custom.echelle_REF + "/tableaux_vierge/Tableau_suivi_MIA_" + contenu_custom.echelle_REF + "_vierge_" + entite_custom + ".xlsx")'''
            return excel_modif

    def export_fichier_excel_osmose_conversion_dora(self):
        workbook = config_DORA.recuperation_excel_vierge_Osmose()
        for entite_custom,contenu_custom in self.items():
            workbook.save("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MIA/" + contenu_custom.echelle_REF + "/Tableau_suivi_osmose_" + entite_custom + ".xlsx")        
            excel_modif = load_workbook("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MIA/" + contenu_custom.echelle_REF + "/Tableau_suivi_osmose_" + entite_custom + ".xlsx", read_only=False, keep_vba=False)
            excel_modif = tableau_excel.ajout_onglet_actions(excel_modif,contenu_custom.df)
            excel_modif = tableau_excel.ajout_onglet_attributs(excel_modif,contenu_custom.df_attributs)
            excel_modif.save("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MIA/" + contenu_custom.echelle_REF + "/Tableau_suivi_osmose_" + entite_custom + ".xlsx")

    def export_fichier_excel_osmose_maj(self):
        workbook = load_workbook("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/TABLEAU_MAJ_OSMOSE_VIERGE.xlsx", read_only=False)
        for type_dict_donnees,dict_donnees in self.items():
            for entite_custom,contenu_custom in dict_donnees.items():
                workbook.save("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MAJ Osmose/tableau_propre_MAJ/Tableau_suivi_MIA_MO_vierge_" + entite_custom + ".xlsx")        
                excel_modif = load_workbook("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MAJ Osmose/tableau_propre_MAJ/Tableau_suivi_MIA_MO_vierge_" + entite_custom + ".xlsx", read_only=False, keep_vba=False)
                excel_modif = tableau_excel.ajout_onglet_actions(excel_modif,contenu_custom.df)
                excel_modif = tableau_excel.ajout_onglet_attributs(excel_modif,contenu_custom.df_attributs)
                excel_modif.save("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MAJ Osmose/tableau_propre_MAJ/Tableau_suivi_MIA_MO_vierge_" + entite_custom + ".xlsx")
                if hasattr(contenu_custom,"df_actions_a_recreer"):
                    excel_modif = load_workbook("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/TABLEAU_CREATION_OSMOSE_VIERGE.xlsx", read_only=False, keep_vba=False)
                    excel_modif = tableau_excel.ajout_onglet_actions(excel_modif,contenu_custom.df_actions_a_recreer)
                    excel_modif = tableau_excel.ajout_onglet_attributs(excel_modif,contenu_custom.df_attributs_df_actions_a_creer)
                    excel_modif.save("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MAJ Osmose/tableau_propre_MAJ/Tableau_suivi_MIA_MO_vierge_" + entite_custom + "_creer_actions" + ".xlsx")

    def attributs_df_filtre_dans_dict_custom_maitre(self,dict_df_donnees):
        for entite_custom,contenu_custom in self.items():
            contenu_custom.df_filtre_tableau = dict_df_donnees["dict_dict_df_actions_originaux"][entite_custom].df_filtre_tableau
        return self

    def attributs_df_log_erreur_dans_dict_custom_maitre(self,dict_df_donnees):
        for entite_custom,contenu_custom in self.items():
            contenu_custom.df_log_erreur = dict_df_donnees["dict_dict_df_actions_originaux"][entite_custom].df_log_erreur
        return self

    def attributs_echelle_REF_dans_dict_custom_maitre(self,dict_df_donnees):
        for entite_custom,contenu_custom in self.items():
            contenu_custom.echelle_df = dict_df_donnees["dict_dict_df_actions_originaux"][entite_custom].echelle_df
        return self

    def export_log_df_erreur(self):
        for entite_custom,contenu_custom in self.items():
            print("attention, il y a plusieurs logs")
            if ENVIRONMENT=="developpement":
                contenu_custom.df_log_erreur.to_csv("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MIA/" + contenu_custom.echelle_df +  "/log/log "+ entite_custom + ".csv",index=False)
        return contenu_custom.df_log_erreur

    def export_tableau_excel_complet(self,dict_df_donnees):
        for entite_custom,contenu_custom in self.items():
            fichier_excel = dict_df_donnees["dict_dict_df_actions_originaux"][entite_custom].fichier_brut
            feuille_a_remplir = fichier_excel['tableau a remplir']

            format_cellule_rouge = NamedStyle(name="format_cellule_rouge")
            format_cellule_rouge.font = copy(feuille_a_remplir.cell(row=4, column=1).font)
            format_cellule_rouge.alignment = copy(feuille_a_remplir.cell(row=4, column=1).alignment)
            format_cellule_rouge.fill = copy(feuille_a_remplir.cell(row=4, column=1).fill)
            format_cellule_rouge.border = copy(feuille_a_remplir.cell(row=4, column=1).border)
            fichier_excel.add_named_style(format_cellule_rouge)

            for numero_col,nom_colonne in enumerate(list(contenu_custom.df_filtre_tableau)):
                feuille_a_remplir.cell(row=4, column=50+numero_col).value = nom_colonne   
                feuille_a_remplir.cell(row=4, column=50+numero_col).style = "format_cellule_rouge"
            for index, row in contenu_custom.df_filtre_tableau.iterrows():
                for numero_ligne,contenu_ligne in enumerate(row):
                    feuille_a_remplir.cell(row=6+index, column=50+numero_ligne).value = contenu_ligne
            feuille_a_remplir.cell(row=1,column=1).value = "Tableau DORA actions MIA " + contenu_custom.echelle_df + " final " + contenu_custom.NOM_custom
            if ENVIRONMENT=="developpement":
                fichier_excel.save("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MIA/" + contenu_custom.echelle_REF + "/Tableaux_final/Tableau_final_" + contenu_custom.NOM_custom + ".xlsx")
        return tableau_excel

class NomCustomMaitre(dict):
    @property
    def _constructor(self):
        return NomCustomMaitre        

    def attribut_NOM_custom(self,NOM_custom,echelle_REF=None):
        self.NOM_custom = NOM_custom
        self.echelle_REF = echelle_REF
        return self

    def definition_liste_REF_hors_echelle_base_REF(self):
        if self.echelle_REF=="MO":
            self.liste_REF = ["PPG","ROE"]
        if self.echelle_REF=="DEP":
            self.liste_REF = ["MO","SAGE","BVG","PPG","ROE"]
        return self

    def creation_bloc_texte_simple(self,orientation,type_icone,sous_type,colonne_texte,nom_custom,taille_globale_carto="petite"):
        df_bloc_texte_simple = BlocTexteSimple(taille_globale_carto)
        df_bloc_texte_simple.type_icone = type_icone
        df_bloc_texte_simple.sous_type = sous_type
        df_bloc_texte_simple.colonne_texte = colonne_texte
        df_bloc_texte_simple.nom_custom = nom_custom
        df_bloc_texte_simple.liste_nom_colonne_a_garder = []
        if orientation=="normal":
            self['dict_boite_maitre_normal']['df_bloc_texte'] = df_bloc_texte_simple 
        if orientation=="orthogonal":
            self['dict_boite_maitre_ortho']['df_bloc_texte'] = df_bloc_texte_simple 
        return self

    def creation_bloc_icone(self,orientation,type_icone,sous_type,colonne_nb_icone,nom_custom,taille_globale_carto="petite"):
        df_bloc_icone = BlocIcone(taille_globale_carto)
        df_bloc_icone.type_icone = type_icone
        df_bloc_icone.type = 'bloc_icone'
        df_bloc_icone.avancement_max = 4
        df_bloc_icone.sous_type = sous_type
        df_bloc_icone.colonne_nb_icone = colonne_nb_icone
        df_bloc_icone.nom_custom = nom_custom
        df_bloc_icone.liste_nom_colonne_a_garder = []
        if orientation=="normal":
            self['dict_boite_maitre_normal']['df_bloc_icone'] = df_bloc_icone 
        if orientation=="orthogonal":
            self['dict_boite_maitre_ortho']['df_bloc_icone'] = df_bloc_icone 
        return self

    def creation_bloc_lignes_multiples(self,orientation,type_icone,sous_type,colonne_texte,nom_custom,taille_globale_carto="petite"):
        df_bloc_lignes_multiples = BlocLignesMultiples(taille_globale_carto)
        df_bloc_lignes_multiples.type = 'bloc_lignes_multiples'
        df_bloc_lignes_multiples.type_icone = type_icone
        df_bloc_lignes_multiples.avancement_max = 4
        df_bloc_lignes_multiples.sous_type = sous_type
        df_bloc_lignes_multiples.colonne_texte = colonne_texte
        df_bloc_lignes_multiples.nom_custom = nom_custom
        df_bloc_lignes_multiples.liste_nom_colonne_a_garder = []
        if orientation=="normal":
            self['dict_boite_maitre_normal']['df_bloc_lignes_multiples'] = df_bloc_lignes_multiples 
        if orientation=="orthogonal":
            self['dict_boite_maitre_ortho']['df_bloc_lignes_multiples'] = df_bloc_lignes_multiples         
        return self