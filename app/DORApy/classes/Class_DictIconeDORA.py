import os
from app.DORApy.classes.modules import connect_path

environment = os.getenv('ENVIRONMENT')
chemin_fichiers_shp = os.getenv('chemin_fichiers_shp')
bucket_common_files = os.getenv('S3_BUCKET_COMMON_FILES')
bucket_back_up = os.getenv('S3_BUCKET_BACK_UP')

class Icone:
    def __init__(self,folder_path=None,complet_path=None,relative_path=None,filename=None,thematique=None,type_icone=None,url_publique=None):
        self.nom_type = "icone"
        self.folder_path = folder_path
        self.relative_path = relative_path
        self.complet_path = complet_path
        self.filename = filename
        self.thematique = thematique
        self.type_icone = type_icone
        self.url_publique = url_publique


class DictIcone(dict):
    def __init__(self):
        self.name = "dict_Icone"

    def __repr__(self):
        return f"nom_gdf : {self.name}"
    
    def remplissage_dict_icone(self,thematique,type_icone):
        folder_path_1 = "config/icones_DORA"
        folder_path_2 = "icone_" + thematique + "_" + type_icone
        folder_path = os.path.join(folder_path_1,folder_path_2)
        list_nom_fichier=connect_path.lister_exclu_fichiers_folder_s3(bucket_common_files,folder_path)
        list_nom_icone = [x for x in list_nom_fichier if x.endswith(".svg")]
        for nom_icone in list_nom_icone:
            complet_path = os.path.join(bucket_common_files,folder_path,nom_icone)
            relative_path = os.path.join(folder_path,nom_icone)
            filename = nom_icone
            thematique = thematique
            type_icone = type_icone
            url_publique = connect_path.generer_un_lien_public_sur_s3(bucket_common_files, relative_path, expiration=3600)
            icone=Icone(folder_path,complet_path,relative_path,filename,thematique,type_icone,url_publique)
            nom_cle=os.path.splitext(("_").join(filename.split("_")[1:]))[0]
            self[nom_cle] = icone
        return self
    
    