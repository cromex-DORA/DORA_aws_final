import os
import sys
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes.modules.connect_path import s3,s3r
import json
environment = os.getenv('ENVIRONMENT')
bucket_users_files = os.getenv('S3_BUCKET_USERS_FILES')
dict_dict_info_REF = DictDfInfoShp({})
dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp(['MO','PPG'])


def get_path_dossier_custom(REF):
    if REF=="MO":
        chemin = "MO_gemapi"
    return chemin

class FolderGemapi:
    def __init__(self, id, path):
        self.id = id
        self.path = path
        self.type_rep = "MO"
        self._typer_rep()
        self.files = []
        self.folders = []

    def add_file(self, file):
        self.files.append(file)

    def add_folder(self, folder):
        self.folders.append(folder)

    def _typer_rep(self):
        self.NOM_MO = dict_dict_info_REF["df_info_MO"].dict_CODE_NOM[self.id]
        self.list_CODE_DEP = dict_dict_info_REF["df_info_MO"].dict_CODE_MO_list_CODE_DEP[self.id]

    def to_dict(self):
        return {
            "id": self.id,
            "path": self.path,
            "files": self.files,
            "folders": [folder.to_dict() for folder in self.folders],
            "type_MO": self.type_rep,
            "name" :self.NOM_MO,
            "list_CODE_DEP" :self.list_CODE_DEP

        }

    def __str__(self):
        return f"repertoire : {self.id},{self.NOM_MO}"


def lister_rep_et_fichiers(bucket_name, folder_prefix):
    response = s3.list_objects_v2(
        Bucket=bucket_name,
        Prefix=folder_prefix,
        Delimiter='/'
    )

    folders_list = []

    # Liste des sous-dossiers
    if 'CommonPrefixes' in response:
        for prefix in response['CommonPrefixes']:
            subfolder_path = prefix['Prefix']
            subfolder_name = subfolder_path.rstrip('/').split('/')[-1]

            # Crée un objet FolderGemapi pour le sous-dossier
            subfolder = FolderGemapi(id=subfolder_name, path=subfolder_path)

            # Ajouter les fichiers dans ce sous-dossier
            files_response = s3.list_objects_v2(
                Bucket=bucket_name,
                Prefix=subfolder_path,
                Delimiter='/'
            )

            if 'Contents' in files_response:
                for content in files_response['Contents']:
                    if content['Key'] != subfolder_path:
                        file_name = content['Key'].replace(subfolder_path, '', 1)
                        if '/' not in file_name:  # Ignore les sous-dossiers
                            subfolder.add_file(file_name)

            folders_list.append(subfolder.to_dict())

    return folders_list

def passage_en_json(folders_list):
    folders_json = json.dumps(folders_list, indent=4)
    return folders_json


