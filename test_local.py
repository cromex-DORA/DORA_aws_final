import os

os.environ['ENVIRONMENT'] = 'production'

'''from app.DORApy import creation_carte
from app.DORApy.security import gestion_db_users
from app.DORApy import creation_carte
from app.DORApy.classes.Class_DictCustomMaitre import DictCustomMaitre
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes import Class_NDictGdf,Class_NGdfREF
from app.DORApy.classes.Class_NDictGdf import NDictGdf
from app.DORApy.classes.Class_NGdfREF import NGdfREF
from app.DORApy.classes.Class_DictIconeDORA import DictIcone
from app.DORApy.classes.modules.connect_path import s3,s3r'''
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp

# Initialise dict_dict_info_REF
dict_dict_info_REF = DictDfInfoShp({})
dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp()

selectedMEId="FRFR288A"

df_tempo = dict_dict_info_REF['df_info_ME'].loc[dict_dict_info_REF['df_info_ME']['CODE_ME']==selectedMEId]
df_tempo.to_dict('index')
print("coucou")

