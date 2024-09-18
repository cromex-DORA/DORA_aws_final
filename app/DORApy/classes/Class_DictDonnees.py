import pandas as pd
import geopandas as gpd
from app.DORApy.classes.modules import dataframe
import os.path
from os import path
import numpy as np
import copy
import itertools
import textwrap
from app.DORApy.classes.Class_DictDFTableauxActionsMIA import DictDFTableauxActionsMIA
from app.DORApy.classes.Class_DfTableauxActionsMIA import DfTableauxActionsMIA
from app.DORApy.classes.modules import config_DORA


dict_config_espace,dict_config_police = config_DORA.creation_dicts_config()
dict_dict_config_df_actions_MIA = config_DORA.creation_dict_dict_config_df_actions_MIA()

##########################################################################################
#bloc_texte_simple (nom des ME, nom PPG)
##########################################################################################
class DictDonnees(dict):
    @property
    def _constructor(self):
        return DictDonnees
    
    def recuperation_donnees_pour_projet(self,dict_dict_info_REF=None,forme="remplis"):
        dict_donnees_hors_REF = DictDonnees({})
        liste_contenu_bloc = []
        liste_thematique_bloc = []
        liste_thematique_bloc.append(self.thematique)
        for nom_custom,entite_custom in self.items():
            for nom_boite,dict_boite in entite_custom.items():
                for nom_bloc,dict_bloc in dict_boite.items():
                    liste_contenu_bloc.extend(dict_bloc.sous_type)
        tempo_list = list(itertools.product(liste_contenu_bloc, liste_thematique_bloc))
        liste_contenu_bloc = liste_contenu_bloc + [str(contenu) + '_' + str(thematique) for (contenu,thematique) in tempo_list]
        liste_contenu_bloc = list(set(liste_contenu_bloc))
        self.liste_contenu_bloc = liste_contenu_bloc
        if ('nombre_actions_MIA' or 'actions_phares_MIA') in liste_contenu_bloc:
            liste_echelle_REF = ['MO','DEP']
            dict_dict_df_actions_originaux = DictDFTableauxActionsMIA.recuperation_dict_tableaux_actions_MIA(dict_dict_info_REF,liste_echelle_REF,forme)
            dict_dict_df_actions_originaux = DictDFTableauxActionsMIA.ajout_BDD_Osmose(dict_dict_df_actions_originaux)
            dict_donnees_hors_REF['dict_dict_df_actions_originaux'] = dict_dict_df_actions_originaux
        if 'NOM_REF' in liste_contenu_bloc:
            list_df_info_REF = []
            for echelle_carto in self.liste_echelle_REF_projet:
                df_info_REF = dict_dict_info_REF['df_info_'+echelle_carto]
                df_info_REF = df_info_REF.rename({"CODE_"+echelle_carto:"CODE_REF","NOM_"+echelle_carto:"NOM_REF"},axis=1)
                list_df_info_REF.append(df_info_REF)
            dict_donnees_hors_REF['df_nom_REF_simple'] = pd.concat(list_df_info_REF)
            if 'ALIAS' in list(dict_donnees_hors_REF['df_nom_REF_simple']):
                dict_donnees_hors_REF['df_nom_REF_simple'] = dict_donnees_hors_REF['df_nom_REF_simple'][['CODE_REF','NOM_REF','ALIAS']]
                dict_donnees_hors_REF['df_nom_REF_simple'] = dict_donnees_hors_REF['df_nom_REF_simple'].reset_index(drop=True)
                dict_donnees_hors_REF['df_nom_REF_simple'].loc[dict_donnees_hors_REF['df_nom_REF_simple']['ALIAS'].isnull(),'ALIAS'] = dict_donnees_hors_REF['df_nom_REF_simple']['NOM_REF']
            if 'ALIAS' not in list(dict_donnees_hors_REF['df_nom_REF_simple']):
                dict_donnees_hors_REF['df_nom_REF_simple'] = dict_donnees_hors_REF['df_nom_REF_simple'][['CODE_REF','NOM_REF']]
                dict_donnees_hors_REF['df_nom_REF_simple']['ALIAS'] = dict_donnees_hors_REF['df_nom_REF_simple']['NOM_REF']
        if "pressions" in liste_contenu_bloc:
            df_pression = dataframe.import_pression()
            dict_donnees_hors_REF['df_pression'] = df_pression
            
        if self.type_rendu=='tableau_MAJ_Osmose':
            dict_df_tableaux_osmose_maj = dataframe.recuperer_tableau_OSMOSE()
            dict_donnees_hors_REF['dict_tableau_MAJ_osmose_par_dep'] = dict_df_tableaux_osmose_maj
            
        if self.type_rendu=='verif_tableau_DORA':
            dict_dict_df_actions_originaux = DictDFTableauxActionsMIA.recuperation_dict_tableaux_actions_MIA(self)
            dict_donnees_hors_REF['dict_dict_df_actions_originaux'] = dict_dict_df_actions_originaux

        if self.type_rendu=='tableau_DORA_vers_BDD':
            dict_dict_df_actions_originaux = DictDFTableauxActionsMIA.recuperation_dict_tableaux_actions_MIA(dict_dict_info_REF,liste_echelle_custom=self.liste_echelle_shp_custom_a_check,forme='final')
            dict_donnees_hors_REF['dict_dict_df_actions_originaux'] = dict_dict_df_actions_originaux
        return dict_donnees_hors_REF

    def traitement_donnees(self,dict_custom_maitre=None,dict_dict_info_REF=None,dict_relation_shp_liste=None):
        #Mise ne forme général des données issues des actions des DF (DORA et Osmose et même autres sources)
        if (dict_custom_maitre.type_rendu == "carte" or dict_custom_maitre.type_rendu == "tableau_DORA_vers_BDD") and dict_custom_maitre.type_donnees == "action" and dict_custom_maitre.thematique == "MIA":
            for nom_donnees,contenu_donnees in self.items():
                if nom_donnees == 'dict_dict_df_actions_originaux':
                    contenu_donnees = DictDFTableauxActionsMIA.recuperer_attribut_echelle_base_REF(contenu_donnees,dict_dict_info_REF,dict_custom_maitre)
                    contenu_donnees = DictDFTableauxActionsMIA.gestion_col_echelle_base_REF(contenu_donnees,dict_dict_info_REF,dict_custom_maitre)
                    contenu_donnees = DictDFTableauxActionsMIA.mise_en_forme_tableau_actions_MIA_sans_modif_contenu(contenu_donnees,dict_dict_info_REF)
                    contenu_donnees = DictDFTableauxActionsMIA.mise_en_forme_format_DORA_tableau_actions_MIA_avec_modif_contenu(contenu_donnees,dict_relation_shp_liste,dict_dict_info_REF,dict_custom_maitre)
                    contenu_donnees = DictDFTableauxActionsMIA.suppression_lignes_df_actions_MIA(contenu_donnees,dict_dict_info_REF,dict_custom_maitre)
                    df_BDD_DORA = DictDFTableauxActionsMIA.rassemblement_df_toutes_sources_pour_BDD_DORA(contenu_donnees)
                    
            if 'dict_dict_df_actions_originaux' in self:
                self["BDD_DORA"] = DictDFTableauxActionsMIA({})
                self["BDD_DORA"].df = df_BDD_DORA
                self["BDD_DORA"].echelle_df = "global"
                self["BDD_DORA"].type_df = "DORA"
                dict_config_col_BDD_DORA_vierge = config_DORA.import_dict_config_col_BDD_DORA_vierge()
                self["BDD_DORA"].dict_type_col = dict_config_col_BDD_DORA_vierge['type_col']
                df_BDD_DORA.to_csv("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/test/essai_BDD_DORA.csv")  

        if dict_custom_maitre.type_rendu == "carte" and dict_custom_maitre.type_donnees == "action" and dict_custom_maitre.thematique == "MIA":
            for nom_donnees,contenu_donnees in self.items():
                if nom_donnees == 'BDD_DORA':
                    contenu_donnees = DictDFTableauxActionsMIA.mise_en_forme_specifique_BDD_DORA_pour_carte(contenu_donnees,dict_dict_info_REF,dict_relation_shp_liste,dict_custom_maitre)
                    ###Prevoir repartition

        if dict_custom_maitre.type_rendu == "carte" and dict_custom_maitre.type_donnees == "toutes_pressions" and dict_custom_maitre.thematique == "global":
            for nom_donnees,contenu_donnees in self.items():
                if nom_donnees=="df_pression":
                    self[nom_donnees] = DictDFTableauxActionsMIA.mise_en_forme_df_pressions_carte_pressions(self[nom_donnees])
                    self[nom_donnees] = DictDFTableauxActionsMIA.mise_en_forme_CODE_REF(self[nom_donnees])
                    

        if dict_custom_maitre.type_rendu == "tableau_DORA_vers_BDD" and dict_custom_maitre.type_donnees == "action" and dict_custom_maitre.thematique == "MIA":
            for nom_donnees,contenu_donnees in self.items():
                if nom_donnees == 'dict_dict_df_actions_originaux':

                    contenu_donnees = DictDFTableauxActionsMIA.actualisation_CODE_ME(contenu_donnees,dict_relation_shp_liste)
                    contenu_donnees = DictDFTableauxActionsMIA.transfert_BDD_DORA(contenu_donnees)

                    contenu_donnees = DictDFTableauxActionsMIA.creation_df_pour_onglets(contenu_donnees)
                    contenu_donnees = DictDFTableauxActionsMIA.creation_CODE_IMPORT(contenu_donnees)
                    contenu_donnees = DictDFTableauxActionsMIA.ajout_info_supplementaire_CODE_Osmose(contenu_donnees)
                    contenu_donnees = DictDFTableauxActionsMIA.conv_colonne_avancement(contenu_donnees)
                    contenu_donnees = DictDFTableauxActionsMIA.Cycle_dimport(contenu_donnees)
                    contenu_donnees = DictDFTableauxActionsMIA.titre_action_DORA(contenu_donnees)                    
                    contenu_donnees = DictDFTableauxActionsMIA.col_debut_avancement_et_engagement(contenu_donnees)
                    #continuité
                    contenu_donnees = DictDFTableauxActionsMIA.conv_CODE_ROE_str(contenu_donnees)
                    contenu_donnees = DictDFTableauxActionsMIA.col_SUIVI_PARCE(contenu_donnees)
                    contenu_donnees = DictDFTableauxActionsMIA.etape_continuite(contenu_donnees)
                    #Localisation
                    contenu_donnees = DictDFTableauxActionsMIA.actualisation_CODE_BVG(contenu_donnees,dict_relation_shp_liste)
                    contenu_donnees = DictDFTableauxActionsMIA.col_departement_PAOT(contenu_donnees,dict_dict_info_REF['df_info_ME'])
                    contenu_donnees = DictDFTableauxActionsMIA.col_departement_pilote(contenu_donnees,dict_dict_info_REF)
                    contenu_donnees = DictDFTableauxActionsMIA.col_bassin_DCE(contenu_donnees,dict_dict_info_REF)

                    ###PAOT
                    contenu_donnees = DictDFTableauxActionsMIA.colonne_PAOT(contenu_donnees)   

                    ###MO
                    contenu_donnees = DictDFTableauxActionsMIA.info_MO(contenu_donnees,dict_dict_info_REF["df_info_MO"])
                    ###Attributs
                    contenu_donnees = DictDFTableauxActionsMIA.attributs(contenu_donnees)

                    contenu_donnees = DictDFTableauxActionsMIA.mise_en_forme_tableau_actions_MIA_renommage_colonne(contenu_donnees,dict_custom_maitre)
                    contenu_donnees = DictDFTableauxActionsMIA.renommage_onglets_annexes(contenu_donnees)

        if dict_custom_maitre.type_rendu == "verif_tableau_DORA" and dict_custom_maitre.type_donnees == "action" and dict_custom_maitre.thematique == "MIA": 
            for nom_donnees,contenu_donnees in self.items():
                if nom_donnees == 'dict_dict_df_actions_originaux':
                    contenu_donnees = DictDFTableauxActionsMIA.col_ID_DORA(contenu_donnees)
                    contenu_donnees = DictDFTableauxActionsMIA.recuperer_attribut_echelle_base_REF(contenu_donnees,dict_dict_info_REF,dict_custom_maitre)
                    dict_dict_df_actions_originaux_avec_mise_en_forme_sans_modif = copy.deepcopy(contenu_donnees)
                    contenu_donnees = DictDFTableauxActionsMIA.mise_en_forme_tableau_actions_MIA_sans_modif_contenu(contenu_donnees,dict_dict_info_REF)
                    contenu_donnees = DictDFTableauxActionsMIA.mise_en_forme_format_DORA_tableau_actions_MIA_avec_modif_contenu(contenu_donnees,dict_relation_shp_liste,dict_dict_info_REF,dict_custom_maitre)
                    
                    #Creation log erreur
                    dict_log = {k:{}for k,x in contenu_donnees.items()}
                    dict_log_df_erreur = {k:pd.DataFrame([x for x in range(0,len(x.df))]) for k,x in contenu_donnees.items()}     
                    dict_log = DictDFTableauxActionsMIA.verif_forme_fichiers_actions_MIA(contenu_donnees,dict_dict_info_REF,dict_log)
                    dict_log_df_erreur = DictDFTableauxActionsMIA.verif_df_actions_MIA(contenu_donnees,dict_dict_df_actions_originaux_avec_mise_en_forme_sans_modif,dict_dict_info_REF,dict_log_df_erreur)
                    dict_log_df_erreur = DictDFTableauxActionsMIA.jointure_tableau_origine_avec_erreur(dict_dict_df_actions_originaux_avec_mise_en_forme_sans_modif,dict_log_df_erreur)
                    dict_log_df_erreur = DictDFTableauxActionsMIA.retour_nom_col_tableau_original(dict_log_df_erreur,dict_dict_df_actions_originaux_avec_mise_en_forme_sans_modif)
                    dict_log_df_erreur = DictDFTableauxActionsMIA.mise_en_forme_avant_export(dict_log_df_erreur)
                    for entite_custom,contenu_custom in contenu_donnees.items():
                        contenu_donnees[entite_custom].df_log_erreur = dict_log_df_erreur[entite_custom]
                    
                    #Creation Tableau avec filtrage
                    dict_filtre_tableau_DORA = {k:pd.DataFrame(data={"ID_DORA":x.df['ID_DORA'].to_list()}) for k,x in contenu_donnees.items()}
                    #contenu_donnees = DictDFTableauxActionsMIA.actualisation_CODE_ME(contenu_donnees,dict_relation_shp_liste)
                    dict_filtre_tableau_DORA = DictDFTableauxActionsMIA.filtre_pression_tableau_DORA(dict_filtre_tableau_DORA,contenu_donnees)
                    dict_filtre_tableau_DORA = DictDFTableauxActionsMIA.filtre_PDM(dict_filtre_tableau_DORA,contenu_donnees,dict_relation_shp_liste)
                    dict_filtre_tableau_DORA = DictDFTableauxActionsMIA.filtre_bon_etat(dict_filtre_tableau_DORA,contenu_donnees)
                    dict_filtre_tableau_DORA = DictDFTableauxActionsMIA.filtre_finale(dict_filtre_tableau_DORA)
                    for entite_custom,contenu_custom in contenu_donnees.items():
                        contenu_donnees[entite_custom].df_filtre_tableau = dict_filtre_tableau_DORA[entite_custom]

                        
        if dict_custom_maitre.type_rendu == "tableau_MAJ_Osmose" and dict_custom_maitre.type_donnees == "action" and dict_custom_maitre.thematique == "MIA": 
            for nom_donnees,contenu_donnees in self.items():
                if nom_donnees == 'dict_tableau_MAJ_osmose_par_dep':
                    contenu_donnees = DictDFTableauxActionsMIA.mise_en_forme_tableau_actions_maj_osmose(contenu_donnees,dict_dict_info_REF,dict_relation_shp_liste,dict_custom_maitre)
                      
        return self
    

    
    
    
