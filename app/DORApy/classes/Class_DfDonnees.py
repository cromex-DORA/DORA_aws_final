import pandas as pd
import geopandas as gpd
import sys
sys.path.append('./app/DORApy/classes/modules')
import config_DORA,texte,custom,PPG,dataframe
import os.path
from os import path
import numpy as np
import copy
import itertools
import textwrap

dict_config_espace,dict_config_police = config_DORA.creation_dicts_config()

##########################################################################################
#bloc_texte_simple (nom des ME, nom PPG)
##########################################################################################
class DfDonnees(pd.DataFrame):
    @property
    def _constructor(self):
        return DfDonnees

    def conversion_special_CODE_REF_boite_ortho_Bloc_Texte(self,projet,dict_dict_info_custom,dict_relation_shp_liste):
        for CODE_custom,dict_info_custom in dict_dict_info_custom.items():
            if dict_dict_info_custom[CODE_custom]["cartouche_boite_ortho_separe"]==False:
                pass
            if dict_dict_info_custom[CODE_custom]["cartouche_boite_ortho_separe"]==True:
                if len(dict_dict_info_custom[CODE_custom]["liste_echelle_boite_ortho"])>1:
                    echelle_final = projet.echelle_shp_custom
                    liste_echelle_a_remplacer = [x for x in dict_dict_info_custom[CODE_custom]["liste_echelle_boite_ortho"] if x != echelle_final]
                    self = self.loc[(self["echelle_REF"]!=echelle_final)]
                    for echelle_a_remplacer in liste_echelle_a_remplacer:
                        #Il faut indiquer, méme si on est é l'échelle du GEMAPIen, les infos du PPG.
                        inv_dict_relation_shp_liste = { v: k for k, l in dict_relation_shp_liste['dict_liste_' + echelle_a_remplacer + '_par_' + echelle_final].items() for v in l }
                        self.loc[(self["echelle_REF"]=='echelle_a_remplacer'),'CODE_REF'] = self['CODE_REF'].map(inv_dict_relation_shp_liste)
                        self.loc[(self["echelle_REF"]=='echelle_a_remplacer'),'echelle_REF'] = 'echelle_'+echelle_final
        return self

##########################################################################################
#bloc_icone
##########################################################################################

    ##########################################################################################
    #Pressions
    ##########################################################################################

    def definition_presence_boite_ortho_function_integral_PPG_ou_MO(self,dict_dict_info_custom):
        liste_df_custom = []
        for CODE_custom,dict_info_custom in dict_dict_info_custom.items():
            df_custom = self[self['CODE_tableau_origine'] == CODE_custom]
            if dict_info_custom['PPG_inclus_dans_integral_custom'] == True:
                df_custom.loc[df_custom['Integral_PPG']==df_custom['Integral_PPG'],'Integral_MO'] = "x"
                if len(df_custom.loc[~df_custom['Integral_MO'].isnull()])>0:
                    dict_info_custom['cartouche_boite_ortho_separe'] = True
                if len(df_custom.loc[~df_custom['Integral_MO'].isnull()])==0:
                    dict_info_custom['cartouche_boite_ortho_separe'] = False
            if dict_info_custom['PPG_inclus_dans_integral_custom'] == False:
                if len(df_custom.loc[~df_custom['Integral_MO'].isnull()])>0:
                    dict_info_custom['cartouche_boite_ortho_separe'] = True
                if len(df_custom.loc[~df_custom['Integral_MO'].isnull()])==0:
                    dict_info_custom['cartouche_boite_ortho_separe'] = False
            liste_df_custom.append(df_custom)
        self = pd.concat(liste_df_custom)
        return self
 
    def conversion_CODE_ME_CODE_REF(self,projet):
        self['CODE_REF'] = self['CODE_'+projet.echelle_base_REF]
        return self

    def conversion_CODE_REF_function_integral_PPG_ou_MO(self,projet,dict_dict_info_custom):
        if len(self)>0:
            self['echelle_REF'] = self['echelle_princ_action']
            for CODE_custom,dict_CODE_custom in dict_dict_info_custom.items():
                for echelle_dans_boite_normal in dict_CODE_custom['liste_echelle_boite_normal']:
                    self.loc[(self['echelle_princ_action'] == echelle_dans_boite_normal)&(self['CODE_tableau_origine']==CODE_custom),'CODE_REF'] = self['CODE_'+echelle_dans_boite_normal]
            #Ici, dans l'ideal, il faudrait définir le niveau le plus bas des ortho et tout mettre dedans
            for CODE_custom,dict_CODE_custom in dict_dict_info_custom.items():
                for echelle_dans_boite_ortho in dict_CODE_custom['liste_echelle_boite_ortho']:
                    self.loc[(self['echelle_princ_action'] == echelle_dans_boite_ortho)&(self['CODE_tableau_origine']==CODE_custom),'CODE_REF'] = self['CODE_'+dict_dict_info_custom[CODE_custom]["info_texte_simple_boite_ortho"]]
        return self


    def conversion_special_CODE_REF_boite_ortho_Bloc_Icone(self,projet,dict_dict_info_custom):
        for CODE_custom,dict_info_custom in dict_dict_info_custom.items():
            if dict_dict_info_custom[CODE_custom]["cartouche_boite_ortho_separe"]==False:
                pass
            if dict_dict_info_custom[CODE_custom]["cartouche_boite_ortho_separe"]==True:
                if len(dict_dict_info_custom[CODE_custom]["liste_echelle_boite_ortho"])>1:
                    echelle_final = projet.echelle_shp_custom
                    liste_echelle_a_remplacer = [x for x in dict_dict_info_custom[CODE_custom]["liste_echelle_boite_ortho"] if x != echelle_final]
                    for echelle_a_remplacer in liste_echelle_a_remplacer:
                        self.loc[(self["CODE_tableau_origine"]==CODE_custom)&(self["echelle_REF"]=='echelle_a_remplacer'),'CODE_REF'] = self['CODE_'+echelle_final]
                        self.loc[(self["CODE_tableau_origine"]==CODE_custom)&(self["echelle_REF"]=='echelle_a_remplacer'),'echelle_REF'] = 'echelle_'+echelle_final
        return self



