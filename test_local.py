import os

os.environ['ENVIRONMENT'] = 'production'
from app.DORApy.manipulation_MO import suppression_shp_MO_gemapi_BDD_DORA
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


suppression_shp_MO_gemapi_BDD_DORA("MO_gemapi_10073")




