# -*- coding: utf-8 -*-
import warnings
from shapely.errors import ShapelyDeprecationWarning
from app.DORApy.classes.modules import connect_path
from api import dict_geom_REF
import pandas as pd
import time
start_time = time.time()
import os
import sys
from flask import Response
import copy


#####################################################################
#Classe (man, top of the pop)
#####################################################################
from app.DORApy.classes.Class_DictCustomMaitre import DictCustomMaitre
from app.DORApy.classes.Class_DictDonnees import DictDonnees
from app.DORApy.classes.Class_DictBoiteComplete import DictBoiteComplete
from app.DORApy.classes.dict_buffer import dict_buffer
from app.DORApy.classes.Class_DictGdfFleche import DictGdfFleche
from app.DORApy.classes.Class_dictGdfCompletREF import dictGdfCompletREF
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes import Class_NDictGdf,Class_NGdfREF


warnings.filterwarnings("ignore","Pandas doesn't allow columns to be created via a new attribute name - see https://pandas.pydata.org/pandas-docs/stable/indexing.html#attribute-access", UserWarning)
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)
pd.options.mode.chained_assignment = None  # default='warn'

pd.set_option("display.max_rows", None, "display.max_columns", None,'display.max_colwidth',None)

#Principe général :
#Carte à l'échelle des syndicats, avec une grosse boite par ME qui contient une petite boite d'icone + une liste d'actions phares écrites en toutes lettres.
#choix_type_carto,liste_CUSTOM_choisi = Menu_selection.menu_selection_projet()


#liste_NOM_CUSTOM = ["GIRONDE"]
#liste_NOM_CUSTOM = ["CHARENTE-MARITIME"]
#liste_NOM_CUSTOM = ["BORDEAUX METROPOLE"]
#liste_NOM_CUSTOM =["SYNDICAT MIXTE DU BASSIN DE LA SEUDRE"]
#liste_NOM_CUSTOM =["COMMUNAUTE DE COMMUNES MEDOC ESTUAIRE"]
#liste_NOM_CUSTOM =["SYNDICAT MIXTE DU BASSIN VERSANT DU RUISSEAU DU GUA"]
#liste_NOM_CUSTOM =["SYNDICAT MIXTE DES BASSINS VERSANTS CENTRE MEDOC - GARGOUILH"]
liste_NOM_CUSTOM = ["Syndicat Mixte d'Aménagement hydraulique des bassins versants du Beuve et de la Bassanne"]
#liste_NOM_CUSTOM = None

def creation_couches_carto(LISTE_CODE_CUSTOM,TYPE_REF=None):
    ##Creation class principale qui appelle toutes les autres classes automatiquement
    dict_CUSTOM_maitre = DictCustomMaitre({})
    notre_projet = "carte_pression_MIA"
    dict_CUSTOM_maitre.format_rendu = 'A3'

    if notre_projet == "carte_action_MIA_elu":
        dict_CUSTOM_maitre.set_config_type_projet(type_rendu='carte',type_donnees='action',thematique='MIA',public_cible="elu",liste_echelle_shp_CUSTOM_a_check=['MO'],liste_grand_bassin=['AG'],info_fond_carte='pression_MIA')
    if notre_projet == "carte_action_MIA_tech":
        dict_CUSTOM_maitre.set_config_type_projet(type_rendu='carte',type_donnees='action',thematique='MIA',public_cible='tech',liste_echelle_shp_CUSTOM_a_check=['MO'],liste_grand_bassin=['AG'],info_fond_carte='pression_MIA')
    if notre_projet == "carte_action_MIA_prefet_dep":
        dict_CUSTOM_maitre.set_config_type_projet(type_rendu='carte',type_donnees='action',thematique='MIA',public_cible='prefet',liste_echelle_shp_CUSTOM_a_check=['DEP'],liste_grand_bassin=['AG'],info_fond_carte='pression_MIA',echelle_REF="DEP",echelle_base_REF="MO")
    if notre_projet == "carte_pression_MIA":
        dict_CUSTOM_maitre.set_config_type_projet(type_rendu='carte',type_donnees='toutes_pressions',thematique='global',public_cible="elu",liste_echelle_shp_CUSTOM_a_check=['MO'],liste_grand_bassin=['AG'],info_fond_carte='etat_eco')

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
    #Découpage des CUSTOM à réduire
    #####################################################################
    #Création des attributions géographiques
    #####################################################################
        #Relation géographiques entre CUSTOM et référentiels
    dict_decoupREF = Class_NDictGdf.creation_dict_decoupREF(dict_geom_REF,dict_CUSTOM_maitre)
        #Relation géographiques entre référentiels
    dict_relation_shp_liste = Class_NDictGdf.extraction_dict_relation_shp_liste_a_partir_decoupREF(dict_CUSTOM_maitre,dict_decoupREF)

    #####################################################################
    #Création des buffers par CUSTOM
    #####################################################################
    dict_df_buffer_CUSTOM = dict_buffer({})
    dict_df_buffer_CUSTOM.creation_ligne_buffer(dict_CUSTOM_maitre)
    dict_df_buffer_CUSTOM.ajout_attributs_coord_points_cardinaux_buffer()

    dict_CUSTOM_maitre = DictCustomMaitre.definition_liste_echelle_boite_projet_carto(dict_CUSTOM_maitre,dict_relation_shp_liste)
    dict_CUSTOM_maitre = DictCustomMaitre.remplissage_bloc_REF_dict_dict_boite_maitre(dict_CUSTOM_maitre,dict_relation_shp_liste)

            #Recupération des fichiers d'info
    dict_df_donnees = DictDonnees.recuperation_donnees_pour_projet(dict_CUSTOM_maitre,dict_dict_info_REF)
    dict_df_donnees = DictDonnees.traitement_donnees(dict_df_donnees,dict_CUSTOM_maitre,dict_dict_info_REF,dict_relation_shp_liste)
    dict_relation_shp_liste = dictGdfCompletREF.actualisation_dict_relation_shp_liste(dict_CUSTOM_maitre,dict_relation_shp_liste,dict_df_donnees)
    dict_CUSTOM_maitre = DictCustomMaitre.initialisation_bloc_avec_liste_entite_base_REF(dict_CUSTOM_maitre,dict_relation_shp_liste)
    dict_CUSTOM_maitre = DictCustomMaitre.repartition_df_donnees_dans_bloc(dict_CUSTOM_maitre,dict_df_donnees,dict_dict_info_REF,dict_decoupREF,dict_relation_shp_liste)
    dict_CUSTOM_maitre = DictCustomMaitre.traitement_special_bloc_ortho_si_plusieurs_echelle(dict_CUSTOM_maitre,dict_relation_shp_liste)
    dict_CUSTOM_maitre = DictCustomMaitre.suppression_blocs_vides(dict_CUSTOM_maitre)
    dict_CUSTOM_maitre = DictCustomMaitre.traitement_bloc_avant_calcul_taille(dict_CUSTOM_maitre,dict_df_donnees,dict_relation_shp_liste)

    #####################################################################
    #Rattachement des info de dict_info_bloc au dict_bloc
    #####################################################################
    dict_CUSTOM_maitre = DictCustomMaitre.suppression_blocs_vides(dict_CUSTOM_maitre)
    dict_CUSTOM_maitre = DictCustomMaitre.remplissage_boite_REF_dict_dict_boite_maitre(dict_CUSTOM_maitre,dict_relation_shp_liste)
    dict_CUSTOM_maitre = DictCustomMaitre.ajout_infos_geometriques_decoupREF_boite_normal(dict_CUSTOM_maitre,dict_decoupREF,dict_df_buffer_CUSTOM)

    #####################################################################
    #Calcul taille des blocs
    #####################################################################
    dict_CUSTOM_maitre = DictCustomMaitre.calcul_taille_bloc(dict_CUSTOM_maitre)

    #On dispose ici d'un dict avec l'intégralité des infos (hors placement).
    #####################################################################
    #Calcul taille boite complete
    #####################################################################
    dict_CUSTOM_maitre = DictCustomMaitre.calcul_taille_boite_complete(dict_CUSTOM_maitre)


    #####################################################################
    #Placement boites completes
    #####################################################################
    dict_CUSTOM_maitre = DictCustomMaitre.definition_point_ancrage_complet_REF_entre_eux(dict_CUSTOM_maitre,dict_df_buffer_CUSTOM)
    dict_CUSTOM_maitre = DictCustomMaitre.recuperation_infos_geom_dans_bloc(dict_CUSTOM_maitre,['normal'])
    dict_CUSTOM_maitre = DictCustomMaitre.ajout_contour_geometry_boite_complete(dict_CUSTOM_maitre,['normal'])
    dict_CUSTOM_maitre = DictCustomMaitre.replacement_eventuel_boite(dict_CUSTOM_maitre,['normal'])
    dict_CUSTOM_maitre = DictCustomMaitre.actualisation_info_geom_dans_bloc(dict_CUSTOM_maitre,['normal'])
        
    '''if num_iteration == 3:
        dict_special_CUSTOM_a_reduire = DictDictInfoCUSTOM.recuperation_taille_boite_complete_par_CUSTOM(dict_special_CUSTOM_a_reduire,dict_boite_complete_pour_placement)
        dict_special_CUSTOM_a_reduire = dict_CUSTOM_maitre.definition_si_CUSTOM_a_reduire(dict_special_CUSTOM_a_reduire,dict_boite_complete_pour_placement,dict_geom_REF['gdf_CUSTOM'],dict_dict_info_CUSTOM)
    num_iteration = 3'''
    #####################################################################
    #Placement intérieur boites
    #####################################################################
        #Placement des blocs à l'intérieur des boites, et des objets à l'intérieur des blocs
    dict_CUSTOM_maitre = DictCustomMaitre.placement_bloc_interieur_boite_complete(dict_CUSTOM_maitre,['normal'])

    #####################################################################
    #Création dict fleches
    ##################################################################### 
    #Création dict fleche boite nom_ME
    #dict_gdf_fleche = copy.deepcopy(dict_CUSTOM_maitre)
    dict_gdf_fleche = DictGdfFleche(dict_CUSTOM_maitre)
    dict_gdf_fleche = DictGdfFleche.creation_dict_gdf_fleche_boite_vers_decoupREF(dict_gdf_fleche,dict_decoupREF)

    #####################################################################
    #Placement eventuel boite ortho
    #####################################################################
    dict_CUSTOM_maitre = DictCustomMaitre.placement_eventuel_boite_ortho(dict_CUSTOM_maitre,['orthogonal'])
    dict_CUSTOM_maitre = DictCustomMaitre.recuperation_infos_geom_dans_bloc(dict_CUSTOM_maitre,['orthogonal'])
    dict_CUSTOM_maitre = DictCustomMaitre.placement_bloc_interieur_boite_complete(dict_CUSTOM_maitre,['orthogonal'])

    #####################################################################
    #Maj dict info bb pour atlas
    ##################################################################### 
    dict_CUSTOM_maitre = DictCustomMaitre.actualisation_dict_dict_info_CUSTOM_avec_bb(dict_CUSTOM_maitre)


    #####################################################################
    #Generation fond de carte
    #####################################################################
    dict_CUSTOM_maitre = DictCustomMaitre.creation_gdf_fond_carte_REF(dict_CUSTOM_maitre,dict_decoupREF,dict_relation_shp_liste)
    dict_CUSTOM_maitre = DictCustomMaitre.ajout_info_fond_carte(dict_CUSTOM_maitre,dict_dict_info_REF)

    #####################################################################
    #Alimentation des colonnes à garder pour l'export QGIS
    ##################################################################### 
    dict_CUSTOM_maitre = DictCustomMaitre.definition_colonne_a_garder_pour_export_vers_QGIS_bloc(dict_CUSTOM_maitre)
    dict_CUSTOM_maitre = DictCustomMaitre.definition_colonne_a_garder_pour_export_vers_QGIS_boite(dict_CUSTOM_maitre)

    #####################################################################
    #Genration colonne atlas
    ##################################################################### 
    dict_CUSTOM_maitre = DictCustomMaitre.generation_col_atlas(dict_CUSTOM_maitre)
    dict_CUSTOM_maitre = DictCustomMaitre.transfert_eventuel_info_bloc_df_vers_bloc_indiv(dict_CUSTOM_maitre)
    dict_CUSTOM_maitre = DictCustomMaitre.garder_colonne_de_attributs_colonne_a_garder(dict_CUSTOM_maitre)
    dict_CUSTOM_maitre = DictCustomMaitre.reduction_nom_colonne_pour_export_QGIS(dict_CUSTOM_maitre)

    dict_gdf_fleche = DictGdfFleche.ajout_colonne_atlas_pour_export_vers_QGIS_dans_fleche(dict_gdf_fleche,dict_CUSTOM_maitre)

    dict_CUSTOM_maitre = DictBoiteComplete.definir_geometry_et_crs_boite(dict_CUSTOM_maitre)

    #####################################################################
    #Export DISSOCIER PRINICPALE ET ORTHO
    #####################################################################
    dict_CUSTOM_maitre = DictCustomMaitre.export_bloc(dict_CUSTOM_maitre)
    dict_CUSTOM_maitre = DictCustomMaitre.export_atlas(dict_CUSTOM_maitre)
    dict_CUSTOM_maitre = DictCustomMaitre.export_fond_carte(dict_CUSTOM_maitre)

    dict_gdf_fleche = DictGdfFleche.export_fleche(dict_gdf_fleche,dict_CUSTOM_maitre)
    exit()


def creation_image_visualisation_folder(CODE_MO):
    image_url=connect_path.get_file_path_racine(os.path.join("MO_gemapi",CODE_MO,'carte_simple_MO_PPG.png'))
    if os.path.isfile(image_url):
        return image_url
    dict_dict_info_REF = DictDfInfoShp({})
    dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp(['MO','PPG'])

    dict_geom_REF = Class_NDictGdf.NDictGdf({})
    dict_geom_REF = Class_NDictGdf.remplissage_dictgdf(dict_geom_REF,dict_CUSTOM_maitre=None,dict_dict_info_REF=dict_dict_info_REF,liste_echelle_REF=['MO','PPG',"ME_CE"])

    image_png=Class_NDictGdf.NDictGdf.creer_image_MO_et_PPG(dict_geom_REF,CODE_MO)
    
    image_png.savefig(image_url)
    return image_url



def ajout_liste_CODE_REF(dict_gdf_REF,type_REF,CODE_DEP):
    df_info_REF = dict_gdf_REF.df_info
    liste_MO_dans_le_DEP = []
    liste_EPTB = df_info_REF.loc[df_info_REF['TYPE_MO']=="EPTB"]['CODE_MO'].to_list()
    print(liste_EPTB, file=sys.stderr)
    liste_Syndicat_dans_le_DEP = df_info_REF.loc[(df_info_REF['CODE_DEP'].apply(lambda x: CODE_DEP in x))&(df_info_REF['TYPE_MO']=="Syndicat")]['CODE_MO'].to_list()
    liste_MO_dans_le_DEP.extend(liste_EPTB)
    liste_MO_dans_le_DEP.extend(liste_Syndicat_dans_le_DEP)
    dict_gdf_REF.gdf = dict_gdf_REF.gdf.loc[dict_gdf_REF.gdf['CODE_MO'].isin(liste_MO_dans_le_DEP)]
    dict_gdf_REF.gdf = pd.merge(dict_gdf_REF.gdf,dict_gdf_REF.df_info[['CODE_MO',"TYPE_MO"]],on="CODE_MO")
    bounds = dict_gdf_REF.gdf.to_crs("EPSG:4326").bounds
    bounds['bounds'] = bounds.apply(lambda row: row.tolist(), axis=1)
    bounds['bounds'] = bounds['bounds'].apply(lambda x:[[x[0],x[1]],[x[2],x[3]]])
    bounds = bounds[['bounds']]
    dict_gdf_REF.gdf = pd.merge(dict_gdf_REF.gdf,bounds,left_index=True,right_index=True)
    geojson_data = Class_NGdfREF.NGdfREF.export_gdf_pour_geojson(dict_gdf_REF)
    return geojson_data

def creation_bb_REF(REF,CODE_REF):
    dict_gdf =   dict_geom_REF['gdf_'+REF]
    dict_gdf.gdf = dict_gdf.gdf.loc[dict_gdf.gdf['CODE_'+REF]==CODE_REF]
    bbox = dict_gdf.gdf.to_crs("EPSG:4326").bounds
    bbox = bbox.to_dict('records')[0]
    return bbox

