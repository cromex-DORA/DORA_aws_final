# -*- coding: utf-8 -*-
import pandas as pd
import os.path
import glob
from itertools import compress
import re
from datetime import date
today = date.today()
from app.DORApy.classes.modules import config_DORA
from dotenv import load_dotenv
from app.DORApy.classes.modules import connect_path
import warnings
warnings.simplefilter(action='ignore', category=UserWarning)



#####################################################################
#Outils généraux
#####################################################################
def recuperer_liste_colonne_df_qui_commence_par_nom(df):
    filtre_liste_colonne = [a.startswith("NOM") for a in [x.upper() for x in list(df)]]
    liste_colonnes_potentielles_nom =  list(compress(list(df), filtre_liste_colonne))
    return liste_colonnes_potentielles_nom

def replacer_colonne_premiere_position(df,liste):
    df = df[ liste + [ col for col in df.columns if col not in liste ] ]
    return df

def mapping_sur_liste(df,colonne_a_mapper,dict_mapping,colonne_resultat):
    liste_final_nested = []
    liste_final = []
    list_tempo_liste_colonne_a_mapper = df[colonne_a_mapper].to_list()
    if isinstance(list(dict_mapping.values())[0],list):
        value_dict_map_list = True
    if not isinstance(list(dict_mapping.values())[0],list):  
        value_dict_map_list = False
    for liste in list_tempo_liste_colonne_a_mapper:
        liste_tempo2 = []
        if isinstance(liste,list):
            for entite in liste:
                try:
                    liste_tempo2.append(dict_mapping[entite])
                except:
                    if value_dict_map_list == True:
                        liste_tempo2.append([])
                    if value_dict_map_list == False:
                        pass                      
            liste_final_nested.append(liste_tempo2)
        if not isinstance(liste,list):
            liste_final_nested.append([])
    if isinstance(list(dict_mapping.values())[0],list):
        for liste in liste_final_nested:
           liste = list(set([val for sublist in liste for val in sublist]))
           liste_final.append(liste)
        df[colonne_resultat] = liste_final
    if not isinstance(list(dict_mapping.values())[0],list):
        liste_final_nested = [list(set(x)) if isinstance(x,list) else 'nan' for x in liste_final_nested]
        df[colonne_resultat] = liste_final_nested
    return df

def strip_et_tease_col(df_tableau):
    for col in list(df_tableau):
        df_tableau = df_tableau.rename(columns=lambda x: x.strip())
    return df_tableau

def strip_et_tease_contenu_col(df_tableau):
    for col in list(df_tableau):
        try:
            df_tableau[col] = df_tableau[col].str.strip()
            df_tableau[col] = df_tableau[col].replace('/n',' ', regex=True)
        except:
            pass
    return df_tableau

def creation_doublon_df(self):
    self.df_original = self.df
    return self


def reduction_nom_colonne_via_fichier_csv(df,type_df):
    dict_reduction_nom_col_bloc_et_boite = config_DORA.creation_dict_reduction_nom_col_bloc_et_boite()
    if type_df=="df_contour":
        df_reduction_nom_colonne_BDD = dict_reduction_nom_col_bloc_et_boite['df_contour']
    if type_df=="bloc_texte_simple":
        df_reduction_nom_colonne_BDD = dict_reduction_nom_col_bloc_et_boite['df_texte_simple']
    if type_df=="bloc_icone":
        df_reduction_nom_colonne_BDD = dict_reduction_nom_col_bloc_et_boite['df_icone']
    if type_df=="bloc_lignes_multiples":
        df_reduction_nom_colonne_BDD = dict_reduction_nom_col_bloc_et_boite['df_lm']       
    df_reduction_nom_colonne_BDD = df_reduction_nom_colonne_BDD.loc[~df_reduction_nom_colonne_BDD['nom_colonne_long'].isnull()]
    dict_reduction_nom_colonne = dict(zip(df_reduction_nom_colonne_BDD["nom_colonne_long"].to_list(),df_reduction_nom_colonne_BDD["nom_colonne_court"].to_list()))
    df = df.rename(dict_reduction_nom_colonne,axis=1)
    return df

def extraction_liste_col_CODE(df,list_REF_df_info):
    list_col_CODE = [x for x in list(df) if x.startswith('CODE')]
    list_col_CODE = [x for x in list_col_CODE if x.split('CODE_')[-1] in list_REF_df_info]
    return list_col_CODE

def extraction_liste_col_NOM(df,list_REF_df_info):
    list_col_NOM = [x for x in list(df) if x.startswith('NOM')]
    list_col_NOM = [x for x in list_col_NOM if x.split('NOM_')[-1] in list_REF_df_info]
    return list_col_NOM

def extraire_string(x,sequence_recherchee):
    if sequence_recherchee!=sequence_recherchee:
        try:
            return re.search('[0-9]+', x).group(0)
        except:
            return pd.NA          
    if sequence_recherchee==sequence_recherchee:
        sequence_recherchee = int(sequence_recherchee)
        var1 = sequence_recherchee
        try:
            list_sequence_chiffre_retourne =re.findall(r'[0-9]{' +  str(sequence_recherchee) + '}', x)
            int_final = int(list_sequence_chiffre_retourne[0])
            return int_final
        except:
            return pd.NA

#####################################################################
#Tableaux PPG
#####################################################################
def recuperation_liste_tableaux_info_PPG_MIA():
    #Obliger de passer par de l'extraction de nom de colonne d'un tableau vierge, car on ne pas écrire manuellement les noms des colonnes depuis un csv é cause des caractéres : ' ?
    try:
        liste_xlsm_info_PPG = [pd.read_excel(f,sheet_name="info_PPG") for f in glob.glob("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MIA/MO/*.xlsm")]
        liste_nom_fichier_actions = [os.path.basename(f) for f in glob.glob("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MIA/MO/*.xlsm")]
        liste_nom_fichier_actions = [x.split("_")[2] for x in liste_nom_fichier_actions]
    except:
        print("Je n'ai pas réussi é trouver d'onglet info_PPG dans les fichiers tableaux actions" )
        liste_nom_fichier_actions = []
        liste_xlsm_info_PPG = []
    return liste_nom_fichier_actions,liste_xlsm_info_PPG

def rassemblement_df_info_PPG(liste_nom_fichier_actions,liste_xlsm_info_PPG):
    liste_df_info_PPG_df_actions = []
    for numero,df_tableau_info_PPG in enumerate(liste_xlsm_info_PPG):
        liste_df_info_PPG_df_actions.append(df_tableau_info_PPG)
    if len(liste_df_info_PPG_df_actions)>0:
        df_info_PPG_issu_df_actions = pd.concat(liste_df_info_PPG_df_actions)
    if len(liste_df_info_PPG_df_actions)==0:
        df_info_PPG_issu_df_actions = pd.DataFrame([])
    return df_info_PPG_issu_df_actions

def traitement_specifique_df_info_PPG_issu_df_actions(df_info_PPG_issu_df_actions):
    df_vierge_info_PPG = pd.read_excel("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MIA/MO/Tableau_suivi_MIA_MO_vierge.xlsm",sheet_name="info PPG")
    dict_renommage_colonne_df_info_PPG_issu_df_actions = {list(df_vierge_info_PPG)[0] : "NOM_MO","Nom_PPG":"NOM_PPG","code SIRET":"CODE_SIRET","Année Début_PPG":"debut_PPG","Année Fin_PPG":"fin_PPG","Année Début_DIG":"debut_DIG","Année_Fin_DIG":"fin_DIG","Compétences MO    L211-7 ITEMs (GEMAPI et Hors GEMAPI)":"competence"}
    if len(df_info_PPG_issu_df_actions)>0:
        df_info_PPG_issu_df_actions = df_info_PPG_issu_df_actions.rename(dict_renommage_colonne_df_info_PPG_issu_df_actions,axis=1)
        df_info_PPG_issu_df_actions = df_info_PPG_issu_df_actions[list(dict_renommage_colonne_df_info_PPG_issu_df_actions.values())]
        df_info_PPG_issu_df_actions['CODE_SIRET'] = df_info_PPG_issu_df_actions['CODE_SIRET'].astype(str)
    return df_info_PPG_issu_df_actions

def recuperer_tableau_OSMOSE():
    dict_df_MAJ = {}
    chemin_fichier_tableau = "/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MAJ Osmose"
    liste_df_actions_originaux = [pd.read_excel(f,sheet_name="Actions") for f in glob.glob(chemin_fichier_tableau + "/*.xlsx")]
    liste_df_attributs_originaux = [pd.read_excel(f,sheet_name="+Attributs") for f in glob.glob(chemin_fichier_tableau + "/*.xlsx")]
    tableau_17_actions = pd.concat(liste_df_actions_originaux)
    tableau_17_attr = pd.concat(liste_df_attributs_originaux)
    return dict_df_MAJ

def recuperer_BDD_Osmose():
    dict_df_MAJ = {}
    chemin_fichier_tableau = "/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/BDD_Osmose"
    liste_df_actions_originaux = [pd.read_excel(f,sheet_name="Actions") for f in glob.glob(chemin_fichier_tableau + "/*.xlsx")]
    liste_df_attributs_originaux = [pd.read_excel(f,sheet_name="+Attributs") for f in glob.glob(chemin_fichier_tableau + "/*.xlsx")]
    if len(liste_df_actions_originaux)>0:
        BDD_Osmose = pd.concat(liste_df_actions_originaux)
        BDD_Osmose_attr = pd.concat(liste_df_attributs_originaux)
        dict_BDD_Osmose_attr = BDD_Osmose_attr.groupby('CODE OSMOSE Action')[["Valeur (s)","Code de l'attribut"]].apply(lambda x: x.set_index("Code de l'attribut").to_dict(orient='index')).to_dict()
        dict_BDD_Osmose_attr = {k:{a:b["Valeur (s)"] for a,b in v.items()} for k,v in dict_BDD_Osmose_attr.items()}
        BDD_Osmose_attr = pd.DataFrame.from_dict(dict_BDD_Osmose_attr, orient='index')
        BDD_Osmose = pd.merge(BDD_Osmose,BDD_Osmose_attr,how="left",left_on="CODE OSMOSE Action",right_index=True)
    if len(liste_df_actions_originaux)==0:
        BDD_Osmose = pd.DataFrame([])
    return BDD_Osmose

def traitement_BDD_OSMOSE_format_DORA(df,dict_dict_info_REF,echelle_df):
    if echelle_df =='global_Osmose':
        df["CODE_TYPE_ACTION_OSMOSE"] = df["CODE_TYPE_ACTION_OSMOSE"].apply(lambda x:x.split("-")[-1])
        df["Avancement"] = df["Avancement"].apply(lambda x:x.split("-")[-1])
        dict_config_col_BDD_DORA_vierge = config_DORA.import_dict_config_col_BDD_DORA_vierge()
        for nom_col in dict_config_col_BDD_DORA_vierge['type_col']:
            if nom_col not in list(df):
                if (dict_config_col_BDD_DORA_vierge[nom_col]=="str" or dict_config_col_BDD_DORA_vierge[nom_col]=="list"):
                    df[nom_col] = "nan"
    return df

#####################################################################
#Tableaux conversion pour moulinette Osmose
#####################################################################
def recuperation_df_conversion_actions_DORA_vers_CODE_Osmose():
    df_conversion_actions_DORA_vers_CODE_Osmose = pd.read_excel("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Tableau actions/MIA/VF5_Tableaux_suivi_PPG.xlsm",sheet_name="AIDE Liste des actions")
    list_col_df_conversion_actions_DORA_vers_CODE_Osmose = list(df_conversion_actions_DORA_vers_CODE_Osmose)
    list_col_df_conversion_actions_DORA_vers_CODE_Osmose = ["type_action_DORA" if col.startswith('Principales interventions travaux') else col for col in list_col_df_conversion_actions_DORA_vers_CODE_Osmose]
    list_col_df_conversion_actions_DORA_vers_CODE_Osmose = ["CODE_Osmose" if col.startswith('Code Osmose') else col for col in list_col_df_conversion_actions_DORA_vers_CODE_Osmose]
    df_conversion_actions_DORA_vers_CODE_Osmose.columns = list_col_df_conversion_actions_DORA_vers_CODE_Osmose
    df_conversion_actions_DORA_vers_CODE_Osmose = df_conversion_actions_DORA_vers_CODE_Osmose.loc[~df_conversion_actions_DORA_vers_CODE_Osmose['CODE_Osmose'].isnull()]
    df_conversion_actions_DORA_vers_CODE_Osmose = df_conversion_actions_DORA_vers_CODE_Osmose.rename(columns=lambda x: x.strip())
    df_conversion_actions_DORA_vers_CODE_Osmose['Catégorie Elus'] = df_conversion_actions_DORA_vers_CODE_Osmose['Catégorie Elus'].fillna(method='ffill')
    df_conversion_actions_DORA_vers_CODE_Osmose['Catégorie Elus'] = df_conversion_actions_DORA_vers_CODE_Osmose['Catégorie Elus'].apply(lambda x: x.strip())
    return df_conversion_actions_DORA_vers_CODE_Osmose

def transformation_tableaux_nom_PPG(self):
    self['nom_PPG_complet'] = self['NOM_PPG']
    self['ALIAS'] = self['ALIAS'].astype(str)
    self['nom_simple_PPG'] = ""
    self.loc[self['ALIAS']!='nan',['nom_simple_PPG']] = self['ALIAS']
    self.loc[self['ALIAS']=='nan',['nom_simple_PPG']] = self['NOM_PPG']
    self['echelle_REF'] = 'PPG'
    return self

def creation_tableaux_nom_custom(dict_dict_info_custom):
    liste_CODE_custom = list(dict_dict_info_custom)
    liste_ALIAS_custom = [dict_dict_info_custom[x]['ALIAS'] for x in liste_CODE_custom]
    liste_NOM_MO_custom = [dict_dict_info_custom[x]['NOM_custom'] for x in liste_CODE_custom]
    self = pd.DataFrame({'CODE_custom':liste_CODE_custom,'nom_simple_custom':liste_ALIAS_custom,'nom_custom_complet':liste_NOM_MO_custom})
    self['echelle_REF'] = 'custom'
    return self


'''def recuperation_tableaux_pressions(GRAND_BV=str(None)):
    df_pression_ME_AG_pour_icone = dataframe.import_pression()
    df_pression_ME_LB_pour_icone = pd.read_csv("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/Me avec pression/Pression ME LB 2022.csv")
    df_pression_ME_AG_pour_icone['CODE_ME'] = df_pression_ME_AG_pour_icone['CODE_ME']
    df_pression_ME_LB_pour_icone['CODE_ME'] = df_pression_ME_LB_pour_icone['CODE_ME']
    liste_colonne_df_pression_AG = list(df_pression_ME_AG_pour_icone)
    liste_colonne_df_pression_LB = list(df_pression_ME_LB_pour_icone)
    liste_elements_classiques_df_pressions = ['CODE_ME','ETAT_ECO','ETAT_CHI']
    liste_colonne_df_pression_AG = [x for x in liste_colonne_df_pression_AG if x not in liste_elements_classiques_df_pressions]
    liste_colonne_df_pression_LB = [x for x in liste_colonne_df_pression_LB if x not in liste_elements_classiques_df_pressions]
    df_pression_ME_AG_pour_icone = df_pression_ME_AG_pour_icone.rename(columns={k:'AG_'+k for k in liste_colonne_df_pression_AG})
    df_pression_ME_LB_pour_icone = df_pression_ME_LB_pour_icone.rename(columns={k:'LB_'+k for k in liste_colonne_df_pression_LB})
    df_pression_ME_AG_pour_icone['CODE_REF'] = df_pression_ME_AG_pour_icone['CODE_ME']
    df_pression_ME_LB_pour_icone['CODE_REF'] = df_pression_ME_LB_pour_icone['CODE_ME']
    df_pression_ME_AG_pour_icone['CODE_GRAND_BASSIN'] = 'AG'
    df_pression_ME_LB_pour_icone['CODE_GRAND_BASSIN'] = 'LB'
    df_pression = pd.concat([df_pression_ME_AG_pour_icone,df_pression_ME_LB_pour_icone])
    if GRAND_BV!=None:
        df_pression = df_pression.loc[df_pression['CODE_GRAND_BASSIN']==GRAND_BV]
        df_pression = df_pression.loc[:, ~df_pression.where(df_pression.astype(bool)).isna().all(axis=0)]
        #df_pression = df_pression.rename({k:k[3:] for k in [x for x in list(df_pression) if x.startswith(GRAND_BV)]},axis=1)
    return df_pression'''



def traitement_avancement_tableau_attributs_Osmose(df_attributs_Osmose):
    dict_conversion_avancement = {1:"Prévisionnelle",2:"Initiée",3:"Engagée",4:"Terminée",5:"Abandonnée"}
    dict_conversion_avancement_inverse = {v: k for k, v in dict_conversion_avancement.items()}
    df_attributs_Osmose["Obligatoire é partir"] = df_attributs_Osmose["Obligatoire é partir"].map(dict_conversion_avancement_inverse)
    return df_attributs_Osmose

def modification_lignes_supprimees_tableau_attributs_Osmose(self):
    self.loc[(self["Sous-domaine"]=="MIA03-Gestion des cours d'eau - continuité")&(self["Attribut"]=="Code ROE"),"Obligatoire é partir"] = "Prévisionnelle"
    return self

def ajout_info_pression_traitee_par_action(df,df_conversion_actions_DORA_vers_CODE_Osmose):
    dict_conversion_pression_traitee = dict(zip(df_conversion_actions_DORA_vers_CODE_Osmose.type_action_DORA,df_conversion_actions_DORA_vers_CODE_Osmose['Catégorie Elus'].to_list()))
    df["Pression_traitee"] = df["NOM_TYPE_ACTION_DORA"].map(dict_conversion_pression_traitee)
    df["Pression_traitee"] = df["Pression_traitee"].apply(lambda x: x.strip())
    dict_renommage_pression = {"Morphologie":"P_MORPHO","Restauration Continuité":"P_CONTI","Hydrologie":"P_HYDRO"}
    df["Pression_traitee"] = df["Pression_traitee"].map(dict_renommage_pression)
    return df



#####################################################################################################
#Pression
#####################################################################################################
def import_pression():
    filename = ("shp_files\\ME\\Pression ME AG 2022.csv")
    filename = connect_path.get_file_path_racine(filename)
    df_pression_AG = pd.read_csv(filename)    
    df_pression_AG = df_pression_AG.fillna(-1)
    df_pression_AG['P_hydromorpho'] = df_pression_AG[['P_CONTI','P_HYDRO','P_MORPHO']].max(axis=1)
    list_col_valeur = [x for x in list(df_pression_AG) if x!="CODE_ME"]
    for nom_col in list_col_valeur:
        df_pression_AG[nom_col] = df_pression_AG[nom_col].astype(int)
    return df_pression_AG


#####################################################################################################
#SANDRE
#####################################################################################################
def recuperation_BDD_SANDRE():
    filename = ("df_info_CODE_SANDRE.csv")
    filename = connect_path.get_file_path_racine(filename,"BDD_SANDRE")
    BDD_SANDRE = pd.read_csv(filename)      
    BDD_SANDRE["CODE_SIRET"] = BDD_SANDRE["CODE_SIRET"].astype(str)
    return BDD_SANDRE

#####################################################################################################
#MO
#####################################################################################################
def recuperation_BDD_SIRET():
    filename = ("df_info_CODE_SIRET_tempo.csv")
    filename = connect_path.get_file_path_racine(filename)
    BDD_SIRET = pd.read_csv(filename)
    BDD_SIRET["CODE_SIRET"] = BDD_SIRET["CODE_SIRET"].astype(str)
    return BDD_SIRET

def recuperation_df_liste_MO_generique():
    filename = ("config\\DORA\\liste_MO_generique.csv")
    filename = connect_path.get_file_path_racine(filename)
    df_liste_MO_generique = pd.read_csv(filename)     
    return df_liste_MO_generique

#####################################################################################################
#continuité
#####################################################################################################
def import_df_liste_ouvrage_prioritaire_PARCE():
    df_ouvrage_prio_PARCE= pd.read_csv("/mnt/g/travail/python/DORA/moulinette/fichiers moulinette import Osmose/Ouvrage_prioritaire_apaise_AG.csv")
    df_ouvrage_prio_PARCE = df_ouvrage_prio_PARCE.rename({"Code ROE":"CODE_ROE","priorisation Adour Garonne":"phase"},axis=1)
    return df_ouvrage_prio_PARCE

#####################################################################################################
#continuité
#####################################################################################################
def import_BDD_DORA():
    BDD_DORA = pd.read_csv("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/BDD_DORA.csv")
    return BDD_DORA