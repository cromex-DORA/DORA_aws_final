# -*- coding: utf-8 -*-
import pandas as pd
import geopandas as gpd
from operator import itemgetter
from app.DORApy.classes.Class_DictBoiteComplete import DictBoiteComplete
from shapely.geometry import LineString,Polygon
from shapely.ops import nearest_points

from app.DORApy.classes.modules import texte,CUSTOM,PPG,dataframe
from app.DORApy.classes.modules import config_DORA
dict_config_espace,dict_config_police = config_DORA.creation_dicts_config()
surface_limite = dict_config_espace['surface_limite']['petite']
f_b = 2

class DictCUSTOM(dict):
    @property
    def _constructor(self):
        return DictCUSTOM

class DictBVCUSTOM(dict):
    @property
    def _constructor(self):
        return DictBVCUSTOM

class listMEpartie(list):
    @property
    def _constructor(self):
        return listMEpartie

class DictGroupeMECUSTOM(dict):
    @property
    def _constructor(self):
        return DictGroupeMECUSTOM

    def creation_key_CUSTOM(self,dict_relation_shp_liste):
        for CODE_CUSTOM in dict_relation_shp_liste:
            self[CODE_CUSTOM] = DictCUSTOM({})
        return self

    def attribution_list_ME(self,dict_relation_shp_liste):
        for CODE_CUSTOM in self:
            self[CODE_CUSTOM].list_ME = dict_relation_shp_liste[CODE_CUSTOM]['dict_liste_ME_par_CUSTOM']
        return self

    def creation_dict_liste_ME_voisin(self,dict_decoupREF):
        dict_liste_ME_voisin = {}
        for CODE_CUSTOM in self:
            dict_liste_ME_voisin[CODE_CUSTOM] = dict(zip(dict_decoupREF[CODE_CUSTOM]['gdf_decoupME_CUSTOM']['CODE_ME'].to_list(),dict_decoupREF[CODE_CUSTOM]['gdf_decoupME_CUSTOM']['liste_CODE_ME_voisin'].to_list()))
        return dict_liste_ME_voisin

    def decoupage_groupe_ME(self,dict_liste_ME_voisin,dict_rg_Strahler,dict_chainage_list_amont):
        dict_chainage_par_CODE_ME = {}
        for CODE_CUSTOM in self:
            dict_chainage_par_CODE_ME[CODE_CUSTOM] = {}
            liste_ME_a_traiter = self[CODE_CUSTOM].list_ME
            liste_CODE_ME_str = [[a,dict_rg_Strahler[a.split('$')[0]]] for a in liste_ME_a_traiter]
            liste_CODE_ME_str = sorted(liste_CODE_ME_str, key=itemgetter(1), reverse=True)
            diff_max_rg_Shtraler = int(liste_CODE_ME_str[0][1] - liste_CODE_ME_str[-1][1])+1

            while len(liste_ME_a_traiter)>0:
                CODE_ME_min_str = [[a,dict_rg_Strahler[a.split('$')[0]]] for a in liste_ME_a_traiter]
                CODE_ME_min_str = sorted(CODE_ME_min_str, key=itemgetter(1))[0][0]
                self[CODE_CUSTOM][CODE_ME_min_str] = DictBVCUSTOM({})
                self[CODE_CUSTOM][CODE_ME_min_str]["rg_str_0"] = [CODE_ME_min_str]
                dict_chainage_par_CODE_ME[CODE_CUSTOM][CODE_ME_min_str] = {}

                for num_str in range(1,diff_max_rg_Shtraler+1):
                    self[CODE_CUSTOM][CODE_ME_min_str]["rg_str_" + str(num_str)] = []
                    for CODE_ME_aval in self[CODE_CUSTOM][CODE_ME_min_str]["rg_str_" + str(num_str-1)]:
                        #filtre ME voisines et amont
                        liste_ME_a_ajouter = [x for x in dict_liste_ME_voisin[CODE_CUSTOM][CODE_ME_aval] if x.split("$")[0] in dict_chainage_list_amont[CODE_ME_aval.split("$")[0]]]
                        liste_ME_a_ajouter = [x for x in liste_ME_a_ajouter if x in liste_ME_a_traiter]
                        dict_chainage_par_CODE_ME[CODE_CUSTOM][CODE_ME_min_str][CODE_ME_aval] = liste_ME_a_ajouter
                        self[CODE_CUSTOM][CODE_ME_min_str]["rg_str_" + str(num_str)].append(liste_ME_a_ajouter)
                    self[CODE_CUSTOM][CODE_ME_min_str]["rg_str_" + str(num_str)] = [item for sublist in self[CODE_CUSTOM][CODE_ME_min_str]["rg_str_" + str(num_str)] for item in sublist]
                    if len(self[CODE_CUSTOM][CODE_ME_min_str]["rg_str_" + str(num_str)])==0:
                        self[CODE_CUSTOM][CODE_ME_min_str] = DictBVCUSTOM({k:v for k,v in self[CODE_CUSTOM][CODE_ME_min_str].items() if len(v)!=0})
                        self[CODE_CUSTOM][CODE_ME_min_str].list_ME = [item for sublist in list(self[CODE_CUSTOM][CODE_ME_min_str].values()) for item in sublist]
                        liste_ME_a_traiter = [x for x in liste_ME_a_traiter if x not in self[CODE_CUSTOM][CODE_ME_min_str].list_ME]
                        break
        return self,dict_chainage_par_CODE_ME

    def attribution_surface_totale(self,dict_surface_decoupME_par_CUSTOM):
        for CODE_CUSTOM,dict_groupe_ME in self.items():
            for CODE_ME_la_plus_aval,dict_CODE_ME_aval in dict_groupe_ME.items():
                self[CODE_CUSTOM][CODE_ME_la_plus_aval].surface_totale = int(sum([dict_surface_decoupME_par_CUSTOM[CODE_CUSTOM][x] for x in dict_CODE_ME_aval.list_ME]))
        return self



    def attribution_liste_chainage(self,dict_chainage_par_CODE_ME,dict_decoupREF):
        def recherche_cle_par_valeur_dans_liste(dictionary, keyword):
            for key, values in dictionary.items():
                if keyword in values:
                    return key

        for CODE_CUSTOM,dict_groupe_ME in self.items():
            for nom_groupe_ME,dict_rg_str in dict_groupe_ME.items():
                list_CODE_ME_max_str = self[CODE_CUSTOM][nom_groupe_ME][(list(self[CODE_CUSTOM][nom_groupe_ME])[-1])]
                list_CODE_ME_max_str = [x for x in list_CODE_ME_max_str]
                list_CODE_ME_max_str = list_CODE_ME_max_str + [nom_groupe_ME]
                df_decoup_REF = dict_decoupREF[CODE_CUSTOM]['gdf_decoupME_CUSTOM']
                df_decoup_REF_max_str = df_decoup_REF.loc[df_decoup_REF['CODE_ME'].isin(list_CODE_ME_max_str)]
                df_decoup_REF_max_str = df_decoup_REF_max_str.set_index('CODE_ME')
                df_max_distance = df_decoup_REF_max_str.geometry.representative_point().apply(lambda g: df_decoup_REF_max_str.representative_point().distance(g))
                df_max_distance = df_max_distance.idxmax(axis=1)
                CODE_ME_max_dist_str = df_max_distance.loc[nom_groupe_ME]
                list_ME_chainage = [CODE_ME_max_dist_str]
                CODE_ME_aval_direct = CODE_ME_max_dist_str
                if recherche_cle_par_valeur_dans_liste(dict_chainage_par_CODE_ME[CODE_CUSTOM][nom_groupe_ME],CODE_ME_aval_direct)!=None:
                    while(recherche_cle_par_valeur_dans_liste(dict_chainage_par_CODE_ME[CODE_CUSTOM][nom_groupe_ME],CODE_ME_aval_direct)!=nom_groupe_ME):
                        CODE_ME_aval_direct = recherche_cle_par_valeur_dans_liste(dict_chainage_par_CODE_ME[CODE_CUSTOM][nom_groupe_ME],CODE_ME_aval_direct)
                        list_ME_chainage.append(CODE_ME_aval_direct)
                list_ME_chainage.append(nom_groupe_ME)
                dict_groupe_ME[nom_groupe_ME].list_ME_chainage = list_ME_chainage
                dict_groupe_ME[nom_groupe_ME].CODE_ME_max_dist_str = int(list(self[CODE_CUSTOM][nom_groupe_ME])[-1].split("_")[-1])
        return self

    def creation_liste_groupe_surface(self):
        for CODE_CUSTOM,dict_groupe_ME in self.items():
            for nom_groupe_ME,dict_rg_str in dict_groupe_ME.items():
                if dict_groupe_ME[nom_groupe_ME].surface_totale < surface_limite/f_b:
                    dict_groupe_ME[nom_groupe_ME].categorie = "noob"
                if dict_groupe_ME[nom_groupe_ME].surface_totale >= surface_limite/f_b:
                    dict_groupe_ME[nom_groupe_ME].categorie = "maitre"
        return self

    def attribut_maitre_pour_un_groupe_ME_minimum(self):
        return self

    def attribution_list_groupe_ME_et_ME(self):
        for CODE_CUSTOM,dict_groupe_ME in self.items():
            self[CODE_CUSTOM].list_groupe_ME_maitre = []
            self[CODE_CUSTOM].list_groupe_ME_noob = []
            for nom_groupe_ME,dict_rg_str in dict_groupe_ME.items():
                if dict_groupe_ME[nom_groupe_ME].categorie == "noob":
                    self[CODE_CUSTOM].list_groupe_ME_noob.append(nom_groupe_ME)
                if dict_groupe_ME[nom_groupe_ME].categorie == "maitre":
                    self[CODE_CUSTOM].list_groupe_ME_maitre.append(nom_groupe_ME)
        for CODE_CUSTOM,dict_groupe_ME in self.items():
            list_list_ME_maitre = [dict_groupe_ME[x].list_ME for x in dict_groupe_ME.list_groupe_ME_maitre]
            list_ME_maitre = [item for sublist in list_list_ME_maitre for item in sublist]
            dict_groupe_ME.list_ME_maitre = list_ME_maitre
        return self

    def attribution_ME_noob_pour_ME_maitre(self,dict_decoupREF):
        for CODE_CUSTOM,dict_groupe_ME in self.items():
            for nom_groupe_ME,dict_rg_str in dict_groupe_ME.items():
                dict_decoup = dict_decoupREF[CODE_CUSTOM]['gdf_decoupME_CUSTOM']
                gdf_geometry_tempo = dict_decoup.loc[dict_decoup['CODE_ME'].isin(dict_groupe_ME[nom_groupe_ME].list_ME)]
                gdf_geometry_tempo = gdf_geometry_tempo.set_geometry('geometry')
                gdf_geometry_tempo = gdf_geometry_tempo.dissolve()
                dict_groupe_ME[nom_groupe_ME].geometry_totale = gdf_geometry_tempo
        for CODE_CUSTOM,dict_groupe_ME in self.items():
            liste_groupe_ME_noob= []
            liste_nom_groupe_ME_noob = []
            dict_decoup = dict_decoupREF[CODE_CUSTOM]['gdf_decoupME_CUSTOM']
            for nom_groupe_ME,dict_NOM_ME in dict_groupe_ME.items():
                if dict_NOM_ME.categorie == "noob":
                    liste_groupe_ME_noob.append(dict_groupe_ME[nom_groupe_ME].geometry_totale)
                    liste_nom_groupe_ME_noob.append(nom_groupe_ME)

            list_ME_maitre = [x for x in dict_groupe_ME.list_ME_maitre]
            gdf_list_ME_maitre = dict_decoup.loc[dict_decoup["CODE_ME"].isin(list_ME_maitre)]
            gdf_list_ME_maitre = gdf_list_ME_maitre.rename({"CODE_ME":"NOM_GROUPE_ME"},axis=1)
            gdf_list_ME_maitre = gdf_list_ME_maitre.set_index('NOM_GROUPE_ME')

            if len(liste_groupe_ME_noob)>0:
                gdf_ME_groupe_ME_noob = pd.concat(liste_groupe_ME_noob)
                gdf_ME_groupe_ME_noob = gdf_ME_groupe_ME_noob.rename({"CODE_ME":"NOM_GROUPE_ME"},axis=1)
                gdf_ME_groupe_ME_noob = gdf_ME_groupe_ME_noob.set_index('NOM_GROUPE_ME')
                gdf_ME_maitre_et_groupe_ME_noob = pd.concat([gdf_ME_groupe_ME_noob,gdf_list_ME_maitre])
            if len(liste_groupe_ME_noob)==0:
                gdf_ME_maitre_et_groupe_ME_noob = gdf_list_ME_maitre

            gdf_ME_maitre_et_groupe_ME_noob_buffer = gdf_ME_maitre_et_groupe_ME_noob.buffer(50)
            gdf_ME_maitre_et_groupe_ME_noob_buffer = gpd.GeoDataFrame(geometry=gpd.GeoSeries(gdf_ME_maitre_et_groupe_ME_noob_buffer))
            gdf_ME_maitre_et_groupe_ME_noob_buffer['groupe_ME'] = gdf_ME_maitre_et_groupe_ME_noob_buffer.index

            list_geometry_ME_maitre_et_groupe_ME_noob = gdf_ME_maitre_et_groupe_ME_noob['geometry'].to_list()
            list_NOM_ME_maitre_et_groupe_ME_noob = gdf_ME_maitre_et_groupe_ME_noob.index.to_list()

            list_groupe_ME_a_traiter = gdf_ME_maitre_et_groupe_ME_noob.index.to_list()
            list_groupe_ME_a_traiter = [x for x in list_groupe_ME_a_traiter if x not in list_ME_maitre]

            list_groupe_ME_ou_ME_a_rattacher = [x for x in list_ME_maitre]
            dict_nom_GROUPE_ME_ME_MAITRE = {k:str for k in liste_nom_groupe_ME_noob}

            dict_nom_ME_geometry = dict(zip(list_NOM_ME_maitre_et_groupe_ME_noob,list_geometry_ME_maitre_et_groupe_ME_noob))
            while len(list_groupe_ME_a_traiter)>0:
                list_tempo_groupe_ME_traited = []
                for nom_geometry,geometry_groupe_ME_ou_ME in dict_nom_ME_geometry.items():
                    if nom_geometry in list_groupe_ME_a_traiter:
                        df_inter = gdf_ME_maitre_et_groupe_ME_noob_buffer.intersection(geometry_groupe_ME_ou_ME)
                        df_inter = df_inter[~df_inter.is_empty]

                        if len(df_inter)>1:
                            gdf_inter = gpd.GeoDataFrame(df_inter)
                            gdf_inter = gdf_inter.rename(columns ={gdf_inter.columns[0]:'geometry'})
                            gdf_inter = gdf_inter.set_geometry('geometry')
                            gdf_inter['surface_com'] = gdf_inter.area
                            gdf_inter = gdf_inter.sort_values('surface_com',ascending=False)
                            gdf_inter = gdf_inter.iloc[1:]
                            gdf_inter = gdf_inter.loc[[x for x in list(gdf_inter.index.values) if x in list_groupe_ME_ou_ME_a_rattacher]]
                            if len(gdf_inter)>0:
                                dict_nom_GROUPE_ME_ME_MAITRE[nom_geometry] = gdf_inter.iloc[0].name
                                list_tempo_groupe_ME_traited.append(nom_geometry)
                list_groupe_ME_ou_ME_a_rattacher.extend(list_tempo_groupe_ME_traited)
                list_groupe_ME_a_traiter = [x for x in list_groupe_ME_a_traiter if x not in list_tempo_groupe_ME_traited]

            while not set(dict_nom_GROUPE_ME_ME_MAITRE.values()).issubset(list_ME_maitre):
                for entite_maitre,entite_noob in dict_nom_GROUPE_ME_ME_MAITRE.items():
                    if entite_noob in list(dict_nom_GROUPE_ME_ME_MAITRE):
                        dict_nom_GROUPE_ME_ME_MAITRE[entite_maitre] = dict_nom_GROUPE_ME_ME_MAITRE[entite_noob]

            for nom_groupe_ME,dict_NOM_ME in dict_groupe_ME.items():
                if nom_groupe_ME in dict_nom_GROUPE_ME_ME_MAITRE:
                    dict_NOM_ME.NOM_ME_MAITRE = dict_nom_GROUPE_ME_ME_MAITRE[nom_groupe_ME]

            dict_ME_Maitre_GROUPE_ME_NOOB = {}
            for k,v in dict_nom_GROUPE_ME_ME_MAITRE.items():
                dict_ME_Maitre_GROUPE_ME_NOOB.setdefault(v, []).append(k)
            for CODE_ME_maitre in dict_groupe_ME.list_ME_maitre:
                if CODE_ME_maitre not in dict_ME_Maitre_GROUPE_ME_NOOB:
                    dict_ME_Maitre_GROUPE_ME_NOOB[CODE_ME_maitre] = []
            for NOM_ME_MAITRE,list_GROUPE_ME_noob in dict_ME_Maitre_GROUPE_ME_NOOB.items():
                dict_ME_Maitre_GROUPE_ME_NOOB[NOM_ME_MAITRE] = [dict_groupe_ME[x].list_ME for x in list_GROUPE_ME_noob]
                dict_ME_Maitre_GROUPE_ME_NOOB[NOM_ME_MAITRE] = [item for sublist in dict_ME_Maitre_GROUPE_ME_NOOB[NOM_ME_MAITRE] for item in sublist]
            dict_groupe_ME.dict_list_groupe_ME_noob_a_recuperer = dict_ME_Maitre_GROUPE_ME_NOOB

        return self

    def actualisation_list_ME_par_groupe_ME(dict_list_groupe_ME_par_CUSTOM):
        for CODE_CUSTOM,dict_groupe_ME in dict_list_groupe_ME_par_CUSTOM.items():
            for nom_groupe_ME,dict_NOM_ME in dict_groupe_ME.items():
                for CODE_ME in dict_NOM_ME.list_ME:
                    if CODE_ME in dict_groupe_ME.dict_list_groupe_ME_noob_a_recuperer:
                        dict_NOM_ME.list_ME.extend(dict_groupe_ME.dict_list_groupe_ME_noob_a_recuperer[CODE_ME])
        return dict_list_groupe_ME_par_CUSTOM

    def descente_decoupage_GROUPE_ME_MAITRE(self,dict_chainage_par_CODE_ME,dict_surface_decoupME_par_CUSTOM,dict_decoupREF):
        class NiveauListe(list):
            @property
            def _constructor(self):
                return NiveauListe

        def deroulage_amont_integral(liste_CODE_ME,dict_chainage_par_CODE_ME,CODE_CUSTOM,CODE_ME_MAITRE):
            liste_ME_total = liste_CODE_ME
            liste_CODE_ME_a_ajouter = liste_ME_total
            if liste_ME_total!=[]:
                while any(dict_chainage_par_CODE_ME[CODE_CUSTOM][CODE_ME_MAITRE][CODE_ME]!=[] for CODE_ME in liste_CODE_ME_a_ajouter):
                    liste_CODE_ME_a_ajouter = [dict_chainage_par_CODE_ME[CODE_CUSTOM][CODE_ME_MAITRE][x] for x in liste_CODE_ME_a_ajouter]
                    liste_CODE_ME_a_ajouter = [item for sublist in liste_CODE_ME_a_ajouter for item in sublist]
                    liste_ME_total.extend(liste_CODE_ME_a_ajouter)
            return liste_ME_total

        def ajout_ME_noob(list_ME,dict_list_ME_noob_a_recup):
            for CODE_ME in list_ME:
                if CODE_ME in dict_list_ME_noob_a_recup:
                    list_ME.extend(dict_list_ME_noob_a_recup[CODE_ME])
            return list_ME

        def obtenir_liste_ME_amont_direct_sans_chainage(CODE_ME,CODE_CUSTOM,dict_chainage_par_CODE_ME,list_ME_chainage):
            liste_ME_amont_direct_sans_chainage = dict_chainage_par_CODE_ME[CODE_CUSTOM][list_ME_chainage[-1]][CODE_ME]
            for CODE_ME_liste in liste_ME_amont_direct_sans_chainage:
                if CODE_ME_liste in list_ME_chainage:
                    if CODE_ME_liste not in list_ME_chainage[list_ME_chainage.index(CODE_ME):]:
                        liste_ME_amont_direct_sans_chainage.remove(CODE_ME_liste)
            return liste_ME_amont_direct_sans_chainage

        def calcul_surface_a_partir_list_ME(liste_ME,CODE_CUSTOM):
            surface_ajout = int(sum([dict_surface_decoupME_par_CUSTOM[CODE_CUSTOM][x] for x in liste_ME]))
            return surface_ajout

        def tri_list_ME_par_surface(liste_ME,CODE_CUSTOM):
            dict_tempo_surface = {k:[] for k in liste_ME}
            for CODE_ME in dict_tempo_surface:
                dict_tempo_surface[CODE_ME] = deroulage_amont_integral([CODE_ME],dict_chainage_par_CODE_ME,CODE_CUSTOM,list_ME_chainage[-1])
                dict_tempo_surface[CODE_ME] = calcul_surface_a_partir_list_ME(dict_tempo_surface[CODE_ME],CODE_CUSTOM)
            list_ME_triee = sorted(liste_ME, key=lambda x: dict_tempo_surface[x], reverse=True)
            return list_ME_triee

        def suppression_des_ME(dict_tempo_memoire_sous_list_ME,liste_ME_a_enlever,CODE_CUSTOM):
            dict_tempo_memoire_sous_list_ME[CODE_CUSTOM].liste_ME_restante = [x for x in dict_tempo_memoire_sous_list_ME[CODE_CUSTOM].liste_ME_restante if x not in liste_ME_a_enlever]
            return dict_tempo_memoire_sous_list_ME

        def diminution_surface(dict_tempo_memoire_sous_list_ME,surface_a_enlever,CODE_CUSTOM):
            dict_tempo_memoire_sous_list_ME[CODE_CUSTOM].surface_restante = dict_tempo_memoire_sous_list_ME[CODE_CUSTOM].surface_restante-surface_a_enlever
            return dict_tempo_memoire_sous_list_ME


        dict_decoupCUSTOM = {}
        for CODE_CUSTOM,dict_groupe_ME in self.items():
            dict_decoupCUSTOM[CODE_CUSTOM] = {}
            dict_list_ME_noob_a_recup = self[CODE_CUSTOM].dict_list_groupe_ME_noob_a_recuperer
            for nom_groupe_ME,dict_NOM_ME in dict_groupe_ME.items():
                if nom_groupe_ME in self[CODE_CUSTOM].list_groupe_ME_maitre:
                    nom_partie_actuel = dict_NOM_ME.CODE_ME_max_dist_str
                    list_ME_chainage = dict_NOM_ME.list_ME_chainage
                    liste_ME_chainage_original = [x for x in list_ME_chainage]
                    liste_ME_restante = [x for x in dict_NOM_ME.list_ME]
                    dict_tempo_memoire_sous_list_ME = {}
                    #Initialisation
                    dict_tempo_memoire_sous_list_ME[CODE_CUSTOM] = NiveauListe(list_ME_chainage[1:])
                    dict_tempo_memoire_sous_list_ME[CODE_CUSTOM].niveau = 0
                    dict_tempo_memoire_sous_list_ME[CODE_CUSTOM].liste_ME_restante = [x for x in liste_ME_restante if x!=list_ME_chainage[0]]
                    dict_tempo_memoire_sous_list_ME[CODE_CUSTOM].surface_restante = dict_NOM_ME.surface_totale-calcul_surface_a_partir_list_ME([list_ME_chainage[0]],CODE_CUSTOM)
                    niveau_actuel = 0

                    dict_decoupCUSTOM[CODE_CUSTOM]["partie_" + list_ME_chainage[0]] = listMEpartie([list_ME_chainage[0]])
                    dict_decoupCUSTOM[CODE_CUSTOM]["partie_" + list_ME_chainage[0]].extend(dict_list_ME_noob_a_recup[list_ME_chainage[0]])
                    dict_decoupCUSTOM[CODE_CUSTOM]["partie_" + list_ME_chainage[0]].surface_total = calcul_surface_a_partir_list_ME([list_ME_chainage[0]],CODE_CUSTOM)
                    dict_decoupCUSTOM[CODE_CUSTOM]["partie_" + list_ME_chainage[0]].niveau = 1

                    CODE_ME_partie_a_remplir = nom_partie_actuel
                    surface_partie_a_remplir = 0
                    while(len(dict_tempo_memoire_sous_list_ME[CODE_CUSTOM].liste_ME_restante)>0):
                        if len(dict_tempo_memoire_sous_list_ME[CODE_CUSTOM].liste_ME_restante)<15:
                            print("cocou")
                        niveau_actuel = 1
                        CODE_ME_chainage = dict_tempo_memoire_sous_list_ME[CODE_CUSTOM][0]
                        liste_ME_AMONT_sans_chainage = obtenir_liste_ME_amont_direct_sans_chainage(CODE_ME_chainage,CODE_CUSTOM,dict_chainage_par_CODE_ME,liste_ME_chainage_original)
                        liste_ME_AMONT_sans_chainage = tri_list_ME_par_surface(liste_ME_AMONT_sans_chainage,CODE_CUSTOM)
                        liste_ME_total_sans_chainage = deroulage_amont_integral(liste_ME_AMONT_sans_chainage,dict_chainage_par_CODE_ME,CODE_CUSTOM,list_ME_chainage[-1])
                        liste_ME_total_sans_chainage.extend([CODE_ME_chainage])
                        liste_ME_total_sans_chainage = ajout_ME_noob(liste_ME_total_sans_chainage,dict_list_ME_noob_a_recup)
                        liste_ME_total_sans_chainage = [x for x in liste_ME_total_sans_chainage if x in dict_tempo_memoire_sous_list_ME[CODE_CUSTOM].liste_ME_restante]
                        dict_tempo_memoire_sous_list_ME[CODE_ME_chainage] = NiveauListe(liste_ME_total_sans_chainage)
                        dict_tempo_memoire_sous_list_ME[CODE_ME_chainage].niveau = niveau_actuel
                        dict_tempo_memoire_sous_list_ME[CODE_ME_chainage].surface_restante = calcul_surface_a_partir_list_ME(liste_ME_total_sans_chainage,CODE_CUSTOM)
                        while len(liste_ME_AMONT_sans_chainage)>0:
                            CODE_ME = liste_ME_AMONT_sans_chainage[0]
                            niveau_actuel = niveau_actuel+1
                            liste_ME_AMONT_sans_chainage = obtenir_liste_ME_amont_direct_sans_chainage(CODE_ME,CODE_CUSTOM,dict_chainage_par_CODE_ME,liste_ME_chainage_original)
                            liste_ME_AMONT_sans_chainage = [x for x in liste_ME_AMONT_sans_chainage if x in dict_tempo_memoire_sous_list_ME[CODE_CUSTOM].liste_ME_restante]
                            liste_ME_AMONT_sans_chainage = tri_list_ME_par_surface(liste_ME_AMONT_sans_chainage,CODE_CUSTOM)
                            if len(liste_ME_AMONT_sans_chainage)>0:
                                liste_ME_total_sans_chainage = deroulage_amont_integral(liste_ME_AMONT_sans_chainage,dict_chainage_par_CODE_ME,CODE_CUSTOM,list_ME_chainage[-1])
                                liste_ME_total_sans_chainage.extend([CODE_ME])
                                liste_ME_total_sans_chainage = ajout_ME_noob(liste_ME_total_sans_chainage,dict_list_ME_noob_a_recup)
                                dict_tempo_memoire_sous_list_ME[CODE_ME] = NiveauListe(liste_ME_total_sans_chainage)
                                dict_tempo_memoire_sous_list_ME[CODE_ME].niveau = niveau_actuel
                                dict_tempo_memoire_sous_list_ME[CODE_ME].surface_restante = calcul_surface_a_partir_list_ME(liste_ME_total_sans_chainage,CODE_CUSTOM)
                            if len(liste_ME_AMONT_sans_chainage)==0:
                                liste_ME_total_sans_chainage=[CODE_ME]
                                liste_ME_total_sans_chainage = ajout_ME_noob(liste_ME_total_sans_chainage,dict_list_ME_noob_a_recup)
                                dict_tempo_memoire_sous_list_ME[CODE_ME] = NiveauListe(liste_ME_total_sans_chainage)
                                dict_tempo_memoire_sous_list_ME[CODE_ME].niveau = niveau_actuel
                                dict_tempo_memoire_sous_list_ME[CODE_ME].surface_restante = calcul_surface_a_partir_list_ME(liste_ME_total_sans_chainage,CODE_CUSTOM)
                        print("coocu")
                        if any(v.surface_restante>surface_limite/f_b and v.surface_restante<surface_limite for v in {k:v for k,v in dict_tempo_memoire_sous_list_ME.items() if v.niveau!=0}.values()):
                            for CODE_ME_partie_tempo,list_ME in dict_tempo_memoire_sous_list_ME.items():
                                if list_ME.niveau!=0:
                                    condition = list_ME.surface_restante<surface_limite and list_ME.surface_restante>surface_limite/f_b
                                    if condition:
                                        surface_a_ajouter = list_ME.surface_restante
                                        niveau_partie = list_ME.niveau
                                        break
                        else:
                            numero_premier_CODE_ME_dans_dict_inverse = len(dict_tempo_memoire_sous_list_ME)-2
                            for numero,CODE_ME_partie_tempo in enumerate(list(dict_tempo_memoire_sous_list_ME)[::-1]):
                                if dict_tempo_memoire_sous_list_ME[CODE_ME_partie_tempo].surface_restante>=surface_limite or numero==numero_premier_CODE_ME_dans_dict_inverse:
                                    list_ME = dict_tempo_memoire_sous_list_ME[CODE_ME_partie_tempo]
                                    surface_a_ajouter = dict_tempo_memoire_sous_list_ME[CODE_ME_partie_tempo].surface_restante
                                    niveau_partie = dict_tempo_memoire_sous_list_ME[CODE_ME_partie_tempo].niveau
                                    print("prout")
                                    break
                        if len([CODE_ME for CODE_ME in list_ME if CODE_ME in list_ME_chainage])>0:
                            nom_partie_a_checker_si_ajout = [nom_partie for nom_partie,list_partie in dict_decoupCUSTOM[CODE_CUSTOM].items() if list_partie.niveau==1][-1]
                            if dict_decoupCUSTOM[CODE_CUSTOM][nom_partie_a_checker_si_ajout].surface_total+surface_a_ajouter<surface_limite:
                                dict_decoupCUSTOM[CODE_CUSTOM][nom_partie_a_checker_si_ajout].surface_total = dict_decoupCUSTOM[CODE_CUSTOM][nom_partie_a_checker_si_ajout].surface_total+surface_a_ajouter
                                dict_decoupCUSTOM[CODE_CUSTOM][nom_partie_a_checker_si_ajout].extend(list_ME)
                                CODE_ME_partie_tempo = nom_partie_a_checker_si_ajout.split("partie_")[-1]
                            else:
                                dict_decoupCUSTOM[CODE_CUSTOM]["partie_" + CODE_ME_partie_tempo] = listMEpartie(list_ME)
                                dict_decoupCUSTOM[CODE_CUSTOM]["partie_" + CODE_ME_partie_tempo].surface_total = surface_a_ajouter
                                dict_decoupCUSTOM[CODE_CUSTOM]["partie_" + CODE_ME_partie_tempo].niveau = niveau_partie
                        else:
                            dict_decoupCUSTOM[CODE_CUSTOM]["partie_" + CODE_ME_partie_tempo] = listMEpartie(list_ME)
                            dict_decoupCUSTOM[CODE_CUSTOM]["partie_" + CODE_ME_partie_tempo].surface_total = surface_a_ajouter
                            dict_decoupCUSTOM[CODE_CUSTOM]["partie_" + CODE_ME_partie_tempo].niveau = niveau_partie
                        #Ménage
                        dict_tempo_memoire_sous_list_ME = suppression_des_ME(dict_tempo_memoire_sous_list_ME,list_ME,CODE_CUSTOM)
                        dict_tempo_memoire_sous_list_ME = diminution_surface(dict_tempo_memoire_sous_list_ME,dict_decoupCUSTOM[CODE_CUSTOM]["partie_" + CODE_ME_partie_tempo].surface_total,CODE_CUSTOM)
                        for CODE_ME_liste_ME in list_ME:
                            if CODE_ME_liste_ME in dict_tempo_memoire_sous_list_ME[CODE_CUSTOM]:
                                dict_tempo_memoire_sous_list_ME[CODE_CUSTOM].remove(CODE_ME_liste_ME)
                        dict_tempo_memoire_sous_list_ME = {k:v for k,v in dict_tempo_memoire_sous_list_ME.items() if v.niveau==0}
                        print("finito")

        return dict_decoupCUSTOM

    print("stop")
    def rassemblement_ME_par_partie(self,dict_decoupREF,dict_rg_Strahler):
        df_nom_ME_simple = dataframe.recuperation_tableaux_nom_ME_simple()
        dict_map_CODE_ME_nom_simple = dict(zip(df_nom_ME_simple['CODE_ME'].to_list(),df_nom_ME_simple['nom_simple_ME'].to_list()))
        for CODE_CUSTOM in list(self):
            dict_tempo = {}
            dict_tempo_2 = {}
            for CODE_partie in list(self[CODE_CUSTOM]):
                list_ME_partie = self[CODE_CUSTOM][CODE_partie]
                CODE_partie_aval = sorted(list_ME_partie, key=lambda x: dict_rg_Strahler[x.split('$')[0]])[0]
                NOM_partie_aval = dict_map_CODE_ME_nom_simple[CODE_partie_aval.split('$')[0]]
                dict_tempo[CODE_partie] = NOM_partie_aval
            num = 1
            num_inconnu = 1
            for CODE_ME,nom_ME_simple in dict_tempo.items():
                if nom_ME_simple in {k:v for k,v in dict_tempo.items() if k!=CODE_ME}.values():
                    dict_tempo_2[CODE_ME] = nom_ME_simple + " " +  str(num)
                    num = num + 1
                if nom_ME_simple not in {k:v for k,v in dict_tempo.items() if k!=CODE_ME}.values():
                    dict_tempo_2[CODE_ME] = nom_ME_simple
                if CODE_ME[2:]==nom_ME_simple:
                    dict_tempo_2[CODE_ME] = 'nom_inconnu' + " " +  str(num_inconnu)
                    num_inconnu = num_inconnu + 1
            for CODE_partie in list(self[CODE_CUSTOM]):
                nom_partie = dict_tempo_2[CODE_partie]
                list_ME_partie = self[CODE_CUSTOM][CODE_partie]
                #REPENDRE LA ATTENTION SI NOM EGAL
                self[CODE_CUSTOM][nom_partie] = dict_decoupREF[CODE_CUSTOM]['gdf_decoupME_CUSTOM'].loc[dict_decoupREF[CODE_CUSTOM]['gdf_decoupME_CUSTOM']['CODE_ME'].isin(list_ME_partie)]
                self[CODE_CUSTOM][nom_partie] = self[CODE_CUSTOM][nom_partie].dissolve()
                self[CODE_CUSTOM][nom_partie] = self[CODE_CUSTOM][nom_partie]['geometry'][0]
                del self[CODE_CUSTOM][CODE_partie]
        for CODE_CUSTOM,dict_partie in self.items():
            self[CODE_CUSTOM] = pd.DataFrame.from_dict(self[CODE_CUSTOM], orient='index',columns=['geometry'])
            self[CODE_CUSTOM]['CODE_CUSTOM'] = self[CODE_CUSTOM].index
            self[CODE_CUSTOM] = self[CODE_CUSTOM].set_geometry("geometry")
        return self
