# -*- coding: utf-8 -*-
#####################################################################
#Classe (man, top of the pop)
#####################################################################
from app.DORApy.classes.Class_DictCustomMaitre import DictCustomMaitre
from app.DORApy.classes.Class_DictDonnees import DictDonnees
from app.DORApy.classes.Class_DictBoiteComplete import DictBoiteComplete
from app.DORApy.classes.dict_buffer import dict_buffer
from app.DORApy.classes.Class_DfTableauxActionsMIA import DfTableauxActionsMIA
from app.DORApy.classes.Class_dictGdfCompletREF import dictGdfCompletREF
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes import Class_NDictGdf
import sys


def verification_tableau_vierge_DORA(liste_NOM_CUSTOM):
    dict_CUSTOM_maitre = DictCustomMaitre({})
    dict_CUSTOM_maitre.format_rendu = 'A3'
    dict_CUSTOM_maitre.set_config_type_projet(type_rendu='verif_tableau_DORA',type_donnees='action',thematique='MIA',public_cible='MO',liste_echelle_shp_CUSTOM_a_check=['DEP','MO'],liste_grand_bassin=['AG'])

    dict_geom_REF = Class_NDictGdf.NDictGdf({})
    dict_geom_REF = Class_NDictGdf.remplissage_dictgdf(dict_geom_REF,dict_CUSTOM_maitre,dict_dict_info_REF)

    dict_dict_info_REF = DictDfInfoShp({})
    dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp()
 
    dict_CUSTOM_maitre = DictCustomMaitre.creation_entite_CUSTOM(dict_CUSTOM_maitre,dict_dict_info_REF,liste_NOM_CUSTOM)
    dict_CUSTOM_maitre = DictCustomMaitre.attributs_gdf_CUSTOM(dict_CUSTOM_maitre,dict_geom_REF,dict_dict_info_REF,liste_NOM_CUSTOM)
    dict_CUSTOM_maitre = DictCustomMaitre.attributs_CODE_CUSTOM(dict_CUSTOM_maitre,dict_dict_info_REF)
    #dict_CUSTOM_maitre = DictCustomMaitre.attributs_echelle_base_REF(dict_CUSTOM_maitre,dict_dict_info_REF)

    dict_CUSTOM_maitre = DictCustomMaitre.attributs_liste_echelle_base_REF(dict_CUSTOM_maitre)
    dict_CUSTOM_maitre = DictCustomMaitre.creation_boite_projet_carto(dict_CUSTOM_maitre)

    dict_CUSTOM_maitre = DictCustomMaitre.attributs_liste_echelle_REF_projet(dict_CUSTOM_maitre)


    #####################################################################
    #Import des couches geom
    #####################################################################
        #Import des couches CUSTOM
    #dict_special_CUSTOM_a_reduire = DictDictInfoCUSTOM.dict_special_CUSTOM_a_reduire(dict_special_CUSTOM_a_reduire,dict_CUSTOM_maitre)
    dict_geom_REF = Class_NDictGdf.remplissage_dictgdf(dict_geom_REF,dict_CUSTOM_maitre,dict_dict_info_REF)

    df_info_CUSTOM = dict_CUSTOM_maitre.creation_df_info_CUSTOM()
    dict_dict_info_CUSTOM = dict_CUSTOM_maitre.creation_dict_dict_info_CUSTOM(df_info_CUSTOM)
    dict_dict_info_CUSTOM = dict_CUSTOM_maitre.attributs_dict_dict_info_CUSTOM(dict_dict_info_CUSTOM)
    #Découpage des CUSTOM à réduire
    #####################################################################
    #Création des attributions géographiques
    #####################################################################
        #Relation géographiques entre CUSTOM et référentiels
    dict_decoupREF = Class_NDictGdf.creation_dict_decoupREF(dict_geom_REF,dict_CUSTOM_maitre)
        #Relation géographiques entre référentiels
    dict_relation_shp_liste = Class_NDictGdf.extraction_dict_relation_shp_liste_a_partir_decoupREF(dict_CUSTOM_maitre,dict_decoupREF)

    dict_CUSTOM_maitre = DictCustomMaitre.definition_liste_echelle_boite_projet_carto(dict_CUSTOM_maitre,dict_relation_shp_liste)
    dict_CUSTOM_maitre = DictCustomMaitre.remplissage_bloc_REF_dict_dict_boite_maitre(dict_CUSTOM_maitre,dict_relation_shp_liste,dict_dict_info_CUSTOM)

            #Recupération des fichiers d'info
    dict_df_donnees = DictDonnees.recuperation_donnees_pour_projet(dict_CUSTOM_maitre,dict_dict_info_REF=None)
    dict_df_donnees = DictDonnees.traitement_donnees(dict_df_donnees,dict_CUSTOM_maitre,dict_dict_info_REF,dict_relation_shp_liste)

    dict_CUSTOM_maitre = DictCustomMaitre.attributs_df_filtre_dans_dict_CUSTOM_maitre(dict_CUSTOM_maitre,dict_df_donnees)
    dict_CUSTOM_maitre = DictCustomMaitre.attributs_df_log_erreur_dans_dict_CUSTOM_maitre(dict_CUSTOM_maitre,dict_df_donnees)
    dict_CUSTOM_maitre = DictCustomMaitre.attributs_echelle_REF_dans_dict_CUSTOM_maitre(dict_CUSTOM_maitre,dict_df_donnees)

    df_log_csv_erreur = DictCustomMaitre.export_log_df_erreur(dict_CUSTOM_maitre)
    tableau_excel=DictCustomMaitre.export_tableau_excel_complet(dict_CUSTOM_maitre,dict_df_donnees)
    return df_log_csv_erreur,tableau_excel

