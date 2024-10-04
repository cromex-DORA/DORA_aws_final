import os

os.environ['ENVIRONMENT'] = 'test'

from app.DORApy import creation_carte
from app.DORApy.security import gestion_db_users
from app.DORApy import creation_carte
from app.DORApy.classes.Class_DictCustomMaitre import DictCustomMaitre
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes import Class_NDictGdf,Class_NGdfREF
from app.DORApy.classes.Class_NDictGdf import NDictGdf
from app.DORApy.classes.Class_NGdfREF import NGdfREF
from app.DORApy.classes.Class_DictIconeDORA import DictIcone
from app.DORApy.classes.modules.connect_path import s3,s3r


'''
dict_CUSTOM_maitre = DictCustomMaitre({})

dict_CUSTOM_maitre.set_config_type_projet(type_rendu='tableau_vierge',type_donnees='action',thematique='MIA',public_cible="elu",liste_echelle_shp_CUSTOM_a_check=['MO','DEP'],liste_grand_bassin=['AG'])

dict_dict_info_REF = DictDfInfoShp({})
dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp()


# Initialise dict_geom_REF
dict_geom_REF = Class_NDictGdf.NDictGdf({})
dict_geom_REF = Class_NDictGdf.remplissage_dictgdf(dict_geom_REF, dict_CUSTOM_maitre=None, dict_dict_info_REF=dict_dict_info_REF, liste_echelle_REF=["ME"])

# Relation géographiques entre CUSTOM et référentiels
dict_decoupREF = Class_NDictGdf.creation_dict_decoupREF(dict_geom_REF, dict_CUSTOM_maitre)

# Relation géographiques entre référentiels
dict_relation_shp_liste = Class_NDictGdf.extraction_dict_relation_shp_liste_a_partir_decoupREF(dict_CUSTOM_maitre, dict_decoupREF)
print("Données initialisées", file=sys.stderr)

dict_geom_MO = NDictGdf.recuperation_gdf_REF(dict_geom_REF,"ME")
dict_geom_MO = NGdfREF.ajout_nom_ME_simplifie(dict_geom_MO)'''

dict_icone = DictIcone()
dict_icone = dict_icone.remplissage_dict_icone("MIA","PRESS")
dict_icone_pour_json = {nom_icone:icone_dict.url_publique for nom_icone,icone_dict in dict_icone.items()}
print("cocou")

