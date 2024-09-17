# -*- coding: utf-8 -*-
from PIL import ImageFont
import textwrap
from app.DORApy.classes.modules.config_DORA import creation_dicts_config

dict_config_espace,dict_config_police = creation_dicts_config()

def extraire_hauteur_largeur_tableau_texte(self,colonne_texte,type):
    if colonne_texte == "NOM_REF":
        colonne_alias = "ALIAS"
    liste_texte = self.df[colonne_alias].tolist()
    liste_liste_texte = [textwrap.wrap(x, width=int(dict_config_espace['nombre_caracteres_decoupage_ligne_simple'][self.taille_globale_carto])) for x in liste_texte]
    liste_largeur,liste_hauteur = convertir_liste_liste_texte_en_listes_largeur_hauteur(liste_liste_texte,dict_config_police['nom_police_' + type + '_' + colonne_texte][self.taille_globale_carto],dict_config_espace['taille_police_' + type + '_' + colonne_texte][self.taille_globale_carto])
    self.df['taille_police'] = dict_config_espace['taille_police_' + type + '_' + colonne_texte][self.taille_globale_carto]
    self.df['nom_police'] = dict_config_police['nom_police_' + type + '_' + colonne_texte][self.taille_globale_carto]
    self.df['hauteur_' + type] = liste_hauteur
    self.df['largeur_' + type] = liste_largeur
    return self

def convertir_liste_liste_texte_en_listes_largeur_hauteur(liste_liste_texte,nom_police,taille_police):
    liste_hauteur = []
    liste_largeur = []
    for liste_lignes in liste_liste_texte:
        liste_tempo_hauteur = []
        liste_tempo_largeur = []
        for ligne in liste_lignes:
            largeur_texte,hauteur_texte = calculer_largeur_hauteur_texte(nom_police,taille_police,ligne)
            liste_tempo_largeur.append(largeur_texte)
            liste_tempo_hauteur.append(hauteur_texte)
        tempo_hauteur = sum(liste_tempo_hauteur)
        tempo_largeur = max(liste_tempo_largeur)
        liste_largeur.append(tempo_largeur)
        liste_hauteur.append(tempo_hauteur)
    return liste_largeur,liste_hauteur

def calculer_largeur_hauteur_texte(nom_police,taille_police,texte):
    taille_police = int(taille_police)
    police = ImageFont.truetype(nom_police,taille_police)
    bbox = police.getbbox(texte)
    longueur_texte = (bbox[2] - bbox[0])*1.2
    hauteur_texte = (bbox[3] - bbox[1])*1.6
    return longueur_texte,hauteur_texte

def calcul_nb_liste_texte(self,colonne_texte,type):
    liste_texte = self.df[colonne_texte].tolist()
    liste_liste_texte = [textwrap.wrap(x, width=13) for x in liste_texte]
    liste_nb_lignes = [len(liste) for liste in liste_liste_texte]
    self.df['nb_ligne_' + type] = liste_nb_lignes
    return self