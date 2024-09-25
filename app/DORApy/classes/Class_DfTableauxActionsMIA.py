import pandas as pd
import geopandas as gpd
from app.DORApy.classes.modules import dataframe
import os.path
from os import path
import sys
import re
import numpy as np
from openpyxl import load_workbook
import copy
from app.DORApy.classes import Class_Folder
from datetime import date

from app.DORApy.classes.modules import config_DORA

environment = os.getenv('ENVIRONMENT')
bucket_users_files = os.getenv('S3_BUCKET_USERS_FILES')
today = date.today()

dict_config_espace,dict_config_police = config_DORA.creation_dicts_config()
dict_config_actions_MIA_DORA = config_DORA.import_dict_config_actions_MIA_DORA()
list_rep_MO_gemapi = Class_Folder.lister_rep_et_fichiers(bucket_users_files, "MO_gemapi/")

##########################################################################################
#Class DfTableauxActionsMIA
##########################################################################################
class DfTableauxActionsMIA:
    def __init__(self, path):
        self.path = os.path.normpath(path)
        self.recuperation_xlsx_brut()
        self.recuperation_xlsx_en_df()
               
        ###Changement attributs
        self.get_echelle_df()
        self.recuperation_CODE_CUSTOM()
        self.get_name()
        self.get_dict_nom_col()
        self.get_dict_type_col()
        self.get_dict_dict_nb_chiffres()
        self.get_numero_dep()
        self.get_annee_remplissage()
        self.get_echelle_REF_base()
        self.suppression_lignes_inutiles()
        self.attribution_col()
        self.strip_et_tease_col()
        self.strip_et_tease_contenu_col()

        ###Changement sur le df
        self.changement_nom_col_tableaux_actions_MIA()
        self.suppression_dernieres_lignes_vides()

        #petite sauvegarde du DF avant modif
        self.stockage_df_brut()
        self.changement_contenu_case_vide_NAN_str_list()
        self.traitement_Int64()
        self.traitement_str_et_list()
        self.completer_col_NOM_MO()


    def __str__(self):
        return f"tableau action : {self.CODE_CUSTOM},{self.NOM_MO}"
    def __repr__(self):
        return f"tableau action : {self.CODE_CUSTOM},{self.NOM_MO}"

    def recuperation_xlsx_brut(self):
        self.fichier_brut=load_workbook(filename=self.path)
    def recuperation_xlsx_en_df(self):
        self.df=pd.read_excel(self.path,sheet_name="tableau a remplir")
    def stockage_df_brut(self):
        self.df_brut=copy.deepcopy(self.df)
    def get_echelle_df(self):
        print((self.path).split(os.sep), file=sys.stderr)
        if (self.path).split(os.sep)[-3]=="MO_gemapi":
            self.echelle_df = "MO"
        if (self.path).split(os.sep)[-3]=="DEP":
            self.echelle_df = "DEP"
    def recuperation_CODE_CUSTOM(self):
        self.CODE_CUSTOM = self.path.split(os.sep)[-2]            
    def get_dict_nom_col(self):
        self.dict_nom_col = config_DORA.creation_dict_dict_config_df_actions_MIA()['dict_conv_nom_col_DORA_'+self.echelle_df]
    def get_dict_type_col(self):
        self.dict_type_col = config_DORA.creation_dict_dict_config_df_actions_MIA()['dict_conv_type_col_DORA_'+self.echelle_df]
    def get_dict_dict_nb_chiffres(self):    
        self.dict_nb_chiffres = config_DORA.creation_dict_dict_config_df_actions_MIA()['dict_nb_chiffres_col_DORA_'+self.echelle_df]
    def get_name(self):
        if self.echelle_df == "MO":
            dict_MO_liste_NOM_MO = {folder.name:folder.NOM_MO for folder in list_rep_MO_gemapi}
            self.name = dict_MO_liste_NOM_MO[self.CODE_CUSTOM]
    def get_numero_dep(self):
        if self.echelle_df == "MO":
            dict_MO_liste_CODE_DEP = {folder.name:folder.list_CODE_DEP for folder in list_rep_MO_gemapi}
            self.numero_dep = dict_MO_liste_CODE_DEP[self.CODE_CUSTOM]
    def get_annee_remplissage(self):
        try:
            self.annee_remplissage = int(self.df.iat[1,0][-4:])
        except:
            self.annee_remplissage = 2024

    def get_echelle_REF_base(self):
        df_SME=pd.read_excel(self.path,sheet_name="Pour lien ME SME")
        if len(df_SME)>1:
            self.echelle_base_REF = "SME"
        else:
            self.echelle_base_REF = "ME"

    def suppression_lignes_inutiles(self):
        self.df.drop(self.df.index[[0,1,3]], inplace=True)

    def attribution_col(self):
        self.df = self.df.reset_index(drop=True)
        self.df = self.df.rename(columns=self.df.iloc[0]).loc[1:]
        self.df = self.df.reset_index(drop=True)

    def changement_nom_col_tableaux_actions_MIA(self):
        self.df = self.df.rename(columns=self.dict_nom_col)
        if self.echelle_base_REF=="SME":
            self.df = self.df.rename({"CODE_ME":"CODE_SME"},axis=1)
        self.df = self.df[[x for x in list(self.df) if not x.startswith('Unnamed')]]


    def changement_contenu_case_vide_NAN_str_list(self):
        dict_chgmt_type_col_df_tableau_action_MIA_REF = self.dict_type_col
        for nom_col in list(self.df):
            if nom_col in dict_chgmt_type_col_df_tableau_action_MIA_REF:
                if (dict_chgmt_type_col_df_tableau_action_MIA_REF[nom_col]=="str" or dict_chgmt_type_col_df_tableau_action_MIA_REF[nom_col]=="list"):
                    self.df[nom_col] = self.df[nom_col].replace('#N/D', np.nan)

    def traitement_str_et_list(self):
        for nom_col in list(self.df):
            if nom_col in self.dict_type_col:
                if self.dict_type_col[nom_col]=="list":
                    if any(x==x for x in self.df[nom_col].to_list()):
                        self.df.loc[~self.df[nom_col].isnull(),nom_col] = self.df[nom_col].astype(str).str.split(';')
                        self.df.loc[~self.df[nom_col].isnull(),nom_col] = self.df.loc[~self.df[nom_col].isnull(),nom_col].apply(lambda x: [entite_REF.strip() for entite_REF in x])
                        self.df.loc[self.df[nom_col].isnull(),nom_col] = self.df[nom_col].apply(lambda x: [])
                        self.df[nom_col] = self.df[nom_col].apply(lambda x:[entite_REF for entite_REF in x if len(entite_REF)>0])
                        if nom_col == "CODE_ME":
                            self.df.loc[~self.df[nom_col].isnull(),nom_col] = self.df[nom_col].apply(lambda x: ["".join(['FR',ME]) if (bool(re.match(r'^[A-Za-z]{4,}\d+', ME))==False and ME!='nan') else ME for ME in x])
                        
                if self.dict_type_col[nom_col]=="str":
                    self.df[nom_col] = self.df[nom_col].astype(self.dict_type_col[nom_col])


    def traitement_Int64(self):
        dict_chgmt_type_col_df_tableau_action_MIA_REF = self.dict_type_col
        dict_chgmt_nb_df_tableau_action_MIA_REF = self.dict_nb_chiffres
        for nom_col in list(self.df):
            if nom_col in dict_chgmt_type_col_df_tableau_action_MIA_REF:
                
                if dict_chgmt_type_col_df_tableau_action_MIA_REF[nom_col]=="Int64":
                    if isinstance(dict_chgmt_nb_df_tableau_action_MIA_REF[nom_col],str):
                        self.df[nom_col] = self.df[nom_col].apply(lambda x:re.sub(r'[^\d\s]', '', str(x)))
                        nb_chiffres = int(dict_chgmt_nb_df_tableau_action_MIA_REF[nom_col])
                        liste_annee = self.df[nom_col].to_list()
                        list_tempo = []
                        for annee in liste_annee:
                            liste_annnee_potentielle = annee.split(" ")
                            for annee_pot in liste_annnee_potentielle:
                                ajout_fait=0
                                if len(annee_pot.strip())==nb_chiffres:
                                    ajout_fait=1
                                    annee_choisie = annee_pot.strip()
                                    list_tempo.append(annee_choisie)
                                    break
                            if ajout_fait==0:
                                list_tempo.append('nan')
                        self.df[nom_col] = list_tempo

    def suppression_dernieres_lignes_vides(self):
        def derniere_ligne_non_vide_df(df,nom_col):
            reversed_self = df.iloc[::-1]
            df_coupe = reversed_self.loc[reversed_self[nom_col]!="nan"]
            if len(df_coupe)>0:
                index_derniere_ligne_remplie_df = df_coupe.index[0]
            else:
                index_derniere_ligne_remplie_df = 0
            return index_derniere_ligne_remplie_df
        
        derniere_ligne_Avancement_non_nul = derniere_ligne_non_vide_df(self.df,"Avancement")
        derniere_ligne_NOM_TYPE_ACTION_DORA_non_nul = derniere_ligne_non_vide_df(self.df,"NOM_TYPE_ACTION_DORA")
        derniere_ligne_NOM_PERSO_ACTION_non_nul = derniere_ligne_non_vide_df(self.df,"NOM_PERSO_ACTION")

        derniere_ligne = max([derniere_ligne_Avancement_non_nul,derniere_ligne_NOM_TYPE_ACTION_DORA_non_nul,derniere_ligne_NOM_PERSO_ACTION_non_nul])
        self.df = self.df.iloc[:derniere_ligne+1]

    def strip_et_tease_col(self):
        for col in list(self.df):
            self.df = self.df.rename(columns=lambda x: x.strip())

    def strip_et_tease_contenu_col(self):
        for col in list(self.df):
            try:
                self.df[col] = self.df[col].apply(lambda x:str(x).strip())
                self.df[col] = self.df[col].apply(lambda x:x.replace('/n',' ', regex=True))
            except:
                pass

    def completer_col_NOM_MO(self):
        if self.echelle_df =='MO':
            self.df['NOM_MO'] = self.df['NOM_MO'].astype(str)
            self.df.loc[self.df['NOM_MO']=="nan",'NOM_MO'] = self.name
        if self.echelle_df =='DEP':
            list_NOM_MO = dict_dict_info_REF['df_info_MO']['NOM_MO'].to_list()
            dict_NOM_MO_DDT_NOM_MO_norme = dict(zip(dict_dict_info_REF['df_info_MO']['NOM_init'].to_list(),dict_dict_info_REF['df_info_MO']['NOM_MO'].to_list()))
            df_tableau['NOM_MO'] = df_tableau['NOM_MO'].astype(str)
            df_tableau['NOM_MO'] = df_tableau['NOM_MO'].apply(lambda x: dict_NOM_MO_DDT_NOM_MO_norme[x] if x in dict_NOM_MO_DDT_NOM_MO_norme else x)
        if self.echelle_df =='global_Osmose':
            dict_CODE_SIRET_NOM_MO = dict(zip(dict_dict_info_REF['df_info_MO']['CODE_SIRET'].to_list(),dict_dict_info_REF['df_info_MO']['NOM_MO'].to_list()))
            df_tableau['NOM_MO_tempo'] = df_tableau['CODE_SIRET'].astype(str).apply(lambda x: dict_CODE_SIRET_NOM_MO[x] if x in dict_CODE_SIRET_NOM_MO else "nan")
            df_tableau.loc[df_tableau['NOM_MO_tempo']!='nan',"NOM_MO"] = df_tableau['NOM_MO_tempo']
            df_tableau = df_tableau[[x for x in list(df_tableau) if x!="NOM_MO_tempo"]]


##########################################################################################
#Les verifs
##########################################################################################
    def verif_nom_fichier(dict_dict_df_actions_originaux,dict_dict_info_REF,dict_log):
        print("verif nom fichier tableau : ")
        for nom_tableau in list(dict_dict_df_actions_originaux):
            if dict_dict_df_actions_originaux[nom_tableau].echelle_df=='MO':
                if nom_tableau in dict_dict_info_REF['df_info_MO']['NOM_MO'].to_list():
                    dict_log[nom_tableau]["verif nom fichier tableau : "] = "Tous les systèmes OK !"
                    print("OK")
                if nom_tableau not in dict_dict_info_REF['df_info_MO']['NOM_MO'].to_list():
                    print("La premiere case du fichier " + nom_tableau +" est mauvais. Il doit prendre la forme 'Tableau DORA actions MIA MO + le nom du syndicat'")
                    print("ex : Tableau DORA actions MIA MO CCE")
                    dict_log[nom_tableau]["verif nom fichier tableau : "] = "Le nom du fichier " + nom_tableau +" est mauvais. Il doit prendre la forme tableau_vierge_ + le nom du syndicat"
                    del dict_dict_df_actions_originaux[nom_tableau]
            if dict_dict_df_actions_originaux[nom_tableau].echelle_df=='DEP': 
                try:
                    if nom_tableau in dict_dict_info_REF['df_info_DEP']['NOM_DEP'].to_list():
                        dict_log[nom_tableau]["verif nom fichier tableau : "] = "Tous les systèmes OK !"
                        print("OK")
                except:
                    print("La premiere case du fichier " + nom_tableau +" est mauvais. Il doit prendre la forme 'Tableau DORA actions MIA DEP + le nom du département'")
                    print("ex : Tableau DORA actions MIA DEP CHARENTE")
                    dict_log[nom_tableau]["verif nom fichier tableau : "] = "Le nom du fichier " + nom_tableau +" est mauvais. Il doit prendre la forme 'Tableau DORA actions MIA DEP + le nom du département'"
                    del dict_dict_df_actions_originaux[nom_tableau]                            
        return dict_log
    
    def verif_nom_col_fichier(dict_dict_df_actions_originaux,dict_log):
        for nom_tableau in list(dict_dict_df_actions_originaux):
            liste_col_erreur = [x for x in list(dict_dict_df_actions_originaux[nom_tableau].df) if x not in list(dict_dict_df_actions_originaux[nom_tableau].dict_type_col)]
            if len(liste_col_erreur)>0:
                print("Il manque des colonnes ou celles-ci sont mal nommées pour : " + nom_tableau)
                print("Voici les colonnes erreurs :")
                print(liste_col_erreur)
                dict_log[nom_tableau]["col_erreurs"] = liste_col_erreur
            if len(liste_col_erreur)==0:
                print("Pour : " + nom_tableau)
                print("Les noms de col sont bons")
                dict_log[nom_tableau]["col_erreurs"] = "Tous les systèmes OK !"
        return dict_log   

##########################################################################################
#Mise en forme general
##########################################################################################
    def changement_contenu_case_vide_NAN(df_tableau,echelle_df,dict_type_col):
        if echelle_df =='MO':
            dict_chgmt_type_col_df_tableau_action_MIA_REF = dict_type_col
        if echelle_df =='DEP':
            dict_chgmt_type_col_df_tableau_action_MIA_REF = dict_type_col
        if echelle_df =='global_Osmose':
            dict_chgmt_type_col_df_tableau_action_MIA_REF = dict_type_col    
        for nom_col in list(df_tableau):
            if nom_col in dict_chgmt_type_col_df_tableau_action_MIA_REF:
                if (dict_chgmt_type_col_df_tableau_action_MIA_REF[nom_col]=="str" or dict_chgmt_type_col_df_tableau_action_MIA_REF[nom_col]=="list"):
                    df_tableau[nom_col] = df_tableau[nom_col].replace('#N/D', np.nan)
        return df_tableau    

    def changement_type_col_tableaux_actions_MIA(df_tableau,echelle_df,dict_dict_info_REF,dict_typ_col,dict_nb_chiffres):
        for nom_col in list(df_tableau):
            if nom_col in dict_typ_col:
                if dict_typ_col[nom_col]=="Int64":
                    df_tableau[nom_col] = df_tableau[nom_col].astype(str)
                    df_tableau[nom_col] = df_tableau[nom_col].apply(lambda x: dataframe.extraire_string(x,dict_nb_chiffres[nom_col]))
                    df_tableau[nom_col] = df_tableau[nom_col].astype(dict_typ_col[nom_col])
                if dict_typ_col[nom_col]=="list":
                    if any(x==x for x in df_tableau[nom_col].to_list()):
                        df_tableau.loc[~df_tableau[nom_col].isnull(),nom_col] = df_tableau[nom_col].astype(str).str.split(';')
                        df_tableau.loc[~df_tableau[nom_col].isnull(),nom_col] = df_tableau.loc[~df_tableau[nom_col].isnull(),nom_col].apply(lambda x: [entite_REF.strip() for entite_REF in x])
                        df_tableau.loc[df_tableau[nom_col].isnull(),nom_col] = df_tableau[nom_col].apply(lambda x: [])
                        df_tableau[nom_col] = df_tableau[nom_col].apply(lambda x:[entite_REF for entite_REF in x if len(entite_REF)>0])
                        if nom_col == "CODE_ME":
                            list_CODE_ME = dict_dict_info_REF['df_info_ME']['CODE_ME'].to_list()
                            df_tableau.loc[~df_tableau[nom_col].isnull(),nom_col] = df_tableau[nom_col].apply(lambda x: ["".join(['FR',ME]) if "FR" + ME in list_CODE_ME else ME for ME in x])
                        
                if dict_typ_col[nom_col]=="str":
                    df_tableau[nom_col] = df_tableau[nom_col].astype(dict_typ_col[nom_col])
        return df_tableau

##########################################################################################
#Modification du tableau
##########################################################################################
    def chgt_col_CODE_ME_ou_CODE_SME_list_vers_string(df,dict_type_col):
        if "CODE_ME" in list(df):
            df = df.explode('CODE_ME')
            df['CODE_ME'] = df['CODE_ME'].fillna('nan')
            df = df.reset_index(drop=True)
            dict_type_col['CODE_ME'] = 'str'

        if "CODE_SME" in list(df):
            df = df.explode('CODE_SME')
            df['CODE_SME'] = df['CODE_SME'].fillna('nan')   
            df = df.reset_index(drop=True)
            dict_type_col['CODE_SME'] = 'str'
        return df

    def remplacement_NOM_PPG_si_necessaire(df_tableau,CODE_MO,dict_dict_info_REF,dict_relation_shp_liste):
        list_PPG_dans_df = list(set(df_tableau['NOM_PPG'].to_list()))
        list_PPG_dans_df = [x for x in list_PPG_dans_df if x!='nan']
        nom_tableau = dict_dict_info_REF['df_info_MO'].dict_CODE_NOM[CODE_MO]
        for NOM_PPG_dans_df_tableau in list_PPG_dans_df:
            if NOM_PPG_dans_df_tableau not in dict_dict_info_REF['df_info_PPG']['NOM_PPG'].to_list():
                print("Pour le tableau " + nom_tableau + ", pas de " + NOM_PPG_dans_df_tableau + " concordant trouvé dans df_info_PPG.csv")  
                liste_PPG_du_CUSTOM = dict_relation_shp_liste["dict_liste_PPG_par_CUSTOM"][CODE_MO]
                if len(liste_PPG_du_CUSTOM)==0:
                    print("Pas de PPG pour ce MO dans df_info_PPG")
                if len(liste_PPG_du_CUSTOM)==1:
                    print("Mais il n'y a qu'un seul PPG dans df_info_PPG qui correspond à ce CUSTOM : " +  nom_tableau)
                    CODE_PPG = dict_relation_shp_liste["dict_liste_PPG_par_CUSTOM"][CODE_MO][0]
                    NOM_PPG = dict_dict_info_REF['df_info_PPG'].dict_CODE_NOM[dict_relation_shp_liste["dict_liste_PPG_par_CUSTOM"][CODE_MO][0]]
                    df_tableau.loc[(df_tableau['NOM_PPG']!='nan')&(df_tableau['NOM_PPG']!=NOM_PPG),"CODE_PPG"]=CODE_PPG
                    df_tableau.loc[df_tableau['NOM_PPG']==NOM_PPG_dans_df_tableau,"NOM_PPG"] = NOM_PPG
                if len(liste_PPG_du_CUSTOM)>1:
                    print("Plusieurs PPG dans df_info_PPG qui correspondent à ce CUSTOM : " +  nom_tableau)
        return df_tableau

    def mise_en_forme_col_action_phare(df_tableau):
        if "Action_phare" in list(df_tableau):
            df_tableau.loc[df_tableau["Action_phare"]!='nan',"Action_phare"] = "x"
            df_tableau.loc[df_tableau["Action_phare"]=='nan',"description_action_phare"] = 'nan'
        return df_tableau
    
    def suppression_lignes_sans_avancement(df_tableau,dict_type_col):
        df_tableau = df_tableau.loc[df_tableau['Avancement']!='nan']
        return df_tableau    

    def ajout_colonne_CODE_REF_permanent(df,dict_dict_info_REF,echelle_df,dict_type_col):
        list_REF_df_info = [x.split("_")[-1] for x in list(dict_dict_info_REF)]
        list_col_NOM = dataframe.extraction_liste_col_NOM(df,list_REF_df_info)
        for nom_col_REF in list_col_NOM:
            CODE_REF = "CODE_" + nom_col_REF.split("_")[1]
            if CODE_REF not in list(df):
                type_REF = nom_col_REF.split("_")[1]
                dict_NOM_CODE_REF = dict_dict_info_REF['df_info_'+type_REF].dict_NOM_CODE
                df[CODE_REF] = df[nom_col_REF].apply(lambda x: dict_NOM_CODE_REF[x] if x in dict_NOM_CODE_REF else "nan")
                if CODE_REF not in dict_type_col:
                    df[CODE_REF] = df[CODE_REF].fillna('nan')
                    dict_type_col[CODE_REF] = 'str'
        return df

    def ajout_colonne_manquante_df_type_DORA(df):
        dict_config_col_BDD_DORA_vierge = config_DORA.import_dict_config_col_BDD_DORA_vierge()
        for nom_col in dict_config_col_BDD_DORA_vierge['type_col']:
            if nom_col not in list(df):
                if dict_config_col_BDD_DORA_vierge['type_col'][nom_col]=="str" or dict_config_col_BDD_DORA_vierge['type_col'][nom_col]=="list":
                    df[nom_col] = "nan"
                if dict_config_col_BDD_DORA_vierge['type_col'][nom_col]=="Int64":
                    df[nom_col] = pd.NA 
                dict_type_col = dict_config_col_BDD_DORA_vierge['type_col'][nom_col]            
        return df

    def traitement_BDD_OSMOSE_format_DORA(df,dict_dict_info_REF,echelle_df):
        ###REPRENDRE ICI : Il faut rassembler les actions d'Osmose par echelle REF sup (Ex : Est-ce que l'action sur les 10 ME est à une echelle de PPG ou BVG ou pas rassemblable ?)
        if echelle_df =='global_Osmose':
            df["CODE_TYPE_ACTION_OSMOSE"] = df["CODE_TYPE_ACTION_OSMOSE"].apply(lambda x:x.split("-")[-1])
            df["Avancement"] = df["Avancement"].apply(lambda x:x.split("-")[-1])
        
        return df
    
    def mise_en_forme_BDD_DORA(df,dict_config_col_BDD_DORA_vierge):
        for nom_col in list(df):
            if nom_col in dict_config_col_BDD_DORA_vierge:
                if (dict_config_col_BDD_DORA_vierge[nom_col]=="str" or dict_config_col_BDD_DORA_vierge[nom_col]=="list"):
                    df[nom_col] = df[nom_col].fillna(np.nan)   
        return df

    def definition_col_localisation_principale(df,echelle_df,echelle_base_REF,dict_type_col):
        if echelle_df == 'DEP':
            list_REF_a_remonter = ['MO','SAGE','PPG','BVG','ME']
            df["echelle_princ_action"] = "Erreur : Pas de localisation trouvée"
            for echelle_a_check in list_REF_a_remonter:
                if dict_type_col['CODE_'+echelle_a_check]=="str":
                    df.loc[df['CODE_'+echelle_a_check]!='nan',"echelle_princ_action"] = echelle_a_check
                if dict_type_col['CODE_'+echelle_a_check]=="list":
                    df.loc[df['CODE_'+echelle_a_check].str.len()>0,"echelle_princ_action"] = echelle_a_check
        if echelle_df == 'MO':
            df.loc[df['CODE_'+echelle_base_REF]!='nan',"echelle_princ_action"] = echelle_base_REF
            df.loc[df['NOM_'+echelle_base_REF]!='nan',"echelle_princ_action"] = echelle_base_REF
            df.loc[df['Integral_PPG']!='nan',"echelle_princ_action"] = "PPG"
            df.loc[df['Integral_MO']!='nan',"echelle_princ_action"] = "MO"
        if echelle_df == 'global_Osmose':
            df["echelle_princ_action"] = "ME"

        if dict_type_col['CODE_'+echelle_base_REF]=="list":
            df.loc[df['echelle_princ_action']!=echelle_base_REF,"CODE_"+echelle_base_REF] = df["CODE_"+echelle_base_REF].apply(lambda x:[])
        if dict_type_col['CODE_'+echelle_base_REF]=="str":
            df.loc[df['echelle_princ_action']!=echelle_base_REF,"CODE_"+echelle_base_REF] = "nan"
        return df

    def ajout_CODE_REF(df,dict_CUSTOM_maitre):
        list_echelle_col_echelle_princ_action = list(set(df['echelle_princ_action'].to_list()))
        list_echelle_col_echelle_princ_action = [x for x in list_echelle_col_echelle_princ_action if x in dict_CUSTOM_maitre.liste_echelle_REF_projet]
        for echelle_princ_action in list_echelle_col_echelle_princ_action:
            df.loc[df['echelle_princ_action']==echelle_princ_action,'CODE_REF'] = df['CODE_'+echelle_princ_action]
        return df
    
    def filtre_par_CODE_MO_si_df_DORA_MO_specifique_au_CUSTOM(self,dict_donnees,CODE_CUSTOM):
        liste_CODE_CUSTOM_DORA = [v.CODE_CUSTOM for k,v in dict_donnees["dict_dict_df_actions_originaux"].items() if v.echelle_df=="MO"]
        if CODE_CUSTOM in liste_CODE_CUSTOM_DORA:
            self = self.loc[self['CODE_MO']==CODE_CUSTOM]
        return self

    def separation_entite_normal_ou_ortho_echelle_CUSTOM_MO(df_BDD,dict_donnees,liste_echelle_REF_total,liste_echelle_boite_ortho,dict_relation_shp_liste,echelle_base_REF,CODE_CUSTOM):
        dict_type_col = dict_donnees['BDD_DORA'].dict_type_col
        def tri_echelle_CUSTOM_MO(ligne_df_BDD):
            echelle_actuelle = ligne_df_BDD['echelle_princ_action']
            for echelle_a_essayer in [x for x in liste_echelle_REF_total if x!=echelle_actuelle]:
                if echelle_a_essayer!=echelle_base_REF:
                    CODE_REF_echelle_a_essayer = dict_relation_shp_liste['dict_liste_' + echelle_a_essayer + '_par_CUSTOM'][CODE_CUSTOM][0]
                    list_CODE_REF_echelle_a_essayer = dict_relation_shp_liste['dict_liste_' + echelle_base_REF + '_par_' + echelle_a_essayer][CODE_REF_echelle_a_essayer]
                    if dict_type_col["CODE_"+echelle_actuelle]=="list":
                        list_CODE_REF = ligne_df_BDD['CODE_REF']
                    if dict_type_col["CODE_"+echelle_actuelle]=="str":
                        CODE_REF = ligne_df_BDD['CODE_REF']
                        if 'dict_liste_' + echelle_base_REF + '_par_' + echelle_actuelle not in dict_relation_shp_liste:
                            dict_relation_shp_liste['dict_liste_' + echelle_base_REF + '_par_' + echelle_actuelle] = {value: key for key in dict_relation_shp_liste['dict_liste_' + echelle_actuelle + '_par_' + echelle_a_essayer] for value in dict_relation_shp_liste['dict_liste_' + echelle_actuelle + '_par_' + echelle_a_essayer][key]}
                        if CODE_REF in dict_relation_shp_liste['dict_liste_' + echelle_base_REF + '_par_' + echelle_actuelle]:
                            list_CODE_REF = dict_relation_shp_liste['dict_liste_' + echelle_base_REF + '_par_' + echelle_actuelle][CODE_REF]
                        if CODE_REF not in dict_relation_shp_liste['dict_liste_' + echelle_base_REF + '_par_' + echelle_actuelle]:  
                            nouveau_CODE_REF = []
                            break
                    liste_entite_base_concerne_dans_CUSTOM = [x for x in list_CODE_REF if x in list_CODE_REF_echelle_a_essayer]
                    if len(liste_entite_base_concerne_dans_CUSTOM)>2:
                        nouveau_CODE_REF = CODE_REF_echelle_a_essayer
                        break
                    if len(liste_entite_base_concerne_dans_CUSTOM)<3:
                        nouveau_CODE_REF = liste_entite_base_concerne_dans_CUSTOM
                        if echelle_a_essayer==[x for x in liste_echelle_REF_total if x!=echelle_actuelle][-1]:
                            nouveau_CODE_REF = ligne_df_BDD['CODE_REF']
                            echelle_a_essayer = ligne_df_BDD['echelle_princ_action']               
            ligne_df_BDD['echelle_princ_action'] = echelle_a_essayer
            ligne_df_BDD['CODE_REF'] = nouveau_CODE_REF
            return ligne_df_BDD    

    def separation_entite_normal_ou_ortho_echelle_CUSTOM(df_BDD,dict_donnees,liste_echelle_boite_normal,dict_relation_shp_liste,echelle_CUSTOM,CODE_CUSTOM):
        #Il faut faire en fonction du type decol de l'echelle finale de chaque ligne
        dict_type_col = dict_donnees['BDD_DORA'].dict_type_col
        def tri_echelle_CUSTOM(ligne_df_BDD):
            echelle_actuelle = ligne_df_BDD['echelle_princ_action']

            for echelle_a_essayer in liste_echelle_boite_normal:
                liste_CODE_REF_CUSTOM = dict_relation_shp_liste['dict_liste_' + echelle_a_essayer + '_par_CUSTOM'][CODE_CUSTOM]
                if dict_type_col["CODE_"+echelle_actuelle]=="list":
                    list_CODE_REF = ligne_df_BDD['CODE_REF']
                if dict_type_col["CODE_"+echelle_actuelle]=="str":
                    list_CODE_REF = [ligne_df_BDD['CODE_REF']]
                if echelle_actuelle==echelle_a_essayer:
                    list_entite_echelle_a_essayer_pour_contenir_action = list_CODE_REF
                if echelle_actuelle!=echelle_a_essayer:
                    if 'dict_liste_' + echelle_actuelle + '_par_' + echelle_a_essayer not in dict_relation_shp_liste:
                        #On inverse un dict existant
                        dict_relation_shp_liste['dict_liste_' + echelle_actuelle + '_par_' + echelle_a_essayer] = {value: [key] for key in dict_relation_shp_liste['dict_liste_' + echelle_a_essayer + '_par_' + echelle_actuelle] for value in dict_relation_shp_liste['dict_liste_' + echelle_a_essayer + '_par_' + echelle_actuelle][key]}
                    list_entite_echelle_a_essayer_pour_contenir_action = [k for k,v in dict_relation_shp_liste['dict_liste_' + echelle_actuelle + '_par_' + echelle_a_essayer].items() if any(x in list_CODE_REF for x in v)]
                if echelle_a_essayer==liste_echelle_boite_normal[-1]:
                    if len(list_entite_echelle_a_essayer_pour_contenir_action)>2:
                        if any(x in list_CODE_REF for x in dict_relation_shp_liste['dict_liste_' + echelle_actuelle + '_par_CUSTOM'][CODE_CUSTOM]):
                            nouveau_CODE_REF = CODE_CUSTOM
                            nouvelle_echelle_CUSTOM = echelle_CUSTOM
                        if not any(x in list_CODE_REF for x in dict_relation_shp_liste['dict_liste_' + echelle_actuelle + '_par_CUSTOM'][CODE_CUSTOM]):
                            nouveau_CODE_REF = "a_supprimer"
                            nouvelle_echelle_CUSTOM = "a_supprimer"                         
                if len(list_entite_echelle_a_essayer_pour_contenir_action)<3:
                    nouveau_CODE_REF = list_entite_echelle_a_essayer_pour_contenir_action
                    nouvelle_echelle_CUSTOM = echelle_a_essayer
                    break
            ligne_df_BDD['echelle_princ_action'] = nouvelle_echelle_CUSTOM
            ligne_df_BDD['CODE_REF'] = nouveau_CODE_REF
            return ligne_df_BDD            

        df_BDD = df_BDD.apply(lambda x:tri_echelle_CUSTOM(x),axis=1)
        return df_BDD

    ##########################################################################################
    #suppression des actions
    ##########################################################################################
    def suppression_CODE_REF_principale_hors_BDD(df,echelle_df,echelle_base_REF,dict_dict_info_REF,dict_type_col):
        if dict_type_col['CODE_'+echelle_base_REF]=='str':
            df = df.loc[((df['CODE_'+echelle_base_REF].isin(dict_dict_info_REF['df_info_'+echelle_base_REF]['CODE_'+echelle_base_REF].to_list())&(df['echelle_princ_action']==echelle_base_REF))|(df['echelle_princ_action']!=echelle_base_REF))]
        if dict_type_col['CODE_'+echelle_base_REF]=='list':
            df_info_REF_BASE = dict_dict_info_REF['df_info_'+echelle_base_REF]
            liste_CODE_REF_BASE_BDD = df_info_REF_BASE['CODE_'+echelle_base_REF].to_list()            
            df['CODE_'+echelle_base_REF] = df['CODE_'+echelle_base_REF].apply(lambda x: [CODE_REF_BASE for CODE_REF_BASE in x if CODE_REF_BASE in liste_CODE_REF_BASE_BDD])
            df = df.loc[((df['CODE_'+echelle_base_REF].astype(bool))&(df['echelle_princ_action']==echelle_base_REF))|((df['echelle_princ_action']!=echelle_base_REF))]
        return df
    
    def suppression_actions_sans_avancement(df):
        df = df.loc[df['Avancement']!='nan']
        return df
    
    def suppression_actions_conti_sans_ROE(df,projet):
        if projet.type_rendu == "tableau" and projet.type_donnees == "action" and projet.thematique=="MIA":
            df = pd.merge(df,dict_config_actions_MIA_DORA['df_DORA_actions_MIA_conv_Osmose'][["NOM_TYPE_ACTION_DORA","CODE_TYPE_ACTION_OSMOSE"]],on="NOM_TYPE_ACTION_DORA")
            df = DfTableauxActionsMIA.menage_si_absence_ROE(df)
            df = df[[x for x in list(df) if x!="CODE_TYPE_ACTION_OSMOSE"]]
        return df
    
    def suppression_actions_sans_echelle_REF(df):
        df = df.loc[~df['echelle_princ_action'].isnull()]
        return df

    ##########################################################################################
    #Continuité
    ##########################################################################################  
    def remplissage_CODE_ROE(df,echelle_df,dict_relation_shp_liste):
        df_tempo = df.loc[df['CODE_ROE'].apply(lambda x:len(x)==1)]
        df_CODE_ROE_a_completer = df_tempo.loc[df_tempo['CODE_ROE'].apply(lambda x:x[0]=="liste")]
        df_hors_CODE_ROE_a_completer = df.drop(list(df_CODE_ROE_a_completer.index))
        df_CODE_ROE_a_completer['CODE_ROE'] = df_CODE_ROE_a_completer.apply(lambda x:dict_relation_shp_liste['dict_liste_ROE_par_'+x["echelle_princ_action"]][x['CODE_'+x["echelle_princ_action"]]], axis=1)
        df = pd.concat(df_CODE_ROE_a_completer,df_hors_CODE_ROE_a_completer)
        return df

    def menage_si_absence_ROE(df):
        df_tempo_conti = df.loc[df["CODE_TYPE_ACTION_OSMOSE"].str.startswith('MIA03')]
        df_tempo_conti = df_tempo_conti.loc[df_tempo_conti["CODE_ROE"].str.startswith('ROE')]
        df = df.loc[~df["CODE_TYPE_ACTION_OSMOSE"].str.startswith('MIA03')]
        df = pd.concat([df,df_tempo_conti])
        return df

    ##########################################################################################
    #Tableau MAJ Osmose
    ##########################################################################################
    def changement_nom_col_tableaux_MAJ_osmose(df_tableau):
        dict_renommage_conv_maj_Osmose_basique = config_DORA.import_tableau_dict_renommage_conv_maj_Osmose_basique()
        df_tableau = df_tableau.rename(dict_renommage_conv_maj_Osmose_basique,axis=1)
        return df_tableau

    def modification_col_CODE_TYPE_ACTION_OSMOSE(df_tableau):
        df_tableau["CODE_TYPE_ACTION_OSMOSE_tempo"] = df_tableau["CODE_TYPE_ACTION_OSMOSE"].apply(lambda x:x.split("-")[-1])
        return df_tableau

    def modification_col_CODE_ME(df_tableau):
        df_tableau["CODE_ME"] = df_tableau["CODE_ME"].apply(lambda x:x.split(";"))
        df_tableau["CODE_ME"] = df_tableau["CODE_ME"].apply(lambda x: [s.strip() for s in x])
        df_tableau["CODE_ME"] = df_tableau["CODE_ME"].apply(lambda x: [ME for ME in x if len(ME)>1])
        df_tableau["CODE_ME"] = df_tableau["CODE_ME"].apply(lambda x: ["FR" + ME for ME in x if len(ME)>1])
        return df_tableau
    
    def ajout_CODE_BVG(df_tableau,dict_relation_shp_liste):
        dict_CODE_BVG_CODE_ME = dict_relation_shp_liste['dict_liste_ME_par_BVG']
        dict_CODE_ME_CODE_BVG = {}
        for k,v in dict_CODE_BVG_CODE_ME.items():
            for x in v:
                dict_CODE_ME_CODE_BVG.setdefault(x, []).append(k)
        
        df_tableau["CODE_ME"] = df_tableau["CODE_ME"].apply(lambda x:";".join(x))
        sub_df_1 = df_tableau.loc[~df_tableau["CODE_ME"].str.contains("FG")]
        sub_df_2 = df_tableau.loc[df_tableau["CODE_ME"].str.contains("FG")]
        sub_df_1["CODE_ME"] = sub_df_1["CODE_ME"].apply(lambda x:x.split(";"))
        sub_df_2["CODE_ME"] = sub_df_2["CODE_ME"].apply(lambda x:x.split(";"))
        
        sub_df_1["CODE_BVG"] = sub_df_1["CODE_ME"].apply(lambda list_ME:[dict_CODE_ME_CODE_BVG[ME] if ME in dict_CODE_ME_CODE_BVG else [] for ME in list_ME])
        sub_df_1["CODE_BVG"] = sub_df_1["CODE_BVG"].apply(lambda x:[list_ME for list_BVG in x for list_ME in list_BVG]) 
        sub_df_1["CODE_BVG"] = sub_df_1["CODE_BVG"].apply(lambda x:list(set(x)))
        
        sub_df_2["CODE_BVG"] = sub_df_2["CODE_BVG"].apply(lambda x:x.split(";"))
        df_tableau = pd.concat([sub_df_1,sub_df_2])
        return df_tableau

    def separation_actions_hors_PDM(self):
        df = self.df
        df = df[[x for x in list(df) if x!="CODE_PDM"]]
        df_PDM_AG = dataframe.import_df_PDM_AG() 
        df_PDM_AG['liste_CODE_TEMPO'] = df_PDM_AG.apply(lambda df_PDM_AG:[x + "$" + df_PDM_AG['CODE_TYPE_ACTION_OSMOSE'] for x in df_PDM_AG['CODE_BVG']],axis=1)
        df_PDM_AG = df_PDM_AG.explode('liste_CODE_TEMPO')
        df_PDM_AG = df_PDM_AG[['CODE_PDM','liste_CODE_TEMPO']]
        df['liste_CODE_TEMPO'] = df.apply(lambda df:[x + "$" + df['CODE_TYPE_ACTION_OSMOSE_tempo'] for x in df['CODE_BVG']],axis=1)
        df = df.explode('liste_CODE_TEMPO')
        df = pd.merge(df,df_PDM_AG,on="liste_CODE_TEMPO",how='left')
        df['CODE_PDM'] = df['CODE_PDM'].fillna('nan')
        #df = df.drop_duplicates(subset = ['CODE_IMPORT'], keep = 'first')
        df = df[[x for x in list(df) if x!="liste_CODE_TEMPO"]]

        df_tempo = df[['CODE_IMPORT','CODE_PDM']].groupby('CODE_IMPORT').agg({'CODE_PDM':lambda x: list(x)})
        df_tempo["CODE_PDM"] = df_tempo["CODE_PDM"].apply(lambda x:list(set(x)))
        df = df[[x for x in list(df) if x!="CODE_PDM"]]
        df = pd.merge(df,df_tempo,on="CODE_IMPORT",how='left')
        df_actions_a_recreer = df.loc[df['CODE_PDM'].str.len()>1]
        df_actions_a_recreer = df_actions_a_recreer.drop_duplicates(subset = ['CODE_IMPORT'], keep = 'first')
        df_actions_a_recreer['CODE_PDM'] = df_actions_a_recreer['CODE_PDM'].apply(lambda x:[])
        
        df = df.loc[df['CODE_PDM'].str.len()<2]
        df = df.drop_duplicates(subset = ['CODE_IMPORT'], keep = 'first')
        self.df = df
        #AJout des actions avec plusieurs CODE PDM à abandonnder
        df_actions_a_abandonner = copy.deepcopy(df_actions_a_recreer)
        df_actions_a_abandonner['Avancement'] = "6-Abandonnée"
        df_actions_a_abandonner['Motif abandon (si niveau avancement = abandonné)'] = "3-Action renseignée par erreur"
        df_actions_a_abandonner = df_actions_a_abandonner.drop_duplicates(subset = ['CODE_IMPORT'], keep = 'first')
        #df = pd.concat([df,df_actions_a_abandonner])
        df = df_actions_a_abandonner
        self.df = df
        self.df_actions_a_recreer = df_actions_a_recreer
        return self
    
    def recuperation_info_ME_BVG_CODE_PDM_pour_actions_abandonnees(self,dict_relation_shp_liste,dict_dict_info_REF):
        dict_ME_par_BVG = dict_relation_shp_liste['dict_liste_ME_par_BVG']
        df_PDM_AG = dataframe.import_df_PDM_AG()
        self_tempo_abandonnee = self.df.loc[self.df['Avancement']=="6-Abandonnée"]  
        self_tempo_non_abandonnee = self.df.loc[self.df['Avancement']!="6-Abandonnée"]      
        self_tempo_abandonnee["CODE_PDM"] = pd.merge(self_tempo_abandonnee[['CODE_IMPORT']],self.df_original,on="CODE_IMPORT")["CODE_PDM"].to_list()
        df_avec_BVG_tempo_du_PDM = pd.merge(self_tempo_abandonnee[['CODE_PDM']],df_PDM_AG,on="CODE_PDM")
        df_avec_BVG_tempo_du_PDM = df_avec_BVG_tempo_du_PDM.drop_duplicates(subset = ['CODE_PDM'], keep = 'first')
        self_tempo_abandonnee = self_tempo_abandonnee[[x for x in list(self_tempo_abandonnee) if x!="CODE_BVG"]]
        self_tempo_abandonnee = pd.merge(self_tempo_abandonnee,df_avec_BVG_tempo_du_PDM[['CODE_PDM','CODE_BVG']],on="CODE_PDM")
        self_tempo_abandonnee["CODE_BVG"] = self_tempo_abandonnee["CODE_BVG"].apply(lambda x:x[0])
        self_tempo_abandonnee["CODE_ME"] = self_tempo_abandonnee["CODE_BVG"].apply(lambda x:dict_ME_par_BVG[x][0])

        dict_relation_CODE_ME_DEP_pilote = dict(zip(dict_dict_info_REF['df_info_ME']['CODE_ME'].to_list(),dict_dict_info_REF['df_info_ME']['DEP_pilote'].to_list()))
        self_tempo_abandonnee['dep_pilote'] = self_tempo_abandonnee['CODE_ME'].map(dict_relation_CODE_ME_DEP_pilote)
        
        self_tempo_abandonnee["CODE_BVG"] = self_tempo_abandonnee["CODE_BVG"].apply(lambda x:x.split(";"))
        self_tempo_abandonnee["CODE_ME"] = self_tempo_abandonnee["CODE_ME"].apply(lambda x:x.split(";"))
        self_tempo_abandonnee["CODE_PDM"] = self_tempo_abandonnee["CODE_PDM"].apply(lambda x:x.split(";"))        
        
        self.df = pd.concat([self_tempo_abandonnee,self_tempo_non_abandonnee])
        return self
    

    def ajout_attributs_non_faits(self):
        df_attributs_Osmose = config_DORA.import_tableau_attributs_Osmose()
        df_attributs_Osmose["Type d'action"] = [x[:7] for x in df_attributs_Osmose["Type d'action"].to_list()]
        df_attributs_Osmose = df_attributs_Osmose.rename({"Type d'action":"CODE_TYPE_ACTION_OSMOSE_tempo"},axis=1)
        df_attributs_Osmose = df_attributs_Osmose.loc[df_attributs_Osmose["Obligatoire à partir"]=="Engagée"]
        df_attributs_Osmose = df_attributs_Osmose[['CODE_TYPE_ACTION_OSMOSE_tempo',"Attribut"]]
        
        list_df = [self.df]
        list_df_attributs = [self.df_attributs]
        
        if hasattr(self,"df_actions_a_recreer"):
            list_df = [self.df,self.df_actions_a_recreer]
            list_df_attributs.extend([self.df_attributs_df_actions_a_creer])
            
        for df_actions in list_df:
            df_attributs_Osmose = pd.merge(df_actions,df_attributs_Osmose,on="CODE_TYPE_ACTION_OSMOSE_tempo")
            df_attributs_Osmose.loc[df_attributs_Osmose['Attribut']=="Action financée par l'Agence de l'eau",'Valeur (s)'] = "Non"
        return self
    
    def gestion_df_attributs(self):
        if hasattr(self,"df_actions_a_recreer"):
            liste_code_action_df_a_creer = self.df_actions_a_recreer["CODE_IMPORT"].to_list()
            self.df_attributs_df_actions_a_creer = self.df_attributs.loc[self.df_attributs["CODE OSMOSE Action"].isin(liste_code_action_df_a_creer)]        
        liste_code_action = self.df["CODE_IMPORT"].to_list()
        self.df_attributs = self.df_attributs.loc[self.df_attributs["CODE OSMOSE Action"].isin(liste_code_action)]
        return self
    
    def transfo_col_en_str(self):
        list_df = [self.df]
        if hasattr(self,"df_actions_a_recreer"):
            list_df = [self.df,self.df_actions_a_recreer]
        for df_tableau in list_df:
            df_tableau["CODE_PDM"] = df_tableau["CODE_PDM"].apply(lambda x:";".join(x))
            df_tableau.loc[df_tableau["CODE_PDM"]=='nan',"CODE_PDM"] = None
            df_tableau["CODE_BVG"] = df_tableau["CODE_BVG"].apply(lambda x:";".join(x))
            df_tableau["CODE_ME"] = df_tableau["CODE_ME"].apply(lambda x:[ME[2:] for ME in x])
            df_tableau["CODE_ME"] = df_tableau["CODE_ME"].apply(lambda x:";".join(x))
        return self

    def changement_nom_col_tableaux_MAJ_osmose_vers_osmose(self):
        dict_renommage_conv_maj_Osmose_basique = config_DORA.import_tableau_dict_renommage_conv_maj_Osmose_basique()
        dict_renommage_conv_basique_maj_Osmose = {v:k for k,v in dict_renommage_conv_maj_Osmose_basique.items()}
        self.df = self.df.rename(dict_renommage_conv_basique_maj_Osmose,axis=1)
        if hasattr(self,"df_actions_a_recreer"):
            self.df_actions_a_recreer = self.df_actions_a_recreer.rename(dict_renommage_conv_basique_maj_Osmose,axis=1)
        return self
    
    def mise_ordre_col_maj_osmose(self):
        df_maj_vierge = pd.read_excel("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/config/Osmose/TABLEAU_MAJ_OSMOSE_VIERGE.xlsx")
        self.df = self.df[list(df_maj_vierge)]
        if hasattr(self,"df_actions_a_recreer"):
            df_vierge = config_DORA.import_df_vierge_Osmose_onglet_action()
            self.df_actions_a_recreer = self.df_actions_a_recreer[list(df_vierge)]
        return self
    ##########################################################################################
    #Inutiles
    ########################################################################################## 
    def col_invariantes(df):
        dict_invariant = config_DORA.import_dict_config_actions_MIA_DORA()["df_DORA_actions_MIA_conv_Osmose"]
        for nom_col,contenul in dict_invariant.items():
            df[nom_col] = contenul
        return df    

    def conversion_contenu_col_list(df,echelle_df,dict_type_col):
        for col in list(df):
            if echelle_df == "MO" or echelle_df == "DEP":
                if col in dict_type_col:
                    if dict_type_col[col]=='list':
                        df[col] = df[col].apply(lambda list_col:';'.join(x for x in list_col))
                        dict_type_col[col]='str'
        return df    

    def conversion_CODE_ME_forme_FR(df):
        df['CODE_ME'] = df['CODE_ME'].apply(lambda x:[CODE_ME[2:] for CODE_ME in x])
        return df

    def renommage_col(df):
        df_vierge_Osmose_onglet_action = config_DORA.import_df_vierge_Osmose_onglet_action()
        dict_renommage_df_Osmose_final = config_DORA.import_dict_renommage_df_Osmose_final()

        #dict_renommage_conv_DORA_Osmose = config.import_dict_config_actions_MIA_DORA()["df_DORA_actions_MIA_conv_Osmose"]
        df = df.rename(dict_renommage_df_Osmose_final,axis=1)
        df.to_csv("/mnt/g/travail/carto/couches de bases/test/allo.csv")
        list_col_traitees = [x for x in list(df_vierge_Osmose_onglet_action) if x in list(df)]
        df = df[list(list_col_traitees)]
        return df
    
    def ajout_col_invariantes(df):
        df_vierge_Osmose_onglet_action = config_DORA.import_df_vierge_Osmose_onglet_action()
        list_col_non_faites = [x for x in list(df_vierge_Osmose_onglet_action) if x not in list(df)]
        for col_non_traitee in list_col_non_faites:
            df[col_non_traitee] = None
        return df


    def ordre_colonne_Osmose_LOL(df):
        df_vierge_Osmose_onglet_action = config_DORA.import_df_vierge_Osmose_onglet_action()
        df = df[list(df_vierge_Osmose_onglet_action)]
        return df


    def remplacer_mention_VIDE(df):
        df = df.replace(np.nan, None)
        df = df.replace("VIDE_DORA", None)
        df = df.replace("Ab SANDRE", None)
        df = df.replace('nan', None)
        return df    
    


##########################################################################################
#onglets presque nulles
##########################################################################################
    def renommage_onglet_blocage(df):
        df_onglet_blocage_vierge = config_DORA.import_onglet_vierge_blocage_Osmose()
        df = df_onglet_blocage_vierge
        return df

    def renommage_onglet_etapes(df):
        df_onglet_etape_vierge = config_DORA.import_onglet_vierge_etapes_Osmose()
        dict_renommage_onglet_etape = {"CODE_IMPORT":"CODE OSMOSE Action","Avancement_spe_conti":"Nom de l'étape (ou sous-étape)*"}
        df = df.rename(dict_renommage_onglet_etape,axis=1)
        list_col_manquante = [x for x in list(df_onglet_etape_vierge) if x not in list(df)]
        for col_manquante in list_col_manquante:
            df[col_manquante] = None
        df = df[list(df_onglet_etape_vierge)]
        return df
    
    def renommage_onglet_financeurs(df):
        df_onglet_blocage_vierge = config_DORA.import_onglet_vierge_financeurs_Osmose()
        df = df_onglet_blocage_vierge
        return df
    
    def renommage_onglet_attributs(df):
        dict_renommage= {"CODE_IMPORT":"CODE OSMOSE Action","Attribut":"Code de l'attribut","Valeur (s)":"Valeur (s)"}
        df = df.rename(dict_renommage,axis=1)
        df = df[list(dict_renommage.values())]
        return df

##########################################################################################
#Verification du tableau
##########################################################################################
    def traitement_specifique_verif_NOM_MO(df_tableau,dict_dict_info_REF,echelle_df,numero_dep):
        if echelle_df=="DEP":
            liste_NOM_MO = df_tableau['NOM_MO'].to_list()
            liste_NOM_MO = list(set(liste_NOM_MO))
            liste_NOM_MO_presents_df_info_GEMAPI = dict_dict_info_REF['df_info_MO']['NOM_MO'].to_list()

            #Ici, on envoie les NOM_MO inconnus dans le fichier df_info_MO
            '''liste_NOM_MO_absents_BDD = [x for x in liste_NOM_MO if x not in liste_NOM_MO_presents_df_info_GEMAPI]
            df_a_ajouter_MO_gemapi = pd.DataFrame(liste_NOM_MO_absents_BDD,columns=['NOM_init'])
            df_a_ajouter_MO_gemapi['CODE_DEP'] = numero_dep
            df_a_ajouter_MO_gemapi['NOM_DEP'] = df_a_ajouter_MO_gemapi['CODE_DEP'].map(dict_dict_info_REF['df_info_DEP'].dict_NOM_CODE)
            df_a_ajouter_MO_gemapi['shp'] = 0
            
            liste_CODE_MO_deja_attribues = dict_dict_info_REF['df_info_MO']['CODE_MO'].to_list()
            liste_numero_CODE_MO_deja_enregistre = [int(x.split("_")[2]) for x in liste_CODE_MO_deja_attribues]
            CODE_MAX_actuel = max(liste_numero_CODE_MO_deja_enregistre)
            df_a_ajouter_MO_gemapi['tempo'] =range(CODE_MAX_actuel,CODE_MAX_actuel+len(df_a_ajouter_MO_gemapi))
            df_a_ajouter_MO_gemapi['CODE_MO'] = "MO_gemapi_" + df_a_ajouter_MO_gemapi['tempo'].astype(str)
            df_a_ajouter_MO_gemapi = df_a_ajouter_MO_gemapi[[x for x in list(df_a_ajouter_MO_gemapi) if x!="tempo"]]
            
            df_info_MO_gemapi = pd.concat([dict_dict_info_REF['df_info_MO'],df_a_ajouter_MO_gemapi])

            dict_dict_info_REF["df_info_MO"] = df_info_MO_gemapi'''

            #Au depart, je comptais mettre à jour les infos directement dans le fichier info GEMAPI. Mais quand on voit les DDT qui prennent même pas la
            #peine de chercher un nom dans une pauvre liste déroulante, je me dis que la confiance à leur accorder est d'environ zéro
            #dict_dict_info_REF = DictDfInfoShp.maj_fichier_DictDfInfoShp(dict_dict_info_REF)
            #On doit réimporter pour actualiser les attributs !
            #dict_dict_info_REF = DictDfInfoShp.import_info_MO(dict_dict_info_REF)
            
            #Ici, on renvoie le tableau vers
            df_erreur_potentiel_col_CODE_REF = df_tableau[['NOM_MO']]
            df_erreur_potentiel_col_CODE_REF.loc[df_erreur_potentiel_col_CODE_REF['NOM_MO']=='nan',"Erreur NOM_MO"] = "Nom absent de la BDD"
            
        return df_erreur_potentiel_col_CODE_REF

    def verification_colonne_NOM_REF_existence_BDD(df_tableau_erreur,df,dict_dict_info_REF,echelle_df,numero_dep,dict_type_col):
        dict_chgmt_type_col_df_tableau_action_MIA_REF = dict_type_col        
        list_REF_df_info = [x.split("_")[-1] for x in list(dict_dict_info_REF)]
        list_col_NOM = dataframe.extraction_liste_col_NOM(df,list_REF_df_info)
        for nom_col in list_col_NOM:
            type_REF = nom_col.split("_")[1]
            dict_NOM_NOM_REF = dict_dict_info_REF['df_info_'+type_REF].dict_NOM_CODE
            #Pas de colonne NOM + REF sous forme de liste, trop le bordel
            if nom_col in dict_type_col:
                if dict_type_col[nom_col]=="str":
                    if type_REF=="MO" and echelle_df=="DEP":
                        #Il faut un tableau avec pour index le numero et pour contenu l'erreur (ex : Cette MO n'apparait pas dans la BDD MO sans carto ni la normale)
                        df_erreur_potentiel_col_CODE_REF = DfTableauxActionsMIA.traitement_specifique_verif_NOM_MO(df,dict_dict_info_REF,echelle_df,numero_dep)
                    if type_REF!="MO" or (type_REF=="MO" and echelle_df!="DEP"):
                        df_erreur_potentiel_col_CODE_REF = df[(~df['NOM_'+type_REF].isin(list(dict_NOM_NOM_REF))&(df['NOM_'+type_REF]!='nan'))]
                        df_erreur_potentiel_col_CODE_REF["Erreur NOM_" + type_REF] = "Nom absent de la BDD"
                    df_tableau_erreur = pd.merge(df_tableau_erreur,df_erreur_potentiel_col_CODE_REF[['Erreur NOM_'+type_REF]],how='left',left_index=True, right_index=True)
            df_tableau_erreur = df_tableau_erreur.replace(float('nan'), 'nan', regex=True)
        return df_tableau_erreur

    def verification_colonne_CODE_REF(df_tableau_erreur,DfActionsMIA,dict_dict_info_REF):
        list_REF_df_info = [x.split("_")[-1] for x in list(dict_dict_info_REF)]
        list_col_CODE = dataframe.extraction_liste_col_CODE(DfActionsMIA.df,list_REF_df_info)
        #On ne vérifie pas la colonne SME ou Me selon l'echelle base REF
        if DfActionsMIA.echelle_base_REF == "SME":
            list_col_CODE = [x for x in list_col_CODE if x!="CODE_ME"]
        if DfActionsMIA.echelle_base_REF == "ME":
            list_col_CODE = [x for x in list_col_CODE if x!="CODE_SME"]            
        for CODE_REF in list_col_CODE:
            if CODE_REF in DfActionsMIA.dict_type_col:
                if DfActionsMIA.dict_type_col[CODE_REF] == 'list':
                    if any(x==x for x in DfActionsMIA.df[CODE_REF].to_list()):
                        list_tempo=[]
                        type_REF = CODE_REF.split("_")[1]
                        dict_CODE_NOM_REF = dict_dict_info_REF['df_info_'+type_REF].dict_CODE_NOM
                        df_erreur_potentiel_col_CODE_REF = DfActionsMIA.df[~DfActionsMIA.df['CODE_'+type_REF].isin(list(dict_CODE_NOM_REF))]
                        list_liste_CODE_REF = df_erreur_potentiel_col_CODE_REF['CODE_'+type_REF].to_list()
                        for liste_CODE_REF in list_liste_CODE_REF:
                            liste_CODE_REF = [x for x in liste_CODE_REF if x!='nan']
                            liste_CODE_REF = [x for x in liste_CODE_REF if x not in list(dict_CODE_NOM_REF)]
                            erreur_CODE_REF = (" et ").join(liste_CODE_REF)
                            if len(erreur_CODE_REF)>0:
                                erreur_CODE_REF = erreur_CODE_REF + " pas dans la BDD" 
                            else:
                                erreur_CODE_REF = 'nan'
                            list_tempo.append(erreur_CODE_REF)
                        df_erreur_potentiel_col_CODE_REF['Erreur CODE_'+type_REF] = list_tempo
                        df_tableau_erreur = pd.merge(df_tableau_erreur,df_erreur_potentiel_col_CODE_REF[['Erreur CODE_'+type_REF]],how='left',left_index=True, right_index=True)
                    
            else:
                type_REF = CODE_REF.split("_")[1]
                dict_CODE_CODE_REF = dict_dict_info_REF['df_info_'+type_REF].dict_CODE_NOM
                df_erreur_potentiel_col_CODE_REF =DfActionsMIA.df.loc[(~DfActionsMIA.df['CODE_'+type_REF].isin(list(dict_CODE_CODE_REF)))&(DfActionsMIA.df['CODE_'+type_REF]!='nan')]
                df_erreur_potentiel_col_CODE_REF["Erreur CODE_" + type_REF] = "CODE absent de la BDD"
                df_tableau_erreur = pd.merge(df_tableau_erreur,df_erreur_potentiel_col_CODE_REF[["Erreur CODE_" + type_REF]],how='left',left_index=True, right_index=True)
            df_tableau_erreur = df_tableau_erreur.replace(float('nan'), 'nan', regex=True)
            df_tableau_erreur = df_tableau_erreur.replace('', 'nan')

        return df_tableau_erreur   
    
    def verification_colonne_echelle_princ_action(df_tableau_erreur,df):
        df_erreur_potentiel_col_CODE_REF =df.loc[(df['echelle_princ_action']=='nan')]
        df_erreur_potentiel_col_CODE_REF["Erreur echelle_princ_action"] = "Pas de localisation d'action valide, il faut au moins une échelle geographique valide"
        df_tableau_erreur = pd.merge(df_tableau_erreur,df_erreur_potentiel_col_CODE_REF[['Erreur echelle_princ_action']],how='left',left_index=True, right_index=True)
        df_tableau_erreur = df_tableau_erreur.replace(float('nan'), 'nan', regex=True)
        return df_tableau_erreur

    def verification_colonne_avancement(df_tableau_erreur,df):
        list_col_avancement = ['Prévisionnelle','Initiée','Engagée','Terminée','Abandonnée']
        df_tempo = df.loc[~df["Avancement"].isin(list_col_avancement)][['Avancement']]
        df_tempo['Erreur Avancement'] = "Niveau d'avancement inconnu"
        df_tempo = df_tempo[[x for x in list(df_tempo) if x!="Avancement"]]
        df_tableau_erreur = pd.merge(df_tableau_erreur,df_tempo,how='left',left_index=True, right_index=True)
        df_tableau_erreur = df_tableau_erreur.fillna('nan')
        return df_tableau_erreur
    
    def verification_colonnes_annee_avancement(df_tableau_erreur,df_action):
        list_col_annee = ['annee_action_ini','annee_action_eng','annee_action_term','action_aba']
        for col_annee in list_col_annee:
            df_tempo = pd.DataFrame(index=df_action.df.index)
            liste_tempo = []
            list_annee_retenu = df_action.df[col_annee]
            list_annee_original = df_action.df_brut[col_annee]
            for numero,annee_original in enumerate(list_annee_original):
                if annee_original!='nan' and list_annee_retenu[numero]=='nan':
                    liste_tempo.append("Date non retenue")
                if annee_original!='nan' and list_annee_retenu[numero]!='nan':
                    liste_tempo.append('nan')
                if annee_original=='nan' and list_annee_retenu[numero]=='nan':
                    liste_tempo.append('nan')
            df_tempo["Erreur "+col_annee]  =  liste_tempo
            df_tableau_erreur = pd.merge(df_tableau_erreur,df_tempo,how='left',left_index=True, right_index=True)
        df_tableau_erreur = df_tableau_erreur.fillna('nan')

        return df_tableau_erreur

class DfBDDOsmose(pd.DataFrame):
    @property
    def _constructor(self):
        return DfBDDOsmose
    
    
    
