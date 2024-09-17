
import os
import sys


def verifier_format_fichier_upload_tableau_DORA(filename):
    liste_formats_attendus = ['xlsx', 'ods', 'xlsm']
    #liste_formats_attendus = ['torrent']
    if filename.split(".")[-1] not in liste_formats_attendus:
        return False, "Format demandé : " + " ,".join(liste_formats_attendus)
    print(filename.split(".")[-1], file=sys.stderr)
    return True, "Bon format"

def verifier_taille_fichier_upload_tableau_DORA(file):
    taille_max_en_MO = 3
    taille_max = taille_max_en_MO*1024*1024
    file.seek(0, os.SEEK_END)  # Aller à la fin du fichier pour obtenir sa taille
    file_length = file.tell()  # Obtenir la taille du fichier
    file.seek(0)  # Revenir au début du fichier pour le lire
    if file_length > taille_max:
        return False, "Taille du fichier inferieure à :" + taille_max_en_MO + " Mo"
    return True, "Taille ok"


def verification_amont_fichier_upload_tableau_DORA(file):
    dict_validation = {}
    dict_validation["format"] = {}
    dict_validation["taille"] = {}
    dict_validation["format"]["valid"], dict_validation["format"]["message"] = verifier_format_fichier_upload_tableau_DORA(file.filename)
    dict_validation["taille"]["valid"], dict_validation["taille"]["message"] = verifier_taille_fichier_upload_tableau_DORA(file)
    return dict_validation

def verifier_fichier_upload_tableau_DORA(file_path):
    print(os.path.getsize(file_path), file=sys.stderr)
    if os.path.getsize(file_path)<10*1024:
        print(os.path.getsize(file_path), file=sys.stderr)
        return False,"C'est pas bon"
    return True,"C'est bon"