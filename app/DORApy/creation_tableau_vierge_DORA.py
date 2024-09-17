# -*- coding: utf-8 -*-
#####################################################################
#Classe (man, top of the pop)
#####################################################################
from app.DORApy.classes.Class_DictCustomMaitre import DictCustomMaitre
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes.Class_DictDonnees import DictDonnees
from app.DORApy.classes import Class_NDictGdf
import pandas as pd

#liste_NOM_custom = ["BORDEAUX METROPOLE"]
#liste_NOM_custom =["SYNDICAT MIXTE DU BASSIN DE LA SEUDRE"]
#liste_NOM_custom =["COMMUNAUTE DE COMMUNES MEDOC ESTUAIRE"]
#liste_NOM_custom =["DEUX-SEVRES"]

#liste_NOM_custom =["SYNDICAT MIXTE DES BASSINS VERSANTS CENTRE MEDOC - GARGOUILH"]
liste_NOM_custom = ["Syndicat de gestion des bassins versants de l'Entre Deux Mers Ouest"]


def create_tableau_vierge_DORA(liste_NOM_custom):
    ##Creation class principale qui appelle toutes les autres classes automatiquement
    dict_custom_maitre = DictCustomMaitre({})

    dict_custom_maitre.set_config_type_projet(type_rendu='tableau_vierge',type_donnees='action',thematique='MIA',public_cible="elu",liste_echelle_shp_custom_a_check=['MO','DEP'],liste_grand_bassin=['AG'])
    
    dict_dict_info_REF = DictDfInfoShp({})
    dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp()


    dict_geom_REF = Class_NDictGdf.NDictGdf({})
    dict_geom_REF = Class_NDictGdf.remplissage_dictgdf(dict_geom_REF,dict_custom_maitre,dict_dict_info_REF)

    dict_custom_maitre = DictCustomMaitre.creation_entite_custom(dict_custom_maitre,dict_dict_info_REF,liste_NOM_custom)
    dict_custom_maitre = DictCustomMaitre.attributs_gdf_custom(dict_custom_maitre,dict_geom_REF,dict_dict_info_REF,liste_NOM_custom)
    dict_custom_maitre = DictCustomMaitre.attributs_CODE_CUSTOM(dict_custom_maitre,dict_dict_info_REF)
    dict_custom_maitre = DictCustomMaitre.attributs_echelle_base_REF(dict_custom_maitre,dict_dict_info_REF)

    dict_custom_maitre = DictCustomMaitre.attributs_liste_echelle_base_REF(dict_custom_maitre)
    dict_custom_maitre = DictCustomMaitre.creation_boite_projet_carto(dict_custom_maitre)

    dict_custom_maitre = DictCustomMaitre.attributs_liste_echelle_REF_projet(dict_custom_maitre)


    #####################################################################
    #Import des couches geom
    #####################################################################
        #Import des couches custom
    #dict_special_custom_a_reduire = DictDictInfoCustom.dict_special_custom_a_reduire(dict_special_custom_a_reduire,dict_custom_maitre)
    dict_geom_REF = Class_NDictGdf.remplissage_dictgdf(dict_geom_REF,dict_custom_maitre,dict_dict_info_REF)

    num_iteration = 1
    while num_iteration == 1 or num_iteration == 2:
    
        df_info_custom = dict_custom_maitre.creation_df_info_custom()
        dict_dict_info_custom = dict_custom_maitre.creation_dict_dict_info_custom(df_info_custom)
        dict_dict_info_custom = dict_custom_maitre.attributs_dict_dict_info_custom(dict_dict_info_custom)
        #Découpage des custom à réduire
        #####################################################################
        #Création des attributions géographiques
        #####################################################################
            #Relation géographiques entre custom et référentiels
        dict_decoupREF = Class_NDictGdf.creation_dict_decoupREF(dict_geom_REF,dict_custom_maitre)
            #Relation géographiques entre référentiels
        dict_relation_shp_liste = Class_NDictGdf.extraction_dict_relation_shp_liste_a_partir_decoupREF(dict_custom_maitre,dict_decoupREF)

            #Recupération des fichiers d'info
        dict_df_donnees = DictDonnees.recuperation_donnees_pour_projet(dict_custom_maitre,dict_dict_info_REF)
        dict_df_donnees = DictDonnees.traitement_donnees(dict_df_donnees,dict_custom_maitre,dict_dict_info_REF,dict_relation_shp_liste)
        num_iteration = 3
    #####################################################################
    #export du tableau perso
    #####################################################################
    fichier_excel = DictCustomMaitre.export_fichier_excel_perso(dict_custom_maitre,dict_relation_shp_liste,dict_dict_info_REF,dict_decoupREF)
    return fichier_excel
    #projet_representation_action.macro_tableaux_excel(dict_relation_shp_liste)


