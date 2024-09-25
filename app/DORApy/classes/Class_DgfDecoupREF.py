import geopandas as gpd
import pandas as pd
from app.DORApy.classes.modules import connect_path
import copy



class NGdfDecoupREF:
    def __init__(self,REF1,REF2,type_geom,gdf_decoup):
        self.echelle_maitre = REF2
        self.echelle_noob = REF1
        self.colonne_geometry = "geometry_" + REF2
        self.CODE_REF = "CODE_" + REF2
        self.nom_entite_REF = "NOM_" + REF2
        self.type_de_geom = type_geom
        self.gdf = gdf_decoup


def creation_decoupREF(gdf_REF1,gdf_REF2,REF1,REF2,dict_custom_maitre=None):
    couche_REF1 = gdf_REF1.gdf[['CODE_'+REF1,'NOM_'+REF1,'geometry_'+REF1]]
    if gdf_REF2.type_de_geom=="polygon":
        couche_REF2 = gdf_REF2.gdf[['CODE_'+REF2,'NOM_'+REF2,'geometry_'+REF2,'surface_'+REF2]]
    if gdf_REF2.type_de_geom=="lignes":  
        couche_REF2 = gdf_REF2.gdf[['CODE_'+REF2,'NOM_'+REF2,'geometry_'+REF2,'longueur_'+REF2]]  
    if gdf_REF1.type_de_geom =="polygon" and gdf_REF2.type_de_geom =="polygon":
        dict_mapping_CODE_REF1_surface_REF1 = dict(zip(gdf_REF1.gdf['CODE_'+REF1].to_list(),gdf_REF1.gdf.area.to_list()))
        gdf_decoup = gpd.overlay(couche_REF1,couche_REF2, how='intersection',keep_geom_type=False)
        if len(gdf_decoup)>0:
            gdf_decoup['surface_' + REF1] = gdf_REF1.gdf['CODE_'+REF1].map(dict_mapping_CODE_REF1_surface_REF1)
            gdf_decoup['surface_decoup' + REF2] = gdf_decoup['geometry'].area
            gdf_decoup['ratio_surf'] = gdf_decoup['surface_decoup' + REF2]/gdf_decoup['surface_' + REF2]
    if gdf_REF1.type_de_geom =="polygon" and gdf_REF2.type_de_geom =="point":
        gdf_REF1_avec_buffer = copy.deepcopy(couche_REF1)
        if dict_custom_maitre!=None:
            if dict_custom_maitre.type_rendu == "tableau_vierge":
                if REF1=="custom":
                    gdf_REF1_avec_buffer["geometry_"+REF1] = gdf_REF1_avec_buffer["geometry_"+REF1].buffer(1000)
        gdf_decoup = gpd.sjoin(couche_REF2, gdf_REF1_avec_buffer)
        gdf_decoup = gdf_decoup[[x for x in list(gdf_decoup) if x!="geometry"]]
        gdf_decoup = gdf_decoup.rename({"geometry_"+REF2:"geometry"},axis=1)
        if len(gdf_decoup)==0:
            gdf_decoup = pd.DataFrame([])
    if gdf_REF1.type_de_geom =="polygon" and gdf_REF2.type_de_geom =="lignes":
        dict_mapping_CODE_REF1_surface_REF1 = dict(zip(gdf_REF1.gdf['CODE_'+REF1].to_list(),gdf_REF1.gdf.area.to_list()))
        gdf_decoup = gpd.overlay(couche_REF1,couche_REF2, how='intersection',keep_geom_type=False)
        if len(gdf_decoup)>0:
            gdf_decoup['longueur_' + REF1] = gdf_REF1.gdf['CODE_'+REF1].map(dict_mapping_CODE_REF1_surface_REF1)
            gdf_decoup['longueur_decoup' + REF2] = gdf_decoup['geometry'].length
            gdf_decoup['ratio_surf'] = gdf_decoup['longueur_decoup' + REF2]/gdf_decoup['longueur_' + REF2]

    if gdf_REF1.type_de_geom =="point" and gdf_REF2.type_de_geom =="lignes":
        gdf_decoup = pd.DataFrame([])
            
    gdf_decoupREF = NGdfDecoupREF(REF1,REF2,gdf_REF2.type_de_geom,gdf_decoup)
    return gdf_decoupREF

