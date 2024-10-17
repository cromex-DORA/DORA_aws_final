import os

os.environ['ENVIRONMENT'] = 'production'
from app.DORApy.classes.Class_DictIconeDORA import DictIcone
'''from app.DORApy import creation_carte
from app.DORApy.security import gestion_db_users
from app.DORApy import creation_carte-è
from app.DORApy.classes.Class_DictCustomMaitre import DictCustomMaitre
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes import Class_NDictGdf,Class_NGdfREF
from app.DORApy.classes.Class_NDictGdf import NDictGdf
from app.DORApy.classes.Class_NGdfREF import NGdfREF
from app.DORApy.classes.Class_DictIconeDORA import DictIcone
from app.DORApy.classes.modules.connect_path import s3,s3r'''
from app.DORApy import gestion_tableau_DORA
import svgwrite
from io import BytesIO

# Initialise dict_dict_info_REF
'''dict_dict_info_REF = DictDfInfoShp({})
dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp()

selectedMEId="FRFR288A"'''
CODE_MO= ["MO_gemapi_10041","MO_gemapi_10005"]

gestion_tableau_DORA.upload_tableau_final_vers_BDD_DORA(CODE_MO)
