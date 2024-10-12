# -*- coding: utf-8 -*-
from pickle import NONE
import pandas as pd
import geopandas as gpd
import geopandas as gpd
import ast
import subprocess
from app.DORApy.classes.modules import dataframe,ME
import warnings
from dotenv import load_dotenv
from app.DORApy.classes.modules import connect_path
from app.DORApy.classes.modules import config_DORA
from app.DORApy.classes.modules.connect_path import s3,s3r
import os
warnings.filterwarnings("ignore","Pandas doesn't allow columns to be created via a new attribute name - see https://pandas.pydata.org/pandas-docs/stable/indexing.html#attribute-access", UserWarning)

bucket_common_files = os.getenv('S3_BUCKET_COMMON_FILES')
bucket_back_up = os.getenv('S3_BUCKET_BACK_UP')

##########################################################################################
#List de couche gdf de différentes échelles
##########################################################################################
class DictDfInfoShp(dict):
    @property
    def _constructor(self):
        return DictDfInfoShp

    def import_info_MO(self):
        filename = ("shp_files\\syndicats GEMAPI\\fichier_info_MO_gemapi.csv")
        df_info_MO = connect_path.conv_s3_obj_vers_python_obj("config",filename)
        df_info_MO = pd.read_csv(df_info_MO)
        df_info_MO['CODE_DEP'] = df_info_MO['CODE_DEP'].fillna("0").astype(str)
        df_info_MO['CODE_DEP'] = df_info_MO['CODE_DEP'].apply(lambda x:x.split(","))
        df_info_MO['CODE_MO'] = df_info_MO['CODE_MO'].astype(str)
        df_info_MO['NOM_MO'] = df_info_MO['NOM_MO'].astype(str)
        df_info_MO["col_tempo"] = df_info_MO['NOM_init'].apply(lambda x:x.split(chr(40)))
        df_info_MO.loc[(df_info_MO["col_tempo"].str.len()==1)&(~df_info_MO["ALIAS"].isnull()),"nom_usuel"] = df_info_MO["NOM_init"] + " (" + df_info_MO["ALIAS"] + ")"
        df_info_MO.loc[(df_info_MO["col_tempo"].str.len()==1)&(df_info_MO["ALIAS"].isnull()),"nom_usuel"] = df_info_MO["NOM_init"]
        df_info_MO.loc[df_info_MO["col_tempo"].str.len()>1,"nom_usuel"] = df_info_MO["NOM_init"]
        df_info_MO = df_info_MO[[x for x in list(df_info_MO) if x!="col_tempo"]]
        df_info_MO["CODE_SIRET"] = df_info_MO["CODE_SIRET"].astype(str)
        df_info_MO["CODE_SIRET"] = df_info_MO["CODE_SIRET"].apply(lambda x:x.split(".")[0])

        self['df_info_MO'] = DfInfoShp(df_info_MO)
        self['df_info_MO'].set_attributs_df_info_shp('MO',"NOM_MO")
        self['df_info_MO'].ajout_dict_CODE_NOM_et_dict_NOM_CODE()
        self['df_info_MO'].dict_CODE_MO_list_CODE_DEP = dict(zip(df_info_MO['CODE_MO'].to_list(),df_info_MO['CODE_DEP']))
        return self

    def import_info_PPG(self):
        filename = ("shp_files\\ppg\\fichier_info_ppg.csv")
        self['df_info_PPG'] = connect_path.conv_s3_obj_vers_python_obj("config",filename)
        self['df_info_PPG'] = pd.read_csv(self['df_info_PPG'])
        self['df_info_PPG']['debut_PPG'] = self['df_info_PPG']['debut_PPG'].astype('Int64').astype(str)
        self['df_info_PPG'] = DfInfoShp(self['df_info_PPG'])
        self['df_info_PPG'].set_attributs_df_info_shp('PPG',"NOM_PPG")
        self['df_info_PPG'].ajout_dict_CODE_NOM_et_dict_NOM_CODE()
        return self
    
    def import_info_ME(self):
        filename = ("shp_files\\ME\\fichier_info_ME_AG.csv")
        self['df_info_ME'] = connect_path.conv_s3_obj_vers_python_obj("config",filename)
        self['df_info_ME'] = pd.read_csv(self['df_info_ME'])
        df_nom_simple_ME_AG = DfInfoShp.recuperation_tableaux_nom_ME_simple()
        self['df_info_ME'] = self['df_info_ME'].merge(df_nom_simple_ME_AG,how='left',on='CODE_ME')
        self['df_info_ME'].loc[self['df_info_ME']['nom_simple_ME'].isnull(),'nom_simple_ME']=self['df_info_ME']['NOM_ME']
        self['df_info_ME'] = self['df_info_ME'].rename({'nom_simple_ME':'ALIAS'},axis=1)
        self['df_info_ME'] = DfInfoShp(self['df_info_ME'])
        filtre_aval = self['df_info_ME']["liste_CODE_ME_aval"]==self['df_info_ME']["liste_CODE_ME_aval"]
        filtre_amont = self['df_info_ME']["liste_CODE_ME_amont"]==self['df_info_ME']["liste_CODE_ME_amont"]
        self['df_info_ME']['liste_CODE_ME_aval'] = [x.replace("'","") for x in self['df_info_ME']['liste_CODE_ME_aval'].to_list()]
        self['df_info_ME']['liste_CODE_ME_aval'] = [x.strip('][').split(', ') if x==x else [] for x in self['df_info_ME'].loc[filtre_aval]['liste_CODE_ME_aval'].to_list()]
        #self['df_info_ME']['liste_CODE_ME_aval'] = [[x[2:] for x in list_ME] for list_ME in self['df_info_ME'].loc[filtre_aval]['liste_CODE_ME_aval'].to_list()]
        self['df_info_ME']['liste_CODE_ME_amont'] = [x.replace("'","") for x in self['df_info_ME']['liste_CODE_ME_amont'].to_list()]
        self['df_info_ME']['liste_CODE_ME_amont'] = [x.strip('][').split(', ') if x==x else [] for x in self['df_info_ME'].loc[filtre_amont]['liste_CODE_ME_amont'].to_list()]
        #self['df_info_ME']['liste_CODE_ME_amont'] = [[x[2:] for x in list_ME] for list_ME in self['df_info_ME'].loc[filtre_aval]['liste_CODE_ME_amont'].to_list()]
        self['df_info_ME']['liste_CODE_DEP'] = self['df_info_ME']['liste_CODE_DEP'].apply(lambda x: ast.literal_eval(x))
        self['df_info_ME']['DEP_pilote'] = self['df_info_ME']['DEP_pilote'].astype(str)
        self['df_info_ME']['OBJ_ECO'] = self['df_info_ME']['OBJ_ECO'].astype(str)
        self['df_info_ME'].loc[self['df_info_ME']['OBJ_ECO']=="2","OBJ_ETAT_ECO"] = "Bon état " + self['df_info_ME']['DATE_ECO'].astype(str)
        self['df_info_ME'].loc[self['df_info_ME']['OBJ_ECO']=="M","OBJ_ETAT_ECO"] = "Bon potentiel " + self['df_info_ME']['DATE_ECO'].astype(str)
        df_pression_ME_AG = dataframe.import_pression()
        self['df_info_ME'] = pd.merge(self['df_info_ME'],df_pression_ME_AG,on="CODE_ME")
        self['df_info_ME'].set_attributs_df_info_shp('ME',"NOM_ME")
        self['df_info_ME'].ajout_dict_CODE_NOM_et_dict_NOM_CODE()
        
        return self
    
    def import_info_BVG(self):
        filename = ("shp_files\\BVG\\data\\bv_gestion_sdage2022\\fichier_info_BVG.csv")
        self['df_info_BVG'] = connect_path.conv_s3_obj_vers_python_obj("config",filename)
        self['df_info_BVG'] = pd.read_csv(self['df_info_BVG'])
        self['df_info_BVG'] = DfInfoShp(self['df_info_BVG'])
        self['df_info_BVG']['liste_CODE_ME'] = [x.replace("'","") for x in self['df_info_BVG']['liste_CODE_ME'].to_list()]
        self['df_info_BVG'].set_attributs_df_info_shp('BVG',"NOM_BVG")
        self['df_info_BVG'].ajout_dict_CODE_NOM_et_dict_NOM_CODE()
        return self
    
    def import_info_SAGE(self):
        filename = ("shp_files\\SAGE\\fichier_info_SAGE.csv")
        self['df_info_SAGE'] = connect_path.conv_s3_obj_vers_python_obj("config",filename)
        self['df_info_SAGE'] = pd.read_csv(self['df_info_SAGE'])
        self['df_info_SAGE'] = DfInfoShp(self['df_info_SAGE'])
        self['df_info_SAGE'].set_attributs_df_info_shp('SAGE',"NOM_SAGE")
        self['df_info_SAGE'].ajout_dict_CODE_NOM_et_dict_NOM_CODE()
        return self
    
    def import_info_ROE(self):
        filename = ("shp_files\\ROE\\fichier_info_ROE.csv")
        self['df_info_ROE'] = connect_path.conv_s3_obj_vers_python_obj("config",filename)
        self['df_info_ROE'] = pd.read_csv(self['df_info_ROE'])
        self['df_info_ROE'] = DfInfoShp(self['df_info_ROE'])
        self['df_info_ROE']['NOM_ROE'] = self['df_info_ROE']['NOM_ROE'] + " (" + self['df_info_ROE']['NOM_COMMUNE'] + ")"
        self['df_info_ROE'].set_attributs_df_info_shp('ROE',"NOM_ROE")
        self['df_info_ROE'].ajout_dict_CODE_NOM_et_dict_NOM_CODE()       
        return self
    
    def import_info_SME(self):
        filename = ("shp_files\\SOUS_ME\\fichier_info_SME_AG.csv")
        self['df_info_SME'] = connect_path.conv_s3_obj_vers_python_obj("config",filename)
        self['df_info_SME'] = pd.read_csv(self['df_info_SME'])
        self['df_info_SME'] = DfInfoShp(self['df_info_SME'])
        self['df_info_SME']['ME_maitre'] = ["".join(["FR",x]) for x in self['df_info_SME']['ME_maitre'].to_list()]
        self['df_info_SME'].set_attributs_df_info_shp('SME',"NOM_SME")
        self['df_info_SME'].ajout_dict_CODE_NOM_et_dict_NOM_CODE()     
        return self   

    def import_info_DEP(self):
        filename = ("shp_files\\dep\\fichier_info_DEP.csv")
        self['df_info_DEP'] = connect_path.conv_s3_obj_vers_python_obj("config",filename)
        self['df_info_DEP'] = pd.read_csv(self['df_info_DEP'])
        self['df_info_DEP']['CODE_DEP'] = self['df_info_DEP']['CODE_DEP'].astype(str)
        self['df_info_DEP'] = DfInfoShp(self['df_info_DEP'])
        self['df_info_DEP'].set_attributs_df_info_shp('DEP',"NOM_DEP")   
        self['df_info_DEP'].ajout_dict_CODE_NOM_et_dict_NOM_CODE()        
        return self        

    ##########################################################################################
    #dict_gdf_REF : Partie fonctions
    ##########################################################################################
    def creation_DictDfInfoShp(self,liste_REF=None):
        if liste_REF==None:
            liste_REF=['MO','PPG','SAGE','ME','DEP','ROE','SME','BVG']
        if "MO" in liste_REF:
            self = DictDfInfoShp.import_info_MO(self)
        if "PPG" in liste_REF:
            self = DictDfInfoShp.import_info_PPG(self)
        if "SAGE" in liste_REF:
            self = DictDfInfoShp.import_info_SAGE(self)
        if "ME" in liste_REF:
            self = DictDfInfoShp.import_info_ME(self)
        if "DEP" in liste_REF:
            self = DictDfInfoShp.import_info_DEP(self)
        if "ROE" in liste_REF:
            self = DictDfInfoShp.import_info_ROE(self)
        if "SME" in liste_REF:
            self = DictDfInfoShp.import_info_SME(self)
        if "BVG" in liste_REF:        
            self = DictDfInfoShp.import_info_BVG(self)
        return self

    def modif_info_special_SOUS_ME(self,dict_geom_REF):
        if hasattr(dict_geom_REF['gdf_ME'], "dict_conversion_CODE_CODE_SME"):
            dict_conv_CODE = dict_geom_REF['gdf_ME'].dict_conversion_CODE_CODE_SME
            dict_conv_NOM = dict_geom_REF['gdf_ME'].dict_conversion_CODE_NOM_SME
            self['df_info_ME']["CODE_ME"].loc[self['df_info_ME']["CODE_ME"].isin(dict_conv_CODE)] = self['df_info_ME']["CODE_ME"].loc[self['df_info_ME']["CODE_ME"].isin(dict_conv_CODE)].map(dict_conv_CODE)
            self['df_info_ME'] = self['df_info_ME'].explode("CODE_ME")
            self['df_info_ME']["NOM_ME"].loc[self['df_info_ME']["NOM_ME"].isin(dict_conv_NOM)] = self['df_info_ME']["NOM_ME"].loc[self['df_info_ME']["NOM_ME"].isin(dict_conv_NOM)].map(dict_conv_NOM)
            self['df_info_ME'].dict_conversion_CODE_CODE_SME = dict_conv_CODE
            self['df_info_ME'].dict_conversion_CODE_NOM_SME = dict_conv_NOM
        return self


    def maj_fichier_DictDfInfoShp(self,list_REF):
        for REF in list_REF:
            if REF =="MO":
                filename = ("shp_files\\syndicats GEMAPI\\fichier_info_MO_gemapi.csv")
                filename = connect_path.conv_s3_obj_vers_python_obj("config",filename)
                self['df_info_MO'].to_csv(filename,index=False)
            if REF =="PPG":
                filename = ("shp_files\\ppg\\fichier_info_PPG.csv")
                filename = connect_path.conv_s3_obj_vers_python_obj("config",filename)
                self['df_info_PPG'].to_csv(filename,index=False)                
        return self 
    
    def creation_dict_relation_shp_liste_a_partir_fichier_info(self,liste_echelle_REF=['MO','PPG','ME']):
         self = self.creation_DictDfInfoShp()
         dict_relation_shp = {}
         for nom_df_REF_index,df_REF_index in self.items():
             liste_col_avec_liste_CODE = [x for x in list (df_REF_index) if x.startswith('liste_CODE') if len(x.split("_"))==3]
             for liste_CODE in liste_col_avec_liste_CODE:
                 REF_entite = liste_CODE.split('_')[2]
                 dict_relation_shp['liste_' + REF_entite + '_par_' + df_REF_index.echelle_REF] = dict(zip(df_REF_index['CODE_'+df_REF_index.echelle_REF],df_REF_index['liste_CODE_'+REF_entite]))
                 dict_relation_shp['liste_' + REF_entite + '_par_' + df_REF_index.echelle_REF] = {k: ast.literal_eval(v) for k, v in dict_relation_shp['liste_' + REF_entite + '_par_' + df_REF_index.echelle_REF].items() if v==v}

         dict_temporaire_inverse = {}
         for type_relation,dict_liste_relation in dict_relation_shp.items():
             
             REF_index = type_relation.split('_')[3]
             REF_entite = type_relation.split('_')[1]
             dict_temporaire_inverse = {}
             for k,v in dict_liste_relation.items():
                for x in v:
                    dict_temporaire_inverse.setdefault(x,[]).append(k)
         dict_relation_shp.update(dict_temporaire_inverse)
         return dict_relation_shp

    def creation_dict_CODE_NOM(self):
         self = self.creation_DictDfInfoShp()
         dict_dict_CODE_NOM = {}
         for nom_df_REF_index,df_REF_index in self.items():
             dict_dict_CODE_NOM['dict_CODE_NOM_'+df_REF_index.echelle_REF] = dict(zip(df_REF_index['CODE_'+df_REF_index.echelle_REF],df_REF_index[df_REF_index.colonne_nom_entite]))
         return dict_dict_CODE_NOM

    def MAJ_info_REF_special(self,dict_relation_shp_liste,dict_CUSTOM_maitre):
        if dict_CUSTOM_maitre.type_rendu=="special_MO_gestion_SAGE":
            df_info_SAGE = self["df_info_SAGE"]
            dict_inv_MO_par_SAGE = {}
            for k,v in dict_relation_shp_liste['dict_liste_SAGE_par_MO'].items():
                for x in v:
                    dict_inv_MO_par_SAGE.setdefault(x, []).append(k)
            dict_inv_MO_par_SAGE = {k:v[0] for k,v in dict_inv_MO_par_SAGE.items()}
            df_info_SAGE['CODE_MO'] = df_info_SAGE['CODE_SAGE'].map(dict_inv_MO_par_SAGE)
            df_info_SAGE = pd.merge(df_info_SAGE,self["df_info_MO"][["CODE_MO","NOM_MO","CODE_SIRET"]],on="CODE_MO",how="left")
            self["df_info_SAGE"] = df_info_SAGE
            self = DictDfInfoShp.maj_fichier_DictDfInfoShp(self)
        return self

   
    def actualisation_par_utilisateur(REF,dict_dict_info_REF):
        if REF == "MO":
            filename = ("shp_files\\syndicats GEMAPI\\fichier_info_MO_gemapi.csv")
            filename = connect_path.conv_s3_obj_vers_python_obj("config",filename)
            filename = filename.replace("//","\\")
            libreoffice_path = "C:/Program Files/LibreOffice/program/scalc.exe"
            p = subprocess.Popen([libreoffice_path, filename])
            p.wait()
            dict_dict_info_REF = DictDfInfoShp.import_info_MO(dict_dict_info_REF)
            dict_dict_info_REF['df_info_MO'] = dict_dict_info_REF['df_info_MO'].loc[dict_dict_info_REF['df_info_MO']['NOM_MO']!='nan']
            dict_dict_info_REF = DictDfInfoShp.maj_fichier_DictDfInfoShp(dict_dict_info_REF,[REF])
        if REF == "PPG":
            filename = ("shp_files\\ppg\\fichier_info_PPG.csv")
            filename = connect_path.conv_s3_obj_vers_python_obj("config",filename)
            filename = filename.replace("//","\\")
            libreoffice_path = "C:/Program Files/LibreOffice/program/scalc.exe"
            p = subprocess.Popen([libreoffice_path, filename])
            p.wait()
            dict_dict_info_REF = DictDfInfoShp.import_info_PPG(dict_dict_info_REF)
            dict_dict_info_REF['df_info_PPG'] = dict_dict_info_REF['df_info_PPG'].loc[(dict_dict_info_REF['df_info_PPG']['debut_PPG'].str.len()!=4|dict_dict_info_REF['df_info_PPG']['NOM_PPG'].isnull())]
            dict_dict_info_REF['df_info_PPG'].loc[dict_dict_info_REF['df_info_PPG']['CODE_PPG'].apply(lambda x:len(x)<8),"CODE_PPG"] = dict_dict_info_REF['df_info_PPG']['CODE_PPG'] + "_" + dict_dict_info_REF['df_info_PPG']['debut_PPG'].astype(str)
            dict_dict_info_REF = DictDfInfoShp.maj_fichier_DictDfInfoShp(dict_dict_info_REF,[REF])            
        return dict_dict_info_REF

    def ajout_surface_ME(df_info_ME,dict_decoupREF):
        df_info_ME = pd.merge(df_info_ME,dict_decoupREF['gdf_decoupME_CUSTOM'].gdf[['CODE_ME',"surface_ME"]],on="CODE_ME",how='left')
        return df_info_ME

    def boost_df_info_ME(dict_dict_info_REF):
        df_pression_ME_AG = dataframe.import_pression()
        dict_conversion_pression = {0:"Inconnue",1:"Pas de pression",2:"Non signi",3:"Pression signi"}
        list_col_valeur = [x for x in list(df_pression_ME_AG) if x!="CODE_ME"]
        for col_valeur in list_col_valeur:
            df_pression_ME_AG[col_valeur] = df_pression_ME_AG[col_valeur].map(dict_conversion_pression)
        
        df_info_ME_boosted = dict_dict_info_REF['df_info_ME']

        gdf_info_topologie_ME = ME.import_ME_CE_AG()
        
        df_info_topologie_ME = gdf_info_topologie_ME[['eu_cd','size']]
        df_info_topologie_ME = df_info_topologie_ME.rename({"eu_cd":"CODE_ME","size":"longueur_CE_principal"},axis=1)
        #Passage en km
        df_info_topologie_ME['longueur_CE_principal'] = df_info_topologie_ME['longueur_CE_principal']*1000
        
        df_relation_ME_BVG = dict_dict_info_REF['df_info_ME'][["CODE_ME","CODE_BVG"]]
        df_relation_ME_BVG = pd.merge(df_relation_ME_BVG,dict_dict_info_REF['df_info_BVG'][["CODE_BVG","NOM_BVG"]])
        
        df_info_ME_boosted = df_info_ME_boosted[['NOM_ME',"CODE_ME","OBJ_ETAT_ECO","surface_ME"]]
        df_info_ME_boosted = pd.merge(df_info_ME_boosted,df_pression_ME_AG[['CODE_ME','P_hydromorpho','P_CONTI','P_HYDRO','P_MORPHO']],on='CODE_ME',how='left')
        df_info_ME_boosted = pd.merge(df_info_ME_boosted,df_relation_ME_BVG[["CODE_ME","NOM_BVG"]],on='CODE_ME',how='left')
        df_info_ME_boosted = df_info_ME_boosted.merge(df_info_topologie_ME,how='left',on='CODE_ME')
        df_info_ME_boosted = df_info_ME_boosted.sort_values('NOM_ME')
        df_info_ME_boosted = df_info_ME_boosted[['NOM_ME',"CODE_ME",'P_hydromorpho','P_CONTI','P_HYDRO','P_MORPHO',"NOM_BVG","longueur_CE_principal","surface_ME","OBJ_ETAT_ECO"]]
        df_info_ME_boosted["surface_ME"] = df_info_ME_boosted["surface_ME"]/1000000
        df_info_ME_boosted = df_info_ME_boosted.drop_duplicates()
        dict_dict_info_REF['df_info_ME'] = df_info_ME_boosted
        return dict_dict_info_REF
    
    def boost_df_info_SME(dict_dict_info_REF):
        df_tempo_ME_pour_merge = dict_dict_info_REF['df_info_ME'][["CODE_ME",'P_hydromorpho','P_CONTI','P_HYDRO','P_MORPHO',"NOM_BVG","longueur_CE_principal","surface_ME","OBJ_ETAT_ECO"]]
        dict_dict_info_REF['df_info_SME'] = pd.merge(dict_dict_info_REF['df_info_SME'].rename({"ME_maitre":"CODE_ME"},axis=1),df_tempo_ME_pour_merge,on="CODE_ME",how='left')
        return dict_dict_info_REF

    def ajout_surface_SME(df_info_SME,dict_decoupREF):
        df_info_SME = pd.merge(df_info_SME,dict_decoupREF['gdf_decoupSME_CUSTOM'][['CODE_SME',"surface_SME"]],on="CODE_SME",how='left')
        df_info_SME["surface_SME"] = df_info_SME["surface_SME"]/1000000
        return df_info_SME

    def ajout_info_issu_ME(df_info_SME,df_info_ME):
        df_info_SME = df_info_SME.rename({'ME_maitre':"CODE_ME"},axis=1)
        df_info_SME = pd.merge(df_info_SME,df_info_ME[["CODE_ME","NOM_ME",'P_hydromorpho','P_CONTI','P_HYDRO','P_MORPHO',"NOM_BVG","OBJ_ETAT_ECO"]],on="CODE_ME",how="left")
        df_info_SME = df_info_SME.rename({'CODE_ME':"ME_maitre"},axis=1)
        return df_info_SME

    def mise_a_jour_df_info_GEMAPI(dict_dict_info_REF,BDD_SANDRE,BDD_SIRET,gdf_MO):
        def col_CODE_SIRET(df_info_MO):
            df_info_MO.loc[df_info_MO["CODE_SIRET"]=="nan","CODE_SIRET"]="Pas de CODE SIRET"
            return df_info_MO


        def normalisation_NOM_MO(df_info_MO,BDD_SIRET):
            #Normalisation NOM_MO
            
            df_info_MO = df_info_MO.rename({"NOM_MO":"NOM_MO_tempo"},axis=1)
            df_info_MO = pd.merge(df_info_MO,BDD_SIRET[["CODE_SIRET","NOM_MO"]],on="CODE_SIRET",how='left')
            df_info_MO.loc[df_info_MO["NOM_MO"].isnull(),"NOM_MO"] = df_info_MO["NOM_MO_tempo"]
            df_info_MO.loc[df_info_MO["NOM_MO"].isnull(),"NOM_MO"] = df_info_MO['NOM_init']
            df_info_MO = df_info_MO[[x for x in list (df_info_MO) if x!="NOM_MO_tempo"]]

            return df_info_MO
        
        def maj_NOM_DEP(df_info_MO,dict_dict_info_REF):
            df_info_MO["NOM_DEP"] = df_info_MO['CODE_DEP'].astype(str).map(dict_dict_info_REF['df_info_DEP'].dict_CODE_NOM)
            df_info_MO.loc[df_info_MO["CODE_DEP"]=="GLOBAL","NOM_DEP"] = "GLOBAL"
            return df_info_MO
        
        def maj_CODE_SANDRE(df_info_MO,BDD_SANDRE,BDD_SIRET):
            df_gemapi_tempo = df_info_MO.loc[df_info_MO["CODE_SIRET"]!='nan']
            df_gemapi_tempo_deja_renseigne = df_info_MO.loc[df_info_MO["CODE_SIRET"]=='nan']

            list_CODE_SIRET_SANDRE = BDD_SANDRE['CODE_SIRET'].to_list()
            #Separation fichier df gemapi

            #Recherche du CODE SANDRE si il existe
            BDD_SIRET = BDD_SIRET.rename({"CODE_SIRET":"CODE_SIRET_possible"},axis=1)
            df_gemapi_tempo_CODE_SIRET_SANDRE = df_gemapi_tempo[['NOM_MO']]
            df_gemapi_tempo_CODE_SIRET_SANDRE = pd.merge(df_gemapi_tempo_CODE_SIRET_SANDRE,BDD_SIRET,on="NOM_MO",how='left')
            df_gemapi_tempo_CODE_SIRET_SANDRE = df_gemapi_tempo_CODE_SIRET_SANDRE.groupby('NOM_MO').agg({'CODE_SIRET_possible':lambda x: list(x)})
            df_gemapi_tempo_CODE_SIRET_SANDRE["CODE_SIRET_possible"] = df_gemapi_tempo_CODE_SIRET_SANDRE['CODE_SIRET_possible'].apply(lambda x:[CODE_SIRET for CODE_SIRET in x if CODE_SIRET in list_CODE_SIRET_SANDRE])
            df_gemapi_tempo_CODE_SIRET_SANDRE['CODE_SIRET_SANDRE'] = df_gemapi_tempo_CODE_SIRET_SANDRE['CODE_SIRET_possible'].apply(lambda x:x[0] if len(x)>0 else "Ab SANDRE")
            df_gemapi_tempo_CODE_SIRET_SANDRE = df_gemapi_tempo_CODE_SIRET_SANDRE[[x for x in list(df_gemapi_tempo_CODE_SIRET_SANDRE) if x!="CODE_SIRET"]]
            df_gemapi_tempo_CODE_SIRET_SANDRE["NOM_MO"] = df_gemapi_tempo_CODE_SIRET_SANDRE.index
            df_gemapi_tempo_CODE_SIRET_SANDRE = df_gemapi_tempo_CODE_SIRET_SANDRE.reset_index(drop=True)
            df_gemapi_tempo_CODE_SIRET_SANDRE = df_gemapi_tempo_CODE_SIRET_SANDRE[['NOM_MO','CODE_SIRET_SANDRE']]
            df_gemapi_tempo = df_gemapi_tempo[[x for x in list(df_gemapi_tempo) if x!="CODE_SIRET_SANDRE"]]
            df_gemapi_tempo = pd.merge(df_gemapi_tempo,df_gemapi_tempo_CODE_SIRET_SANDRE,on="NOM_MO")
            df_info_MO = pd.concat([df_gemapi_tempo,df_gemapi_tempo_deja_renseigne])
            col_NOM_MO = df_info_MO.pop('NOM_MO')
            df_info_MO.insert(0,'NOM_MO',col_NOM_MO) 
            df_info_MO.loc[df_info_MO["CODE_SIRET_SANDRE"]=='nan',"CODE_SIRET_SANDRE"] = "Ab SANDRE"
            return df_info_MO

        def suppression_MO_si_deja_presentes_dans_df_info_MO(df_info_MO):
            df_info_MO['CODE_SIREN'] = ""
            df_info_MO.loc[df_info_MO['CODE_SIRET']!="Pas de CODE SIRET","CODE_SIREN"] = df_info_MO['CODE_SIRET'].str[:-5]
            df_info_MO_avec_SIREN = df_info_MO.loc[~df_info_MO["CODE_SIREN"].isnull()]
            df_info_MO_sans_SIREN = df_info_MO.loc[df_info_MO["CODE_SIREN"].isnull()]
            df_info_MO_avec_SIREN = df_info_MO_avec_SIREN.drop_duplicates(subset=['CODE_SIREN', 'shp'], keep='first')
            df_info_MO = pd.concat([df_info_MO_avec_SIREN,df_info_MO_sans_SIREN])
            return df_info_MO
        
        def MAJ_fichier_shp_MO(df_info_MO,gdf_MO):
            list_col_gdf_MO = list(gdf_MO)
            gdf_MO = pd.merge(gdf_MO[["CODE_MO","geometry_MO"]],df_info_MO,on="CODE_MO",how='left')
            gdf_MO['surface_MO'] = gdf_MO.area
            gdf_MO = gdf_MO[list_col_gdf_MO]
            return gdf_MO

        df_info_MO = dict_dict_info_REF['df_info_MO']
        df_info_MO = col_CODE_SIRET(df_info_MO)
        df_info_MO = normalisation_NOM_MO(df_info_MO,BDD_SIRET)
        df_info_MO = maj_NOM_DEP(df_info_MO,dict_dict_info_REF)
        df_info_MO = maj_CODE_SANDRE(df_info_MO,BDD_SANDRE,BDD_SIRET)
        #A faire pour alléger la RAM. Quand j'aurai 2 fois 16 Gb, je pourrai enelever ça
        del BDD_SANDRE
        del BDD_SIRET
        df_info_MO = suppression_MO_si_deja_presentes_dans_df_info_MO(df_info_MO)
        df_info_MO.to_csv("/mnt/g/travail/carto/couches de bases/syndicats GEMAPI/fichier_info_MO_gemapi.csv",index=False)
        gdf_MO = MAJ_fichier_shp_MO(df_info_MO,gdf_MO)
        #gdf_MO.to_file("/mnt/g/travail/carto/couches de bases/syndicats GEMAPI/MO_gemapi_NA.shp")
        return df_info_MO

class DfInfoShp(pd.DataFrame):
    @property
    def _constructor(self):
        return DfInfoShp

    def set_attributs_df_info_shp(self,echelle_REF,colonne_nom_entite):
        self.echelle_REF = echelle_REF
        self.colonne_nom_entite = colonne_nom_entite
        self.colonne_CODE_entite = "CODE_"+echelle_REF
        return self

    def ajout_dict_CODE_NOM_et_dict_NOM_CODE(self):
        self.dict_CODE_NOM = dict(zip(self["CODE_"+self.echelle_REF].to_list(),self[self.colonne_nom_entite].to_list()))
        self.dict_NOM_CODE = dict(zip(self[self.colonne_nom_entite].to_list(),self["CODE_"+self.echelle_REF].to_list()))        
        return self

    def recuperation_tableaux_nom_ME_simple():
        filename = ("shp_files\\ME\\etiquette simplifie nom CE AG.csv")
        df_nom_ME_simple = connect_path.conv_s3_obj_vers_python_obj("config",filename)
        df_nom_ME_simple = pd.read_csv(df_nom_ME_simple)    
        df_nom_ME_simple['CODE_ME'] = df_nom_ME_simple['CODE_ME']
        df_nom_ME_simple = df_nom_ME_simple.drop_duplicates(subset=['CODE_ME'])
        return df_nom_ME_simple        