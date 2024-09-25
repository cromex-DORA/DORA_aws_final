# -*- coding: utf-8 -*-
from PIL import ImageFont
import textwrap
import numpy as np
from app.DORApy.classes.modules.config_DORA import creation_dicts_config
dict_config_espace,dict_config_police = creation_dicts_config()


def calcul_nb_liste_lignes_multiples(self,colonne_texte):
    liste_texte = self.df[colonne_texte].tolist()
    liste_liste_texte = [textwrap.wrap(x, width=dict_config_espace['nombre_caracteres_decoupage_lm'][self.taille_globale_carto]) for x in liste_texte]
    liste_nb_lignes = [len(liste) for liste in liste_liste_texte]
    self.df['nb_ligne_ligne_indiv'] = liste_nb_lignes
    return self


def extraire_hauteur_largeur_tableau_lignes_multiples(self,colonne_texte,type,sous_type):
    liste_texte = self.df[colonne_texte].tolist()
    liste_liste_texte = [textwrap.wrap(x, width=dict_config_espace['nombre_caracteres_decoupage_lm'][self.taille_globale_carto]) for x in liste_texte]
    liste_largeur,liste_hauteur = convertir_liste_liste_texte_en_listes_largeur_hauteur(liste_liste_texte,dict_config_police['nom_police_' + type + '_' + sous_type][self.taille_globale_carto],dict_config_espace['taille_police_' + type + '_' + sous_type][self.taille_globale_carto])
    self.df['taille_police'] = dict_config_espace['taille_police_' + type + '_' + sous_type][self.taille_globale_carto]
    self.df['nom_police'] = dict_config_police['nom_police_' + type + '_' + sous_type][self.taille_globale_carto]
    self.df['hauteur_ligne_indiv'] = liste_hauteur
    self.df['largeur_ligne_indiv'] = liste_largeur
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
    longueur_texte = (bbox[2] - bbox[0])*1.0
    hauteur_texte = (bbox[3] - bbox[1])*1.6
    return longueur_texte,hauteur_texte

def adaptation_hauteur_largeur_lm_indiv_fonction_nb_lignes(self,colonne_texte):
    #Le calcul de la hauteur du bloc ligne multiple surestime beaucoup quand plusieurs lignes
    self.df.loc[self.df['nb_ligne_ligne_indiv']==2,'hauteur_ligne_indiv'] = self.df['hauteur_ligne_indiv']*0.85
    self.df.loc[self.df['nb_ligne_ligne_indiv']==3,'hauteur_ligne_indiv'] = self.df['hauteur_ligne_indiv']*0.70
    self.df.loc[self.df['nb_ligne_ligne_indiv']==4,'hauteur_ligne_indiv'] = self.df['hauteur_ligne_indiv']*0.75
    self.df.loc[self.df['nb_ligne_ligne_indiv']==5,'hauteur_ligne_indiv'] = self.df['hauteur_ligne_indiv']*0.65
    return self

def adaptation_hauteur_largeur_lm_indiv_fonction_orientation(self,colonne_texte):
    #La largeur en biais est la hauteur que l'on verra sur la carto finale
    self.df['hauteur_ligne_indiv_droit'] = self.df['hauteur_ligne_indiv'] * 0.9
    self.df['largeur_ligne_indiv_droit'] = self.df['largeur_ligne_indiv'] * 1.15
    self.df['hauteur_ligne_indiv_biais'] = [future_hauteur*np.cos(dict_config_espace['angle_rotation_lm_paysage'][self.taille_globale_carto] * np.pi / 180.)*1.65 for future_hauteur in self.df['largeur_ligne_indiv']]
    self.df['largeur_ligne_indiv_biais'] = [future_largeur/np.cos(dict_config_espace['angle_rotation_lm_paysage'][self.taille_globale_carto] * np.pi / 180.)*0.9 for future_largeur in self.df['hauteur_ligne_indiv']]
    return self