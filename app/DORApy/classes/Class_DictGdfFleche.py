# -*- coding: utf-8 -*-df_temp_paysage_total
import pandas as pd
import geopandas as gpd

from app.DORApy.classes.Class_DictBoiteComplete import DictBoiteComplete
from shapely.geometry import LineString,Polygon
from shapely.ops import nearest_points


class DictGdfFleche(DictBoiteComplete):
    def __init__(self,dictboitecomplete):
        for key,value in dictboitecomplete.items():
            self[key] = value        
        super().__init__(taille_globale_carto=dictboitecomplete.taille_carto)
        self = dictboitecomplete


    def creation_dict_gdf_fleche_boite_vers_decoupREF(self,dict_decoupREF):
        for nom_entite_custom,contenu_custom in self.items():
            for nom_boite_maitre,dict_boite_maitre in contenu_custom.items():
                if dict_boite_maitre.orientation =="normal":
                    dict_boite_maitre.df_fleche=dict_boite_maitre.df[["CODE_REF",'geometry_point_interception','echelle_REF']]
                    list_df_tempo = []
                    for echelle_REF in dict_boite_maitre.liste_echelle_REF:
                        dict_decoupREF_tempo = dict_decoupREF['gdf_decoup' + echelle_REF + '_custom'].gdf.loc[dict_decoupREF['gdf_decoup' + echelle_REF + '_custom'].gdf['CODE_custom']==contenu_custom.CODE_custom]
                        dict_decoupREF_tempo = dict_decoupREF_tempo.rename({"CODE_"+echelle_REF:"CODE_REF"},axis=1)
                        df_tempo = pd.merge(dict_boite_maitre.df_fleche,dict_decoupREF_tempo,on="CODE_REF")
                        list_df_tempo.append(df_tempo)
                    dict_boite_maitre.df_fleche = pd.concat(list_df_tempo)
                    dict_boite_maitre.df_fleche['point_decoupREF'] = dict_boite_maitre.df_fleche['geometry'].representative_point()
                    dict_boite_maitre.df_fleche['geom_arrow'] = dict_boite_maitre.df_fleche.apply(lambda x: LineString([x['geometry_point_interception'], x['point_decoupREF']]), axis=1)
                    dict_boite_maitre.df_fleche = dict_boite_maitre.df_fleche[["CODE_REF",'geom_arrow','echelle_REF']]
                    dict_boite_maitre.df_fleche = dict_boite_maitre.df_fleche.set_geometry('geom_arrow')
                    dict_boite_maitre.df_fleche = dict_boite_maitre.df_fleche.set_crs('epsg:2154')
        return self

    def ajout_colonne_atlas_pour_export_vers_QGIS_dans_fleche(self,un_projet):
        for nom_entite_custom,contenu_custom in self.items():
            for nom_boite_maitre,dict_boite_maitre in contenu_custom.items():
                if dict_boite_maitre.orientation =="normal":
                    dict_boite_maitre.df_fleche['id_atlas'] = contenu_custom.CODE_custom + '%' + un_projet.type_donnees + '%' + un_projet.thematique + '%' + un_projet.public_cible + '%' + un_projet.info_fond_carte
        return self
    
    def export_fleche(self,un_projet):
        id_projet = un_projet.type_donnees + '_' + un_projet.thematique + '_' + un_projet.public_cible
        for nom_entite_custom,contenu_custom in self.items():
            for type_boite,contenu_boite in contenu_custom.items():
                if contenu_boite.orientation=="normal":
                    contenu_boite.df_fleche = contenu_boite.df_fleche.to_file("/mnt/g/travail/carto/projets basiques/PAOT global 5.0/"+ id_projet +"/couche_fleche/fleche_" + id_projet +".shp",engine="fiona", encoding='utf-8')




