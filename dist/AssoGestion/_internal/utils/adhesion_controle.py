from datetime import datetime

from loguru import logger

from utils.format_input import format_date_to_database
from utils.models import assogestion_adh_dons


def controle_adhesion_presence(s, code_adherent, id_cotisation, date_debut, date_fin):
    debut = None
    fin = None
    try:
        debut = datetime.strptime(format_date_to_database(date_debut), "%Y-%m-%d")
    except Exception as err:
        logger.error(err)
    try:
        fin = datetime.strptime(format_date_to_database(date_fin), "%Y-%m-%d")
    except Exception as err:
        logger.error(err)
    try:
        res = s.query(assogestion_adh_dons).filter_by(code_adherent=code_adherent, id_cotisation=id_cotisation).first()
        if res:
            return "ADHESION_CTRL_001"
        else:
            res = s.query(assogestion_adh_dons).filter_by(code_adherent=code_adherent, date_debut_adh_don=debut,
                                                          date_fin_adh_don=fin).all()
            if res:
                return "ADHESION_CTRL_002"
            else:
                return ""
    except Exception as err:
        logger.error(err)