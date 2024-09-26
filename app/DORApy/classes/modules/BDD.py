# -*- coding: utf-8 -*-
import os
import boto3
import pandas as pd
from pathlib import Path
from app.DORApy.classes.modules import config_DORA
from app.DORApy.classes.modules import connect_path
from openpyxl import load_workbook
pd.set_option("display.max_rows", None, "display.max_columns", None,'display.max_colwidth',None)
pd.options.mode.chained_assignment = None  # default='warn'

###Production
environment = os.getenv('ENVIRONMENT')

#####################################################################################################
#PDM
#####################################################################################################
def import_df_PDM_AG():
    filename = ("config\\Osmose\\PDM_2024_AG.csv")
    filename = connect_path.conv_s3_obj_vers_python_obj("config",filename)
    df_PDM_AG= pd.read_csv(filename, index_col=0)
    dict_renom = {"Code Osmose de l'action/mesure":"CODE_PDM","Code du type d'action":"CODE_TYPE_ACTION_OSMOSE","Code(s) us-pdm":"CODE_BVG","Code du sous-domaine":"SOUS_DOMAINE_OSMOSE"}
    df_PDM_AG = df_PDM_AG.rename(dict_renom,axis=1)
    df_PDM_AG = df_PDM_AG[list(dict_renom.values())]
    df_PDM_AG["CODE_BVG"] = df_PDM_AG["CODE_BVG"].apply(lambda x: x.split(";"))
    
    df_info_complementaire_info_CODE_Osmose = config_DORA.recuperation_df_info_complementaire_info_CODE_Osmose()
    df_info_complementaire_info_CODE_Osmose['SOUS_DOMAINE_OSMOSE'] = df_info_complementaire_info_CODE_Osmose["CODE_TYPE_ACTION_OSMOSE"].apply(lambda x: x[:-2])
    df_tempo = df_info_complementaire_info_CODE_Osmose.groupby('SOUS_DOMAINE_OSMOSE').agg({'CODE_TYPE_ACTION_OSMOSE':lambda x: list(x)})
    
    df_PDM_AG_precis = df_PDM_AG.loc[~df_PDM_AG["CODE_TYPE_ACTION_OSMOSE"].isnull()]
    df_PDM_AG_precis["CODE_TYPE_ACTION_OSMOSE"] = df_PDM_AG_precis["CODE_TYPE_ACTION_OSMOSE"].apply(lambda x: x.split(";"))
    
    df_PDM_AG_pas_precis = df_PDM_AG.loc[df_PDM_AG["CODE_TYPE_ACTION_OSMOSE"].isnull()]
    df_PDM_AG_pas_precis = df_PDM_AG_pas_precis[[x for x in list(df_PDM_AG_pas_precis) if x!="CODE_TYPE_ACTION_OSMOSE"]]
    df_PDM_AG_pas_precis = pd.merge(df_PDM_AG_pas_precis,df_tempo,on="SOUS_DOMAINE_OSMOSE")

    df_PDM_AG = pd.concat([df_PDM_AG_precis,df_PDM_AG_pas_precis])
    
    return df_PDM_AG