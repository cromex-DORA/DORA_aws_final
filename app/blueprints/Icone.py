from flask import  jsonify, Blueprint
import os
from api import dict_dict_info_REF
import sys

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
