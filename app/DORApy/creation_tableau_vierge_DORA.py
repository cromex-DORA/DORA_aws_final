# -*- coding: utf-8 -*-
#####################################################################
#Classe (man, top of the pop)
#####################################################################
from app.DORApy.classes.Class_DictCustomMaitre import DictCustomMaitre
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes.Class_DictDonnees import DictDonnees
from app.DORApy.classes import Class_NDictGdf
import pandas as pd

#liste_NOM_CUSTOM = ["BORDEAUX METROPOLE"]
#liste_NOM_CUSTOM =["SYNDICAT MIXTE DU BASSIN DE LA SEUDRE"]
#liste_NOM_CUSTOM =["COMMUNAUTE DE COMMUNES MEDOC ESTUAIRE"]
#liste_NOM_CUSTOM =["DEUX-SEVRES"]

#liste_NOM_CUSTOM =["SYNDICAT MIXTE DES BASSINS VERSANTS CENTRE MEDOC - GARGOUILH"]
LISTE_CODE_CUSTOM = ["MO_gemapi_10041"]

def create_tableau_vierge_DORA(LISTE_CODE_CUSTOM,TYPE_REF=None):
    ##Creation class principale qui appelle toutes les autres classes automatiquement
    dict_CUSTOM_maitre = DictCustomMaitre({})

    dict_CUSTOM_maitre.set_config_type_projet(type_rendu='tableau_vierge',type_donnees='action',thematique='MIA',public_cible="elu",liste_echelle_shp_CUSTOM_a_check=['MO','DEP'],liste_grand_bassin=['AG'])
    
    dict_dict_info_REF = DictDfInfoShp({})
    dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp()


    dict_geom_REF = Class_NDictGdf.NDictGdf({})
    dict_geom_REF = Class_NDictGdf.remplissage_dictgdf(dict_geom_REF,dict_CUSTOM_maitre,dict_dict_info_REF,TYPE_REF)


    dict_CUSTOM_maitre = DictCustomMaitre.creation_entite_CUSTOM(dict_CUSTOM_maitre,dict_dict_info_REF,dict_geom_REF,LISTE_CODE_CUSTOM,TYPE_REF)
    dict_CUSTOM_maitre = DictCustomMaitre.creation_gdf_CUSTOM(dict_CUSTOM_maitre)
    dict_CUSTOM_maitre = DictCustomMaitre.ajout_df_info_CUSTOM(dict_CUSTOM_maitre)

    dict_CUSTOM_maitre = DictCustomMaitre.attributs_echelle_base_REF(dict_CUSTOM_maitre,dict_dict_info_REF)

    dict_CUSTOM_maitre = DictCustomMaitre.attributs_liste_echelle_base_REF(dict_CUSTOM_maitre)
    dict_CUSTOM_maitre = DictCustomMaitre.creation_boite_projet_carto(dict_CUSTOM_maitre)

    dict_CUSTOM_maitre = DictCustomMaitre.attributs_liste_echelle_REF_projet(dict_CUSTOM_maitre)


    #####################################################################
    #Import des couches geom
    #####################################################################
        #Import des couches CUSTOM
    #dict_special_CUSTOM_a_reduire = DictDictInfoCUSTOM.dict_special_CUSTOM_a_reduire(dict_special_CUSTOM_a_reduire,dict_CUSTOM_maitre)
    dict_geom_REF = Class_NDictGdf.remplissage_dictgdf(dict_geom_REF,dict_CUSTOM_maitre,dict_dict_info_REF)
    dict_geom_REF = Class_NDictGdf.creation_NGdfCustom(dict_geom_REF,dict_CUSTOM_maitre)

    num_iteration = 1
    while num_iteration == 1 or num_iteration == 2:
        #Découpage des CUSTOM à réduire
        #####################################################################
        #Création des attributions géographiques
        #####################################################################
            #Relation géographiques entre CUSTOM et référentiels
        dict_decoupREF = Class_NDictGdf.creation_dict_decoupREF(dict_geom_REF,dict_CUSTOM_maitre)
            #Relation géographiques entre référentiels
        dict_relation_shp_liste = Class_NDictGdf.extraction_dict_relation_shp_liste_a_partir_decoupREF(dict_CUSTOM_maitre,dict_decoupREF)

            #Recupération des fichiers d'info
        dict_df_donnees = DictDonnees.recuperation_donnees_pour_projet(dict_CUSTOM_maitre,dict_dict_info_REF)
        dict_df_donnees = DictDonnees.traitement_donnees(dict_df_donnees,dict_CUSTOM_maitre,dict_dict_info_REF,dict_relation_shp_liste)
        num_iteration = 3
    #####################################################################
    #export du tableau perso
    #####################################################################
    fichier_excel = DictCustomMaitre.export_fichier_excel_perso(dict_CUSTOM_maitre,dict_relation_shp_liste,dict_dict_info_REF,dict_decoupREF)
    return fichier_excel
    #projet_representation_action.macro_tableaux_excel(dict_relation_shp_liste)


