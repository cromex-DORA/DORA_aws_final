from flask import  jsonify, Blueprint, send_file
import os
from api import dict_dict_info_REF
import sys
from app.DORApy.classes.Class_DictIconeDORA import DictIcone
import svgwrite
from io import BytesIO

Icone_bp = Blueprint('Icone', __name__)
SECRET_JKEY = os.getenv('SECRET_JKEY')


# Exemple de données d'icônes
icons_data = {
    "FRFR288A": {
        "pressionSignificative": [
            {"name": "MIA_PRESS_ASS"}
        ],
        "pressionNonSignificative": []
    },
    # D'autres ME peuvent être ajoutées ici...
}

@Icone_bp.route('/api/me_icons/<selectedMEId>', methods=['GET'])
def get_me_icons(selectedMEId):
    # Vérifie si l'ID de ME existe dans les données
    df_tempo = dict_dict_info_REF['df_info_ME'].loc[dict_dict_info_REF['df_info_ME']['CODE_ME']==selectedMEId]
    print(df_tempo,file=sys.stderr)
    
    icons_data = {
        selectedMEId: {
            "pressionSignificative": [
                {"name": "MIA_PRESS_ASS"}
            ],
            "pressionNonSignificative": []
        },
        # D'autres ME peuvent être ajoutées ici...
    }    
    if selectedMEId in icons_data:
        return jsonify(icons_data[selectedMEId]), 200
    else:
        return jsonify({"error": "ME ID not found"}), 404
    
@Icone_bp.route('/generate-svg')
def generate_svg():
    dict_icone = DictIcone()
    dict_icone = dict_icone.remplissage_dict_icone("MIA", "PRESS")

    # Créer un SVG avec un rectangle et une icône
    dwg = svgwrite.Drawing(size=(100, 100))  # Augmenter la taille du dessin SVG

    # Rectangle pour représenter Paris (plus grand)
    #dwg.add(dwg.rect(insert=(30, 30), size=(20, 20), fill='lightblue', stroke='black', stroke_width=4))  # Augmenter les dimensions du rectangle

    # Ajouter l'icône au centre du rectangle (plus grand)
    dwg.add(dwg.image(dict_icone['MIA_PRESS_ASS'].url_publique, insert=(30, 30), size=(20, 20)))  # Augmenter la taille de l'icône

    # Sauvegarder dans un fichier en mémoire
    svg_io = BytesIO()
    svg_io.write(dwg.tostring().encode('utf-8'))
    svg_io.seek(0)

    # Envoyer le fichier au frontend
    return send_file(svg_io, mimetype='image/svg+xml')
