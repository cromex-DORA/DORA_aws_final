# -*- coding: utf-8 -*-
import pandas as pd
import shapely.geometry as geom
import geopandas as gpd
from app.DORApy.classes.modules import config_DORA
import numpy as np
###Fichiers config
dict_config_espace,dict_config_police = config_DORA.creation_dicts_config()
df_csv_x_icone_bloc_icone,df_csv_y_icone_bloc_icone = config_DORA.import_csv_placement_icone_bloc_icone()


def empilement_paysage(self,type_placement,dict_info_custom):
    #empilement paysage
    liste_orientation = ["B","H"]
    for orientation in liste_orientation:
        if type_placement.split(" ")[0] =="placement_boite_classique":
            filtre_boite = (self["orient_BH"] == orientation)
        if type_placement.split(" ")[0] =="placement_boite_extremite_qui_depassent":
            filtre_boite = (self["orient_BH"] == orientation) & (self["replacement"]=="paysage")
            if len(self[(self["orient_BH"]==orientation) & (self["replacement"]=='paysage')])==0:
                break
        gdf_filtre = self[filtre_boite]
        gdf_filtre = gdf_filtre.sort_values(by="X_centre_decoupREF",ascending=False)
        liste_x_REF = gdf_filtre["X_centre_decoupREF"].to_list()
        liste_largeur = gdf_filtre["taille_largeur_boite_biais"].to_list()
        liste_REF = gdf_filtre["CODE_REF"].to_list()
        liste_x_apres_empilement = [0] * len(liste_REF)
        liste_numero_ensemble_bloc = [0] * len(liste_REF)
        compteur_numero_ensemble_bloc = 1
        #On empile les boites, du haut vers le bas
        for numero_REF,REF in enumerate(liste_REF):
            if numero_REF==0:
                liste_x_apres_empilement[0] = liste_x_REF[0]
                liste_numero_ensemble_bloc[0] = 1
            if numero_REF>0:
                bas_boite_precedente = liste_x_apres_empilement[numero_REF-1]-liste_largeur[numero_REF-1]/2-dict_config_espace['espace_sous_boite_complete'][dict_info_custom['echelle']]
                haut_boite_actuel = liste_x_REF[numero_REF]+liste_largeur[numero_REF]/2
                if bas_boite_precedente<haut_boite_actuel:
                    liste_x_apres_empilement[numero_REF] = liste_x_apres_empilement[numero_REF-1]-liste_largeur[numero_REF-1]/2-dict_config_espace['espace_sous_boite_complete'][dict_info_custom['echelle']]-liste_largeur[numero_REF]/2
                    liste_numero_ensemble_bloc[numero_REF] = liste_numero_ensemble_bloc[numero_REF-1]
                if bas_boite_precedente>haut_boite_actuel:
                    liste_x_apres_empilement[numero_REF] = liste_x_REF[numero_REF]
                    liste_numero_ensemble_bloc[numero_REF] = liste_numero_ensemble_bloc[numero_REF-1]+1

        #Replacement : On tape par en dessous pour faire remonter les boites
        #Si on est sur le premier algo de traitment de placement des boites
        if type_placement.split(" ")[0] =="placement_boite_classique":
            limite_droite_boite = dict_info_custom["max_x_custom"]
            limite_gauche_boite = dict_info_custom["min_x_custom"]
        if type_placement.split(" ")[0] =="placement_boite_extremite_qui_depassent":
            if orientation =="B":
                limite_droite_boite = dict_info_custom["limite_x_droite_boite_basse"]
                limite_gauche_boite = dict_info_custom["limite_x_gauche_boite_basse"]
            if orientation =="H":
                limite_droite_boite = dict_info_custom["limite_x_droite_boite_haut"]
                limite_gauche_boite = dict_info_custom["limite_x_gauche_boite_haut"]
        #Si un seul bloc, on regroupe tout
        largeur_totale_ensemble_boite = sum(liste_largeur) + (len(liste_largeur)-1)*dict_config_espace['espace_sous_boite_complete'][dict_info_custom['echelle']]
        if len(liste_REF)==1:
            liste_x_apres_empilement = liste_x_REF
        if largeur_totale_ensemble_boite>(limite_droite_boite-limite_gauche_boite):
            droite_de_lensemble_des_boites = liste_x_apres_empilement[0]+liste_largeur[0]/2
            gauche_de_lensemble_des_boites = liste_x_apres_empilement[-1]-liste_largeur[-1]/2
            dif_droite = limite_droite_boite-droite_de_lensemble_des_boites
            dif_gauche = limite_gauche_boite-gauche_de_lensemble_des_boites
            decalage_ensemble_boite = (dif_gauche+dif_droite)/2
            liste_x_apres_empilement = [x+decalage_ensemble_boite for x in liste_x_apres_empilement]
            liste_definitive_x = liste_x_apres_empilement
            liste_numero_ensemble_bloc = [1 for numero_boite in liste_numero_ensemble_bloc]

        #Si plus d'un bloc, on replace subtilement
        if largeur_totale_ensemble_boite<(limite_droite_boite-limite_gauche_boite):
            liste_x_apres_deplacement_vers_droite = liste_x_apres_empilement
            #On commence par la droite et on remonte ensemble de bloc par ensemble de bloc vers la gauche
            for numero_boite,numero_ensemble_boite_actuel in enumerate(liste_numero_ensemble_bloc):
                liste_ensemble_boites_actuelles_largeur = []
                liste_ensemble_boites_actuelles_x_REF = []
                liste_ensemble_boites_actuelles_x_apres_empilement = []
                #On recupere toutes les infos sur le bloc actuel
                for numero_REF,REF in enumerate(liste_REF):
                    if liste_numero_ensemble_bloc[numero_REF]==numero_ensemble_boite_actuel:
                        liste_ensemble_boites_actuelles_largeur.append(liste_largeur[numero_REF])
                        liste_ensemble_boites_actuelles_x_apres_empilement.append(liste_x_apres_empilement[numero_REF])
                        liste_ensemble_boites_actuelles_x_REF.append(liste_x_REF[numero_REF])
                largeur_bloc_actuel = sum(liste_ensemble_boites_actuelles_largeur)+(len(liste_ensemble_boites_actuelles_largeur)-1)*dict_config_espace['espace_sous_boite_complete'][dict_info_custom['echelle']]
                centre_x_bloc_actuel = ((liste_ensemble_boites_actuelles_x_apres_empilement[0]+liste_ensemble_boites_actuelles_largeur[0]/2)+(liste_ensemble_boites_actuelles_x_REF[-1]-liste_ensemble_boites_actuelles_largeur[-1]/2))/2
                x_droite_necessaire_sur_ensemble_de_bloc_actuel = centre_x_bloc_actuel + largeur_bloc_actuel/2
                x_droite_derniere_boite_bloc_actuel = liste_ensemble_boites_actuelles_x_apres_empilement[0] + liste_ensemble_boites_actuelles_largeur[0]/2

                #Pour les boites "du milieux"
                #if numero_ensemble_boite_actuel!=1 and numero_ensemble_boite_actuel!=max(liste_numero_ensemble_bloc):
                if numero_boite==max([i for i in range(len(liste_numero_ensemble_bloc)) if liste_numero_ensemble_bloc[i] == numero_ensemble_boite_actuel]):
                    liste_ensemble_boites_precedentes_largeur = []
                    liste_ensemble_boites_precedentes_x_REF = []
                    liste_ensemble_boites_precedentes_x_apres_empilement = []
                    #On recupere toutes les infos sur le bloc é droite
                    for numero_REF,REF in enumerate(liste_REF):
                        if liste_numero_ensemble_bloc[numero_REF]==numero_ensemble_boite_actuel-1:
                            liste_ensemble_boites_precedentes_largeur.append(liste_largeur[numero_REF])
                            liste_ensemble_boites_precedentes_x_apres_empilement.append(liste_x_apres_empilement[numero_REF])
                            liste_ensemble_boites_precedentes_x_REF.append(liste_x_REF[numero_REF])
                    if type_placement.split(" ")[0] =="placement_boite_classique":
                        pass

                    if type_placement.split(" ")[0] =="placement_boite_extremite_qui_depassent":
                        if numero_ensemble_boite_actuel==1:
                            limite_droite_boites_portraits = limite_droite_boite
                        if numero_ensemble_boite_actuel>1:
                            limite_droite_boites_portraits = liste_ensemble_boites_precedentes_x_apres_empilement[-1]-liste_ensemble_boites_precedentes_largeur[-1]/2-dict_config_espace['espace_sous_boite_complete'][dict_info_custom['echelle']]
                        if x_droite_necessaire_sur_ensemble_de_bloc_actuel<limite_droite_boites_portraits:
                            decalage_boite_vers_droite = x_droite_necessaire_sur_ensemble_de_bloc_actuel - x_droite_derniere_boite_bloc_actuel
                            liste_ensemble_boites_actuelles_x_apres_empilement = [x_apres_empilement + decalage_boite_vers_droite for x_apres_empilement in liste_ensemble_boites_actuelles_x_apres_empilement]
                        if x_droite_necessaire_sur_ensemble_de_bloc_actuel>limite_droite_boites_portraits:    
                            decalage_boite_vers_droite = limite_droite_boites_portraits - x_droite_derniere_boite_bloc_actuel
                            liste_ensemble_boites_actuelles_x_apres_empilement = [x_apres_empilement + decalage_boite_vers_droite for x_apres_empilement in liste_ensemble_boites_actuelles_x_apres_empilement]
          
                    #On actualise la liste des x
                    nombre_boite_avant_ensemble_boites_actuel = len([numero_ensemble_bloc for numero_ensemble_bloc in liste_numero_ensemble_bloc if numero_ensemble_bloc<liste_numero_ensemble_bloc[numero_boite]])
                    for numero_boite_dans_ensemble_boite in range(nombre_boite_avant_ensemble_boites_actuel,numero_boite+1):
                        liste_x_apres_deplacement_vers_droite[numero_boite_dans_ensemble_boite] = liste_ensemble_boites_actuelles_x_apres_empilement[numero_boite_dans_ensemble_boite-nombre_boite_avant_ensemble_boites_actuel]
                    liste_definitive_x = liste_x_apres_deplacement_vers_droite
        if len(gdf_filtre)==0:
            liste_definitive_x = []
        gdf_filtre["X_centre_boiteREF" + "_apres_empilement"]=liste_definitive_x
        self = self[~filtre_boite]
        self=pd.concat([self,gdf_filtre])
    return self

def empilement_portrait(self,type_placement,dict_info_custom):
    #empilement portrait
    liste_orientation = ["G","D"]
    for orientation in liste_orientation:
        if type_placement.split(" ")[0] =="placement_boite_classique":
            filtre_boite = (self["orient_GD"] == orientation)
        if type_placement.split(" ")[0] =="placement_boite_extremite_qui_depassent":
            filtre_boite = (self["orient_GD"] == orientation) & (self["replacement"]=="portrait")
            if len(self[(self["orient_GD"]==orientation) & (self["replacement"]=='portrait')])==0:
                break
        gdf_filtre = self[filtre_boite]
        gdf_filtre = gdf_filtre.sort_values(by="Y_centre_decoupREF",ascending=False)
        liste_y_REF = gdf_filtre["Y_centre_decoupREF"].to_list()
        liste_hauteur = gdf_filtre["taille_hauteur_boite_droit"].to_list()
        liste_REF = gdf_filtre["CODE_REF"].to_list()
        liste_y_apres_empilement = [0] * len(liste_REF)
        liste_numero_ensemble_bloc = [0] * len(liste_REF)
        compteur_numero_ensemble_bloc = 1
        #On empile les boites, du haut vers le bas
        for numero_REF,REF in enumerate(liste_REF):
            if numero_REF==0:
                liste_y_apres_empilement[0] = liste_y_REF[0]
                liste_numero_ensemble_bloc[0] = 1
            if numero_REF>0:
                bas_boite_precedente = liste_y_apres_empilement[numero_REF-1]-liste_hauteur[numero_REF-1]/2-dict_config_espace['espace_sous_boite_complete'][dict_info_custom['echelle']]
                haut_boite_actuel = liste_y_REF[numero_REF]+liste_hauteur[numero_REF]/2
                if bas_boite_precedente<haut_boite_actuel:
                    liste_y_apres_empilement[numero_REF] = liste_y_apres_empilement[numero_REF-1]-liste_hauteur[numero_REF-1]/2-dict_config_espace['espace_sous_boite_complete'][dict_info_custom['echelle']]-liste_hauteur[numero_REF]/2
                    liste_numero_ensemble_bloc[numero_REF] = liste_numero_ensemble_bloc[numero_REF-1]
                if bas_boite_precedente>haut_boite_actuel:
                    liste_y_apres_empilement[numero_REF] = liste_y_REF[numero_REF]
                    liste_numero_ensemble_bloc[numero_REF] = liste_numero_ensemble_bloc[numero_REF-1]+1

        #Replacement : On tape par en dessous pour faire remonter les boites
        #Si on est sur le premier algo de traitment de placement des boites
        if type_placement.split(" ")[0] =="placement_boite_classique":
            limite_haute_boite = dict_info_custom["max_y_custom"]
            limite_basse_boite = dict_info_custom["min_y_custom"]
        if type_placement.split(" ")[0] =="placement_boite_extremite_qui_depassent":
            if orientation =="G":
                limite_haute_boite = dict_info_custom["limite_y_haute_boite_gauche"]
                limite_basse_boite = dict_info_custom["limite_y_basse_boite_gauche"]
            if orientation =="D":
                limite_haute_boite = dict_info_custom["limite_y_haute_boite_droite"]
                limite_basse_boite = dict_info_custom["limite_y_basse_boite_droite"]
        #Si une seule boite, on touche pas
        #Si un seul bloc, on regroupe tout
        hauteur_totale_ensemble_boite = sum(liste_hauteur) + (len(liste_hauteur)-1)*dict_config_espace['espace_sous_boite_complete'][dict_info_custom['echelle']]
        if len(liste_REF)==1:
            liste_y_apres_empilement = liste_y_REF
        if hauteur_totale_ensemble_boite>(limite_haute_boite-limite_basse_boite):
            haut_de_lensemble_des_boites = liste_y_apres_empilement[0]+liste_hauteur[0]/2
            bas_de_lensemble_des_boites = liste_y_apres_empilement[-1]-liste_hauteur[-1]/2
            dif_haute = limite_haute_boite-haut_de_lensemble_des_boites
            dif_basse = limite_basse_boite-bas_de_lensemble_des_boites
            decalage_ensemble_boite = (dif_basse+dif_haute)/2
            liste_y_apres_empilement = [y+decalage_ensemble_boite for y in liste_y_apres_empilement]
            liste_definitive_y = liste_y_apres_empilement
            liste_numero_ensemble_bloc = [1 for numero_boite in liste_numero_ensemble_bloc]

        #Si plus d'un bloc, on replace subtilement
        if hauteur_totale_ensemble_boite<(limite_haute_boite-limite_basse_boite):
            liste_y_apres_deplacement_vers_haut = liste_y_apres_empilement
            #On commence par la haut et on remonte ensemble de bloc par ensemble de bloc vers la bas
            for numero_boite,numero_ensemble_boite_actuel in enumerate(liste_numero_ensemble_bloc):
                liste_ensemble_boites_actuelles_hauteur = []
                liste_ensemble_boites_actuelles_y_REF = []
                liste_ensemble_boites_actuelles_y_apres_empilement = []
                #On recupere toutes les infos sur le bloc actuel
                for numero_REF,REF in enumerate(liste_REF):
                    if liste_numero_ensemble_bloc[numero_REF]==numero_ensemble_boite_actuel:
                        liste_ensemble_boites_actuelles_hauteur.append(liste_hauteur[numero_REF])
                        liste_ensemble_boites_actuelles_y_apres_empilement.append(liste_y_apres_empilement[numero_REF])
                        liste_ensemble_boites_actuelles_y_REF.append(liste_y_REF[numero_REF])
                hauteur_bloc_actuel = sum(liste_ensemble_boites_actuelles_hauteur)+(len(liste_ensemble_boites_actuelles_hauteur)-1)*dict_config_espace['espace_sous_boite_complete'][dict_info_custom['echelle']]
                centre_y_bloc_actuel = ((liste_ensemble_boites_actuelles_y_apres_empilement[0]+liste_ensemble_boites_actuelles_hauteur[0]/2)+(liste_ensemble_boites_actuelles_y_REF[-1]-liste_ensemble_boites_actuelles_hauteur[-1]/2))/2
                y_haut_necessaire_sur_ensemble_de_bloc_actuel = centre_y_bloc_actuel + hauteur_bloc_actuel/2
                y_haut_derniere_boite_bloc_actuel = liste_ensemble_boites_actuelles_y_apres_empilement[0] + liste_ensemble_boites_actuelles_hauteur[0]/2

                if numero_boite==max([i for i in range(len(liste_numero_ensemble_bloc)) if liste_numero_ensemble_bloc[i] == numero_ensemble_boite_actuel]):
                    liste_ensemble_boites_precedentes_hauteur = []
                    liste_ensemble_boites_precedentes_y_REF = []
                    liste_ensemble_boites_precedentes_y_apres_empilement = []
                    #On recupere toutes les infos sur le bloc é haut
                    for numero_REF,REF in enumerate(liste_REF):
                        if liste_numero_ensemble_bloc[numero_REF]==numero_ensemble_boite_actuel-1:
                            liste_ensemble_boites_precedentes_hauteur.append(liste_hauteur[numero_REF])
                            liste_ensemble_boites_precedentes_y_apres_empilement.append(liste_y_apres_empilement[numero_REF])
                            liste_ensemble_boites_precedentes_y_REF.append(liste_y_REF[numero_REF])
                    if type_placement.split(" ")[0] =="placement_boite_classique":
                        pass

                    if type_placement.split(" ")[0] =="placement_boite_extremite_qui_depassent" or type_placement.split(" ")[0] =="placement_boite_classique":
                        if numero_ensemble_boite_actuel==1:
                            limite_haut_boites_paysages = limite_haute_boite
                        if numero_ensemble_boite_actuel>1:
                            limite_haut_boites_paysages = liste_ensemble_boites_precedentes_y_apres_empilement[-1]-liste_ensemble_boites_precedentes_hauteur[-1]/2-dict_config_espace['espace_sous_boite_complete'][dict_info_custom['echelle']]
                        if y_haut_necessaire_sur_ensemble_de_bloc_actuel<limite_haut_boites_paysages:
                            decalage_boite_vers_haut = y_haut_necessaire_sur_ensemble_de_bloc_actuel - y_haut_derniere_boite_bloc_actuel
                            liste_ensemble_boites_actuelles_y_apres_empilement = [y_apres_empilement + decalage_boite_vers_haut for y_apres_empilement in liste_ensemble_boites_actuelles_y_apres_empilement]
                        if y_haut_necessaire_sur_ensemble_de_bloc_actuel>limite_haut_boites_paysages:    
                            decalage_boite_vers_haut = limite_haut_boites_paysages - y_haut_derniere_boite_bloc_actuel
                            liste_ensemble_boites_actuelles_y_apres_empilement = [y_apres_empilement + decalage_boite_vers_haut for y_apres_empilement in liste_ensemble_boites_actuelles_y_apres_empilement]
          
                    #On actualise la liste des y
                    nombre_boite_avant_ensemble_boites_actuel = len([numero_ensemble_bloc for numero_ensemble_bloc in liste_numero_ensemble_bloc if numero_ensemble_bloc<liste_numero_ensemble_bloc[numero_boite]])
                    for numero_boite_dans_ensemble_boite in range(nombre_boite_avant_ensemble_boites_actuel,numero_boite+1):
                        liste_y_apres_deplacement_vers_haut[numero_boite_dans_ensemble_boite] = liste_ensemble_boites_actuelles_y_apres_empilement[numero_boite_dans_ensemble_boite-nombre_boite_avant_ensemble_boites_actuel]
                    liste_definitive_y = liste_y_apres_deplacement_vers_haut
        if len(gdf_filtre)==0:
            liste_definitive_y = []
        gdf_filtre["Y_centre_boiteREF_apres_empilement"]=liste_definitive_y
        self = self[~filtre_boite]
        self=pd.concat([self,gdf_filtre])
    return self