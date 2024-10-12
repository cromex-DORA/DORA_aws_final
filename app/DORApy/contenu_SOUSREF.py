# -*- coding: utf-8 -*-
import pandas as pd
import sys
import geopandas as gpd
import json
from shapely.geometry import shape

pd.set_option("display.max_rows", None, "display.max_columns", None,'display.max_colwidth',None)
from app.DORApy.classes.Class_DictCustomMaitre import DictCustomMaitre
from app.DORApy.classes.Class_dictGdfCompletREF import dictGdfCompletREF,GdfCompletREF
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes import Class_NDictGdf

def generation_json_pression_ME(CODE_ME):
    type_REF_maj = "MO"
    dict_dict_info_REF = DictDfInfoShp({})
    dict_dict_info_REF = dict_dict_info_REF.creation_DictDfInfoShp()

