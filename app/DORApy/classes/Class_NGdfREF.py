import os
import geopandas as gpd
from app.DORApy.classes.modules.connect_path import s3
from app.DORApy.classes.modules import connect_path
from shapely import Polygon,MultiPolygon
from collections import ChainMap
import json
import pandas as pd
import os
import copy

environment = os.getenv('ENVIRONMENT')
chemin_fichiers_shp = os.getenv('chemin_fichiers_shp')
bucket_common_files = os.getenv('S3_BUCKET_COMMON_FILES')

class NGdfREF:
    def __init__(self,REF, path=None,type_geom=None):
        self.path = path
        
        if REF!="CUSTOM":
            self.name = path.split("/")[-1]
            self.path_folder = ("/").join(path.split("/")[3:-1])
            self.path_relative = ("/").join(path.split("/")[3:])
        self.echelle_REF_shp = REF
        self.colonne_geometry = "geometry_" + REF
        self.nom_entite_REF = "NOM_" + REF
        self.type_de_geom = type_geom
        if REF !="CUSTOM":
            self._ajout_gdf(path,REF)
            self._scan_file(path)

    def _ajout_gdf(self,path,REF):
        gdf = connect_path.lire_gpkg_sur_s3_avec_gpd("CUSTOM",path)
        gdf = gdf.to_crs(2154)
        if self.type_de_geom == "polygon":
            gdf['surface_'+REF] = gdf.area
        if self.type_de_geom == "lignes":
            gdf['longueur_'+REF] = gdf.length  
        gdf = gdf.rename(columns={'geometry':'geometry_'+REF})
        gdf.set_geometry('geometry_'+REF)
        if REF=="ROE":
            gdf = gdf.rename({'geometry':'geometry_ROE',"CdObstEcou":"CODE_ROE","NomPrincip":"NOM_ROE","CdEuMasseD":"CODE_ME_maitre"},axis=1)
        if REF =="ME":
            gdf = gdf.rename({'EU_CD':'CODE_ME'},axis=1)
        if REF =="BVG":
            gdf = gdf.rename({'id_bvgesti':'CODE_BVG','nom_bvgest':'nom_BVG'},axis=1)
        if REF =="DEP":
            gdf = gdf.rename({'CODE_DEPT':'CODE_DEP','NOM_DEPT':'NOM_DEP'},axis=1)
            gdf['CODE_DEP'] = gdf['CODE_DEP'].astype(str)
            gdf['NOM_DEP'] = gdf['NOM_DEP'].astype(str)
        if REF =="CE_ME" :
            gdf = gdf.rename({'eu_cd':'CODE_CE_ME','nom_masse_':'NOM_CE_ME'},axis=1) 
            gdf = gdf[['CODE_CE_ME','NOM_CE_ME','longueur_CE_ME','geometry_CE_ME']]  
        self.gdf = gdf

    def _scan_file(self,path):
        get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))
        objs = s3.list_objects_v2(Bucket=bucket_common_files, Prefix=self.path_relative, Delimiter='/') ['Contents']
        date_modif = [obj['LastModified'] for obj in sorted(objs, key=get_last_modified)][0]
        self.date_modif = date_modif

    def __repr__(self):
        return f"repertoire : {self.REF},{self.type_de_geom}"

    def suppression_EPTB_dans_gdf_MO(self):
        if hasattr(self,'df_info'):
            liste_MO_sans_EPTB = self.df_info.loc[self.df_info['TYPE_MO']!="EPTB"]['CODE_MO'].to_list()
            self.gdf = self.gdf.loc[self.gdf['CODE_MO'].isin(liste_MO_sans_EPTB)]
        return self
    
    def export_gdf_pour_geojson(self):
        gdf = self.gdf.to_crs("EPSG:4326")  # Assurez-vous que les coordonnées sont en WGS84
        gdf['geometry_'+self.echelle_REF_shp] = gdf['geometry_'+self.echelle_REF_shp].apply(traitement_gdf_pour_geojson)
        gdf = gdf.rename({"CODE_"+self.echelle_REF_shp:"id"},axis=1)
        gdf = gdf.set_index('id')
        gdf['type_REF'] = self.echelle_REF_shp
        geojson_data = gdf.to_json()
        geojson_data = json.loads(geojson_data)
        return geojson_data
    
    def selection_par_DEP(dict_gdf_REF,type_REF,CODE_DEP,dict_relation):
        CODE_DEP = str(CODE_DEP)
        liste_REF = dict_relation['dict_liste_'+type_REF+"_par_DEP"][CODE_DEP]
        dict_gdf_REF.gdf = dict_gdf_REF.gdf.loc[dict_gdf_REF.gdf['CODE_'+type_REF].isin(liste_REF)]
        bounds = dict_gdf_REF.gdf.to_crs("EPSG:4326").bounds
        bounds['bounds'] = bounds.apply(lambda row: row.tolist(), axis=1)
        bounds['bounds'] = bounds['bounds'].apply(lambda x:[[x[0],x[1]],[x[2],x[3]]])
        bounds = bounds[['bounds']]
        dict_gdf_REF.gdf = pd.merge(dict_gdf_REF.gdf,bounds,left_index=True,right_index=True)
        return dict_gdf_REF 
    

    ####Pour la couche MO
    def ajout_TYPE_MO(dict_gdf_REF):
        dict_gdf_REF.gdf = pd.merge(dict_gdf_REF.gdf,dict_gdf_REF.df_info[['CODE_MO',"TYPE_MO"]],on="CODE_MO")
        return dict_gdf_REF

    def ajout_LISTE_ME(dict_gdf_REF,dict_relation):
        dict_relation_liste_ME_par_MO = dict_relation['dict_liste_ME_par_MO']
        dict_gdf_REF.gdf['liste_CODE_ME'] = dict_gdf_REF.gdf['CODE_MO'].map(dict_relation_liste_ME_par_MO)
        return dict_gdf_REF
    
    def ajout_dict_coordonnes_ME(dict_gdf_REF,dict_decoupREF):
        decoupME_tempo = copy.deepcopy(dict_decoupREF['gdf_decoupME_MO'].gdf)
        decoupME_tempo = decoupME_tempo.to_crs("EPSG:4326")
        decoupME_tempo['coord_centre_ME']=decoupME_tempo.representative_point()
        decoupME_tempo = decoupME_tempo.loc[decoupME_tempo['coord_centre_ME']!=None]
        decoupME_tempo['coord_centre_ME'] = decoupME_tempo['coord_centre_ME'].apply(lambda geom: [geom.x, geom.y])
        decoupME_tempo['dict_CODE_ME_et_coord'] = decoupME_tempo.apply(lambda x:{x['CODE_ME']:x['coord_centre_ME']},axis=1)
        def merge_dicts(dicts):
            # Utilisation de ChainMap pour fusionner plusieurs dictionnaires
            return dict(ChainMap(*dicts))
        decoupME_tempo = decoupME_tempo.groupby('CODE_MO')['dict_CODE_ME_et_coord'].agg(merge_dicts).reset_index()
        dict_gdf_REF.gdf = pd.merge(dict_gdf_REF.gdf,decoupME_tempo,on="CODE_MO")
        return dict_gdf_REF
    
    ####Pour la couche ME
    def ajout_nom_ME_simplifie(dict_gdf_REF):
        dict_gdf_REF.gdf = pd.merge(dict_gdf_REF.gdf,dict_gdf_REF.df_info[['CODE_ME','ALIAS']],on="CODE_ME")
        return dict_gdf_REF

def chercher_gdf_CUSTOM(dict_CUSTOM_maitre,dict_geom_REF,dict_dict_info_REF):
    list_tempo_gdf_CUSTOM = []
    list_date = []
    list_echelle_REF_CUSTOM = list(set([v.echelle_REF for k,v in dict_CUSTOM_maitre.items()]))
    for echelle_REF in list_echelle_REF_CUSTOM:
        gdf_CUSTOM_echelle_REF = dict_geom_REF['gdf_'+echelle_REF].gdf.loc[dict_geom_REF['gdf_'+echelle_REF].gdf['NOM_'+echelle_REF].isin(list(dict_CUSTOM_maitre))]
        dict_renommage = {'NOM_'+echelle_REF:'NOM_CUSTOM','geometry_'+echelle_REF:'geometry_CUSTOM'}
        gdf_CUSTOM_echelle_REF['CODE_CUSTOM'] = gdf_CUSTOM_echelle_REF['CODE_'+echelle_REF]
        gdf_CUSTOM_echelle_REF = gdf_CUSTOM_echelle_REF.rename(dict_renommage,axis=1)
        gdf_CUSTOM_echelle_REF = gdf_CUSTOM_echelle_REF[list(dict_renommage.values()) + ['CODE_CUSTOM','CODE_'+echelle_REF]]
        gdf_CUSTOM_echelle_REF['echelle_REF'] = echelle_REF
        if "ALIAS" in list(dict_dict_info_REF['df_info_'+echelle_REF]):
            df_info_REF = dict_dict_info_REF['df_info_'+echelle_REF].rename({"CODE_"+echelle_REF:"CODE_CUSTOM"},axis=1)
            gdf_CUSTOM_echelle_REF = pd.merge(gdf_CUSTOM_echelle_REF,df_info_REF[['CODE_CUSTOM',"ALIAS"]],on="CODE_CUSTOM",how='left')  
            gdf_CUSTOM_echelle_REF.loc[gdf_CUSTOM_echelle_REF['ALIAS'].isnull(),"ALIAS"] = gdf_CUSTOM_echelle_REF['NOM_CUSTOM'] 
        if "ALIAS" not in list(gdf_CUSTOM_echelle_REF):
            gdf_CUSTOM_echelle_REF["ALIAS"] = gdf_CUSTOM_echelle_REF["NOM_CUSTOM"]
        if len(gdf_CUSTOM_echelle_REF)>0:
            list_tempo_gdf_CUSTOM.append(gdf_CUSTOM_echelle_REF)
            #list_date.append(dict_geom_REF['gdf_'+echelle_REF].date_modif)
    if len(list_tempo_gdf_CUSTOM)>0:
        gdf_REF_total = pd.concat(list_tempo_gdf_CUSTOM)
    if len(list_tempo_gdf_CUSTOM)==0:
        print("Je n'ai pas trouvé d'entité avec les noms suivants dans mes BDD : " + list(dict_CUSTOM_maitre))
        exit()
    gdf_REF_total = gdf_REF_total.reset_index(drop=True)
    gdf_REF = NGdfREF("CUSTOM",path=None,type_geom="polygon")
    gdf_REF.gdf = gdf_REF_total
    #gdf_REF.date_modif = sorted(list_date)[0]
    return gdf_REF

def traitement_gdf_pour_geojson(geometry):
    if geometry.geom_type == 'Polygon':
        return Polygon(list(geometry.exterior.coords))
    elif geometry.geom_type == 'MultiPolygon':
        corrected_polygons = [Polygon(list(p.exterior.coords)) for p in geometry.geoms]
        return MultiPolygon(corrected_polygons)
    else:
        return geometry
    
