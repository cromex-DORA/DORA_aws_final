import os
import geopandas as gpd
from app.DORApy.classes.Class_NGdfREF import NGdfREF
from app.DORApy.classes.Class_DictDfInfoShp import DictDfInfoShp
from app.DORApy.classes.Class_DgfDecoupREF import creation_decoupREF
from app.DORApy.classes.modules import connect_path
from shapely.geometry import MultiPolygon
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from app.DORApy.classes.modules.connect_path import s3,s3r
import sys
import itertools
import tempfile
import shutil
import pandas as pd
from io import StringIO
from geojson_rewind import rewind
from  geojson import dump
import copy
_default = object()

environment = os.getenv('ENVIRONMENT')
chemin_fichiers_shp = os.getenv('chemin_fichiers_shp')
bucket_common_files = os.getenv('S3_BUCKET_COMMON_FILES')
bucket_back_up = os.getenv('S3_BUCKET_BACK_UP')

class NDictGdf(dict):
    def __init__(self,dict_CUSTOM_maitre=None,liste_echelle_REF=None):
        self.name = "dict_gdf_perso"

    def __repr__(self):
        return f"nom_gdf : {self.name}"
    
    def chercher_gdf(echelle_REF):
        if echelle_REF=="SAGE":
            chemin_fichiers_shp = "shp_files\\SAGE\\SAGE_SUP_2024.gpkg"
            type_geom = "polygon"
        if echelle_REF=="BVG":
            chemin_fichiers_shp = "shp_files\\BVG\\BVG_AG_2022.gpkg"
            type_geom = "polygon"        
        if echelle_REF=="PPG":
            chemin_fichiers_shp = "shp_files\\ppg\\PPG_NA.shp"
            type_geom = "polygon"
        if echelle_REF=="DEP":
            chemin_fichiers_shp = "shp_files\\dep\\departement NAQ + AG.shp"
            type_geom = "polygon"
        if echelle_REF=="ME":
            chemin_fichiers_shp = "shp_files\\ME\\BV_ME_SUP_AG_2022.gpkg"
            type_geom = "polygon"
        if echelle_REF=="SME":
            chemin_fichiers_shp = "shp_files\\SOUS_ME\\SME_DORA_MO.shp"
            type_geom = "polygon"            
        if echelle_REF=="MO":
            chemin_fichiers_shp = "shp_files\\syndicats GEMAPI\\MO_gemapi_NA.gpkg"
            type_geom = "polygon"
        if echelle_REF=="ROE":
            chemin_fichiers_shp = "shp_files\\ROE\\ROE_AG_2023.gpkg"
            type_geom = "point"
        if echelle_REF=="CE_ME":
            chemin_fichiers_shp = "shp_files\\CE_ME\\CE_ME_AG_complet.gpkg"
            type_geom = "lignes" 
        chemin_fichiers_shp = connect_path.get_file_path_racine(chemin_fichiers_shp)
        gdf_REF = NGdfREF(echelle_REF,chemin_fichiers_shp,type_geom)
        gdf_REF.gdf = gdf_REF.gdf.set_geometry("geometry_"+echelle_REF)
        return gdf_REF


    def creer_image_MO_et_PPG(self,CODE_MO):
        self['gdf_MO'] = NGdfREF.suppression_EPTB_dans_gdf_MO(self['gdf_MO'])
        
        liste_PPG_MO = self['gdf_PPG'].df_info.loc[self['gdf_PPG'].df_info['CODE_MO_gemapi']==CODE_MO]['CODE_PPG'].to_list()
        print(CODE_MO,sys.stderr)
        
        gdf = self['gdf_MO'].gdf
        gdf_CE = self['gdf_ME_CE'].gdf
        gdf_zoom = gdf[gdf['CODE_MO'] == CODE_MO]
        print(len(gdf_zoom),sys.stderr)

        # Obtenir les limites de la bounding box de l'élément
        
        minx, miny, maxx, maxy = gdf_zoom.total_bounds

        # Définir une marge autour de l'élément pour le zoom
        margin = 0.1  # 10% de marge
        x_margin = (maxx - minx) * margin
        y_margin = (maxy - miny) * margin

        # Tracer la carte avec zoom
        fig, ax = plt.subplots(figsize=(10, 10))
        gdf.plot(ax=ax, color='none', edgecolor='black', legend=True)
        gdf_CE.plot(ax=ax, color='blue', edgecolor='black')
        gdf_zoom.plot(ax=ax, color='none', edgecolor='red',linewidth=2)
        if len(liste_PPG_MO)>0:
            gdf_PPG_zoom = self['gdf_PPG'].gdf.loc[self['gdf_PPG'].gdf['CODE_PPG'].isin(liste_PPG_MO)]
            gdf_PPG_zoom = gdf_PPG_zoom.buffer(-200)
            gdf_PPG_zoom.plot(ax=ax, color='none', edgecolor='green',linewidth=2)

        legend_elements = [Patch(facecolor='none', edgecolor='red', lw=2, label='MO'),
                        Patch(facecolor='none', edgecolor='green', lw=2, label='PPG')]
        ax.legend(handles=legend_elements)

        # Définir les limites des axes pour le zoom
        ax.set_xlim(minx - x_margin, maxx + x_margin)
        ax.set_ylim(miny - y_margin, maxy + y_margin)

        # Ajouter des éléments supplémentaires (titre, axes, etc.)
        ax.set_title(f'Carte du MO')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

        # Sauvegarder l'image
        output_path = 'map_image.png'
        plt.savefig(output_path, dpi=300)
        plt.show()
        return plt
    
    def back_up_shp(self,type_REF):
    # Liste des objets dans le dossier source
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_common_files, Prefix=self['gdf_'+type_REF].path_folder):
            for obj in page.get('Contents', []):
                source_key = obj['Key']
                # Définir la nouvelle clé de destination en remplaçant le dossier source par celui de destination
                destination_key = source_key.replace(bucket_common_files, self['gdf_'+type_REF].path, 1)
                
                # Copier l'objet
                copy_source = {'Bucket': bucket_common_files, 'Key': source_key}
                s3.copy_object(CopySource=copy_source, Bucket=bucket_back_up, Key=destination_key)
            print(f"Back up du shp {self['gdf_'+type_REF].echelle_REF_shp} effectué dans le s3 back up {destination_key}")

    def actualisation_shp(self,type_REF):
    # Liste des objets dans le dossier source
        temp_dir = tempfile.mkdtemp()

        try:
            # Chemin du fichier shapefile temporaire
            temp_shapefile_path = os.path.join(temp_dir, "essai.gpkg")
            
            # Sauvegarder le GeoDataFrame en tant que shapefile localement
            self['gdf_'+type_REF].gdf.to_file(temp_shapefile_path, driver='GPKG', encoding='utf-8')
            s3.upload_file(temp_shapefile_path, bucket_common_files, "shp_files/syndicats GEMAPI/MO_gemapi_NA.gpkg")
            # Récupérer les fichiers associés (.shp, .shx, .dbf, etc.)
            '''for file_name in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file_name)

                # Upload vers S3
                s3_key = self['gdf_'+type_REF].path_relative
                s3.upload_file(file_path, bucket_common_files, s3_key)
                print(f"Actualisation du "+ s3_key + " dans le s3 "+ bucket_common_files)'''

        finally:
            # Supprimer les fichiers temporaires et le dossier
            shutil.rmtree(temp_dir)
            print(f"Temporary files in {temp_dir} deleted.")

    def actualisation_df_info(dict_geom_REF,REF):
        dict_geom_REF['gdf_'+REF].df_info.to_csv('s3://' + bucket_common_files + '/' + dict_geom_REF['gdf_'+REF].path_folder + '/' + "fichier_info_MO_gemapi.csv", index=False)
       
    def recuperation_gdf_REF(dict_geom_REF,REF):
        dict_gdf_REF =   copy.deepcopy(dict_geom_REF['gdf_'+REF])
        return dict_gdf_REF    
    
    def ajouter_gdf_CUSTOM(gdf_CUSTOM):
        return gdf_CUSTOM
        

    
def remplissage_dictgdf(self,dict_CUSTOM_maitre=None,dict_dict_info_REF=None,liste_echelle_REF=_default,TYPE_REF=None):
    if liste_echelle_REF is _default:
        liste_echelle_REF = ['MO','PPG','ME','SME','BVG','SAGE']
    if liste_echelle_REF is not _default:     
        liste_gdf_deja_presents = [v.echelle_REF_shp for k,v in self.items()]
    
    if dict_CUSTOM_maitre!=None:
        liste_echelle_REF = []
        if hasattr(dict_CUSTOM_maitre,"liste_echelle_shp_CUSTOM_a_check"):
            if TYPE_REF==None:
                liste_echelle_REF.extend(dict_CUSTOM_maitre.liste_echelle_shp_CUSTOM_a_check)
            if TYPE_REF!=None:
                liste_echelle_REF.extend(TYPE_REF)
        if hasattr(dict_CUSTOM_maitre,"liste_echelle_REF_projet"):
            liste_echelle_REF.extend(dict_CUSTOM_maitre.liste_echelle_REF_projet)                
        liste_echelle_REF = list(set(liste_echelle_REF))

    for REF in liste_echelle_REF:
        if REF not in liste_gdf_deja_presents:
            self['gdf_'+REF] = NDictGdf.chercher_gdf(REF)
            if dict_dict_info_REF!=None:
                if 'df_info_'+REF in dict_dict_info_REF:
                    self['gdf_'+REF].df_info = dict_dict_info_REF['df_info_'+REF]
    return self

def creation_NGdfCustom(self,dict_CUSTOM_maitre):
    REF = "CUSTOM"
    self['gdf_CUSTOM'] = NDictGdf({})
    self['gdf_CUSTOM'].gdf = dict_CUSTOM_maitre.gdf_CUSTOM
    self['gdf_CUSTOM'].echelle_REF_shp = REF
    self['gdf_CUSTOM'].nom_entite_REF = "NOM_"+REF
    self['gdf_CUSTOM'].colonne_geometry = 'geometry_'+REF
    self['gdf_CUSTOM'].type_de_geom = 'polygon'
    return self


def creation_dict_decoupREF(self,dict_CUSTOM_maitre=None):
    def ajout_CUSTOM_liste_echelle_REF(self,dict_CUSTOM_maitre):
        if dict_CUSTOM_maitre!=None:
            if hasattr(dict_CUSTOM_maitre,"liste_echelle_REF_projet"):
                liste_echelle_REF_projet = dict_CUSTOM_maitre.liste_echelle_REF_projet + ['CUSTOM']
            if not hasattr(dict_CUSTOM_maitre,"liste_echelle_REF_projet"):
                liste_echelle_REF_projet = [NGdf.echelle_REF_shp for Nom_gdf,NGdf in self.items()]
        if dict_CUSTOM_maitre==None:
            liste_echelle_REF_projet = [NGdf.echelle_REF_shp for Nom_gdf,NGdf in self.items()]
        return liste_echelle_REF_projet
    
    def suppression_CE_ME(liste_combinaison_REF):
        liste_combinaison_REF = [x for x in liste_combinaison_REF if x!="CE_ME"]
        return liste_combinaison_REF

    def hierarchisation_liste_echelle(liste_combinaison_REF):
        list_hierarchie_shp_hydro = ['CUSTOM','DEP','CT','EPTB','SAGE','MO','PPG','BVG','ME','SME','ROE',"CE_ME"]
        dict_hierarchie_hydro = {}
        for numero_hierarchie,echelle_shp in enumerate(list_hierarchie_shp_hydro):
            dict_hierarchie_hydro[echelle_shp] = numero_hierarchie
        dict_tempo_shp = {x:dict_hierarchie_hydro[x] for x in liste_combinaison_REF}
        dict_tempo_shp = dict(sorted(dict_tempo_shp.items(), key=lambda x: x[1], reverse=False))
        liste_combinaison_REF = list(dict_tempo_shp)
        return liste_combinaison_REF

    def decoupage_entite_par_entite(self,liste_combinaison_REF,dict_CUSTOM_maitre=None):
        dict_geomREF_decoupREF = {}
        for [REF1,REF2] in liste_combinaison_REF:
            gdf_REF1 = self['gdf_' + REF1]
            gdf_REF2 = self['gdf_' + REF2]
            dict_geomREF_decoupREF['gdf_decoup' + REF2 +'_' + REF1] = creation_decoupREF(gdf_REF1,gdf_REF2,REF1,REF2,dict_CUSTOM_maitre)
            '''
            if len(dict_geomREF_decoupREF['gdf_decoup' + REF2 +'_' + REF1])>0:
                dict_tempo_pour_copie['gdf_decoup' + REF2 +'_' + REF1] = copy.deepcopy(dict_geomREF_decoupREF['gdf_decoup' + REF2 +'_' + REF1])
                dict_tempo_pour_copie['gdf_decoup' + REF2 +'_' + REF1] = dict_tempo_pour_copie['gdf_decoup' + REF2 +'_' + REF1].set_geometry("geometry")
                dict_tempo_pour_copie['gdf_decoup' + REF2 +'_' + REF1].to_file("D:/projet_DORA/shp_files/decoup_files/decoup" + REF2 + REF1 + ".gpkg", driver='GPKG')'''
        return dict_geomREF_decoupREF

    def regle_tri_dict_decoupREF(self,projet=None):
        def extraire_plus_gros_polygon(multipolygon):
            areas = [i.area for i in multipolygon.geoms]
            max_area = areas.index(max(areas))    
            return multipolygon.geoms[max_area]

        for echelle_shp_par_decoupage,shp_decoupREF in self.items():
            #Regles generales
            if shp_decoupREF.type_de_geom=="polygon":
                REF_entite = echelle_shp_par_decoupage[10:].split("_")[0]
                REF_index = echelle_shp_par_decoupage[10:].split("_")[1]
                #Pour tous projets, Chaque ME ne doit appartenir qu'à un seul BVG
                if REF_entite=='ME' and REF_index=='BVG':
                    shp_decoupREF.gdf = shp_decoupREF.gdf.loc[(shp_decoupREF.gdf['ratio_surf']>0.3)]
                #Pour tous projets, on considère que presque chaque PPG ne doit appartenir qu'à une seule MO
                if REF_entite=='PPG' and REF_index=='MO':
                    shp_decoupREF.gdf = shp_decoupREF.gdf.loc[(shp_decoupREF.gdf['ratio_surf']>0.8)]                   
                if REF_entite=='SME' and REF_index!='MO':
                    if len(shp_decoupREF.gdf)>0:
                    #Highlander ! Il ne doit rester qu'un seul SME par entité
                        shp_decoupREF.gdf.loc[shp_decoupREF.gdf.geom_type=='MultiPolygon','geometry'] = shp_decoupREF.gdf.loc[shp_decoupREF.gdf.geom_type=='MultiPolygon']['geometry'].map(lambda x : extraire_plus_gros_polygon(x))   
                        shp_decoupREF.gdf['CODE_MO_tempo'] = shp_decoupREF.gdf['CODE_SME'].apply(lambda x:x.split("_SME")[0])
                        shp_decoupREF.gdf = shp_decoupREF.gdf.sort_values('ratio_surf',ascending=False).groupby(['CODE_MO_tempo','CODE_'+REF_entite]).first()
                        shp_decoupREF.gdf = shp_decoupREF.gdf.reset_index()
                        shp_decoupREF.gdf = shp_decoupREF.gdf[[x for x in list (shp_decoupREF.gdf) if x!='CODE_MO_tempo']]
            #Regles liées aux projets
            if projet!=None:
                ###Regles de tri uniques pour chaque projets
                if (projet.type_rendu=='tableau' or projet.type_rendu=='carte' or projet.type_rendu=='tableau_DORA_vers_BDD') and (projet.type_donnees=='action' or projet.type_donnees=='toutes_pressions'):
                    #Pour tous projets carto, on ne garde pas les entités qui ont au moins de 5% de la surface dans le final
                    REF_entite = echelle_shp_par_decoupage[10:].split("_")[0]
                    REF_index = echelle_shp_par_decoupage[10:].split("_")[1]
                    if shp_decoupREF.type_de_geom=="polygon":
                        shp_decoupREF.gdf = shp_decoupREF.gdf.loc[(shp_decoupREF.gdf['ratio_surf']>0.2)]                     

                        if REF_entite=='ME' and REF_index=='CUSTOM':
                            shp_decoupREF.gdf = shp_decoupREF.gdf.loc[(shp_decoupREF.gdf['ratio_surf']>0.2)|(shp_decoupREF.gdf['surface_decoup'+REF_entite]>500000)]
                            shp_decoupREF.gdf.loc[shp_decoupREF.gdf.geom_type=='MultiPolygon','geometry'] = shp_decoupREF.gdf.loc[shp_decoupREF.gdf.geom_type=='MultiPolygon']['geometry'].map(lambda x : extraire_plus_gros_polygon(x))

                        if (REF_entite=='ME' or REF_entite=='SME') and REF_index=='CUSTOM':
                            #Pour les PPG par MO, la ration de surface doit étre de 0.1 (Sauf si une action est bien présente sur le CODE_REF !) et on garde que les plus gros polygon
                            shp_decoupREF.gdf = shp_decoupREF.gdf.loc[(shp_decoupREF.gdf['ratio_surf']>0.2)|(shp_decoupREF.gdf['surface_decoup'+REF_entite]>5000000)]
                            shp_decoupREF.gdf.loc[shp_decoupREF.gdf.geom_type=='MultiPolygon','geometry'] = shp_decoupREF.gdf.loc[shp_decoupREF.gdf.geom_type=='MultiPolygon']['geometry'].map(lambda x : extraire_plus_gros_polygon(x))
                        if REF_entite=='PPG' and REF_index=='CUSTOM':
                            #Pour les PPG par MO, la ration de surface doit étre de 0.5 (Sauf si une action est bien présente sur le CODE_REF !) et on garde que les plus gros polygon
                            shp_decoupREF.gdf = shp_decoupREF.gdf.loc[(shp_decoupREF.gdf['ratio_surf']>0.5)|(shp_decoupREF.gdf['surface_decoup'+REF_entite]>20000000)]
                            shp_decoupREF.gdf.loc[shp_decoupREF.gdf.geom_type=='MultiPolygon','geometry'] = shp_decoupREF.gdf.loc[shp_decoupREF.gdf.geom_type=='MultiPolygon']['geometry'].map(lambda x : extraire_plus_gros_polygon(x))

                if (projet.type_rendu=='tableau_vierge') and (projet.type_donnees=='action'):
                    if shp_decoupREF.type_de_geom=="polygon":
                        if len(shp_decoupREF.gdf)>0:
                            shp_decoupREF.gdf = shp_decoupREF.gdf.loc[(shp_decoupREF.gdf['ratio_surf']>0.05)]                     

            if projet==None:
                REF_entite = echelle_shp_par_decoupage[10:].split("_")[0]
                REF_index = echelle_shp_par_decoupage[10:].split("_")[1]
                #Pour les PPG par MO, la ration de surface doit étre de 0.3 et on garde que les plus gros polygon
                if REF_entite=='SAGE' and REF_index=='MO':
                    shp_decoupREF.gdf = shp_decoupREF.gdf.loc[shp_decoupREF.gdf['ratio_surf']>0.9]
                #Pour les PPG par MO, la ration de surface doit étre de 0.3 et on garde que les plus gros polygon
                if REF_entite=='PPG' and REF_index=='CUSTOM':
                    if len(shp_decoupREF.gdf)>0:
                        shp_decoupREF.gdf = shp_decoupREF.gdf.loc[shp_decoupREF.gdf['ratio_surf']>0.3]
                        def extraire_plus_gros_polygon(multipolygon):
                            liste_filtre = [True if(a.area)>5000000 else False for a in multipolygon]
                            multipolygon = list(itertools.compress(multipolygon.geoms, liste_filtre))
                            multipolygon =  MultiPolygon(list(multipolygon))
                            return multipolygon
                        shp_decoupREF.gdf.loc[shp_decoupREF.gdf.geom_type=='MultiPolygon','geometry'] = shp_decoupREF.gdf.loc[shp_decoupREF.gdf.geom_type=='MultiPolygon']['geometry'].map(lambda x : extraire_plus_gros_polygon(x))
                if REF_entite=='ME' and (REF_index=='CUSTOM' or REF_index=='BVG' or REF_index=='PPG'):
                    shp_decoupREF.gdf = shp_decoupREF.gdf.loc[(shp_decoupREF.gdf['ratio_surf']>0.3)|(shp_decoupREF.gdf['surface_decoup'+REF_entite]>50000000)]
        return self

    def suppression_CODE_REF_vide(self):
        for echelle_shp_par_decoupage,shp_decoupREF in self.items():
            if len(shp_decoupREF.gdf)>0:
                REF_entite = shp_decoupREF.echelle_maitre
                REF_index = shp_decoupREF.echelle_noob
                shp_decoupREF.gdf = shp_decoupREF.gdf.loc[~shp_decoupREF.gdf["CODE_"+REF_entite].isnull()]
                shp_decoupREF.gdf = shp_decoupREF.gdf.loc[~shp_decoupREF.gdf["CODE_"+REF_index].isnull()]
        return self
    
    liste_echelle_REF_projet = ajout_CUSTOM_liste_echelle_REF(self,dict_CUSTOM_maitre)
    #liste_combinaison_REF = suppression_CE_ME(liste_echelle_REF_projet)
    liste_combinaison_REF = hierarchisation_liste_echelle(liste_echelle_REF_projet)
    liste_combinaison_REF = list(itertools.combinations(liste_combinaison_REF, 2))
    liste_combinaison_REF = [list(x) for x in liste_combinaison_REF]
    dict_geomREF_decoupREF = decoupage_entite_par_entite(self,liste_combinaison_REF,dict_CUSTOM_maitre)
    dict_geomREF_decoupREF = regle_tri_dict_decoupREF(dict_geomREF_decoupREF,dict_CUSTOM_maitre)
    #dict_geomREF_decoupREF = dictGdfCompletREF.suppression_entite_hors_des_CUSTOM(dict_geomREF_decoupREF,dict_CUSTOM_maitre)
    dict_geomREF_decoupREF = suppression_CODE_REF_vide(dict_geomREF_decoupREF)
    return dict_geomREF_decoupREF

def extraction_dict_relation_shp_liste_a_partir_decoupREF(dict_CUSTOM_maitre=None,dict_decoupREF=None):
    class DictListeREFparREF(dict):
        def __init__(self, *args, **kwargs):
            super(DictListeREFparREF, self).__init__(*args, **kwargs)
            self.name = "dict_simple_relation"


    class DictRelationListeREFparREF(dict):
        def __getitem__(self, key):
            print(key, file=sys.stderr)
            if key not in self:

                REF1 = key.split("_")[2]
                REF2 = key.split("_")[4]
                if "dict_liste_" + REF1 + "_par_" + REF2:
                    self[key] = self.create_key(key)
            return super().__getitem__(key)
        
        def create_key(self,key):
            REF1 = key.split("_")[2]
            REF2 = key.split("_")[4]

            dict_temporaire_inverse = DictListeREFparREF({})
            
            try:
                for k, v in self['dict_liste_' + REF2 + '_par_' + REF1].items():
                    for x in v:
                        dict_temporaire_inverse.setdefault(x, []).append(k)
            except KeyError:
                print(f"Clé manquante pour 'dict_liste_{REF2}_par_{REF1}'", file=sys.stderr)
                raise

            dict_temporaire_inverse.REF_maitre = REF1
            dict_temporaire_inverse.REF_noob = REF2
            return dict_temporaire_inverse

    dict_relation_shp_liste = DictRelationListeREFparREF({})
    
    for echelle_shp_par_decoupage,shp_decoupREF in dict_decoupREF.items():
        REF1 = shp_decoupREF.echelle_maitre
        REF2 = shp_decoupREF.echelle_noob
        df_decoupREF_REF = shp_decoupREF.gdf.groupby('CODE_'+REF2).agg({'CODE_'+REF1:lambda x: list(x)})
        df_decoupREF_REF.columns = ['liste_' + REF1 +'_par_' + REF2]
        dict_relation_shp_liste['dict_liste_' + REF1 +'_par_' + REF2] = DictListeREFparREF(df_decoupREF_REF.to_dict()['liste_' + REF1 +'_par_' + REF2])
        dict_relation_shp_liste['dict_liste_' + REF1 +'_par_' + REF2].REF_maitre = REF2
        dict_relation_shp_liste['dict_liste_' + REF1 +'_par_' + REF2].REF_noob = REF1

    if dict_CUSTOM_maitre!=None:
        list_CODE_CUSTOM = [v.CODE_CUSTOM for k,v in dict_CUSTOM_maitre.items()]
    for nom_dict_relation,dict_relation_REF1_REF2 in dict_relation_shp_liste.items():
        if nom_dict_relation.endswith("CUSTOM"):
            for CODE_CUSTOM in list_CODE_CUSTOM:
                if CODE_CUSTOM not in dict_relation_REF1_REF2:
                    dict_relation_REF1_REF2[CODE_CUSTOM] = []
    return dict_relation_shp_liste

def generation_geojson_sur_s3(self):
    def creation_geojson_REF_s3(REF):
        temp_dir = tempfile.mkdtemp()
        temp_shapefile_path = os.path.join(temp_dir, "fichier_tempo.geojson")
        geojson_file=dict_gdf.export_gdf_pour_geojson()
        essai=rewind(geojson_file)

        with open(temp_shapefile_path, 'w') as f:
            dump(essai, f)
        # Chemin du fichier shapefile temporaire
        destination_fichier = os.path.join(dict_gdf.path_folder, REF+".geojson")
        s3r.meta.client.upload_file(temp_shapefile_path, bucket_common_files, destination_fichier) 

        shutil.rmtree(temp_dir)
        print(f"Temporary files in {temp_dir} deleted.")    

    for nom_gdf,dict_gdf in self.items():
        REF = dict_gdf.echelle_REF_shp
        list_noms_fichiers = connect_path.lister_exclu_fichiers_folder_s3(bucket_common_files,dict_gdf.path_folder)
        if REF + ".geojson" not in list_noms_fichiers:
            creation_geojson_REF_s3(REF)
            #creation
        if REF + ".geojson" in list_noms_fichiers:
            #Recuperation csv avec date
            if "metadata_" + REF + ".csv" not in list_noms_fichiers:
                path_csv = os.path.join(dict_gdf.path_folder,"metadata_" + REF + ".csv")
                dict_date = {'nom_fichier': [dict_gdf.name], 'date': [dict_gdf.date_modif]}
                df_date = pd.DataFrame(data=dict_date)
                csv_buffer = StringIO()
                df_date.to_csv(csv_buffer)
                s3r.Object(bucket_common_files, path_csv).put(Body=csv_buffer.getvalue())     

            if "metadata_" + REF + ".csv" in list_noms_fichiers:
                date_modif_gpkg = dict_gdf.date_modif
                path_csv = os.path.join(dict_gdf.path_folder,"metadata_" + REF + ".csv")
                obj = s3.get_object(Bucket=bucket_common_files, Key=path_csv)
                df_date = pd.read_csv(obj['Body'])
                #comparaison date
                date = df_date['date'].to_list()[0]
                date_format = date_modif_gpkg.strftime('%Y-%m-%d %H:%M:%S+00:00')
                if date!=date_format:
                    creation_geojson_REF_s3(REF)
                    df_date.loc[0,"date"] = date_format
                    csv_buffer = StringIO()
                    df_date.to_csv(csv_buffer)
                    s3r.Object(bucket_common_files, path_csv).put(Body=csv_buffer.getvalue())
                    #Actualisation de la date
                
     


 