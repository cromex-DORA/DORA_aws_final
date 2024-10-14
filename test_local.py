import os

os.environ['ENVIRONMENT'] = 'test'
from app.DORApy.classes.Class_DictIconeDORA import DictIcone
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
import svgwrite
from io import BytesIO

# Initialise dict_dict_info_REF
'''dict_dict_info_REF = DictDfInfoShp({})
dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp()

selectedMEId="FRFR288A"

df_tempo = dict_dict_info_REF['df_info_ME'].loc[dict_dict_info_REF['df_info_ME']['CODE_ME']==selectedMEId]
df_tempo.to_dict('index')
print("coucou")'''
dict_icone = DictIcone()
dict_icone = dict_icone.remplissage_dict_icone("MIA","PRESS")

# Créer un SVG avec un rectangle et une icône
dwg = svgwrite.Drawing(size=(500, 500))

# Rectangle pour représenter Paris
#dwg.add(dwg.rect(insert=(100, 100), size=(200, 200), fill='lightblue', stroke='black', stroke_width=2))

# Ajouter l'icône au centre du rectangle
dwg.add(dwg.image(dict_icone['MIA_PRESS_ASS'].url_publique, insert=(175, 175), size=(50, 50)))

# Sauvegarder dans un fichier en mémoire
svg_io = BytesIO()
svg_io.write(dwg.tostring().encode('utf-8'))
svg_io.seek(0)
print("coucou")
