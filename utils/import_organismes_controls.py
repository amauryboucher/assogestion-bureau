import re

from loguru import logger

from utils.models import assogestion_cotisation


def import_org_ctrl_001(value):
    try:
        if value is None or value == "":
            return "ORG_CTRL_001"
        else:
            return ""
    except Exception as err:
        logger.error(err)


def import_org_ctrl_002(titre, nom, prenom):
    try:
        if titre in ("MONSIEUR", "MADAME") and nom == "" and prenom == "":
            return "ORG_CTRL_002"
        else:
            return ""
    except Exception as err:
        logger.error(err)


def import_org_ctrl_003(value):
    try:
        if value == "":
            return "ADH_CTRL_003"
        else:
            return ""
    except Exception as err:
        logger.error(err)


def import_org_ctrl_004(value):
    try:
        if value == "":
            return "ADH_CTRL_004"
        else:
            return ""
    except Exception as err:
        logger.error(err)


def import_org_ctrl_005(value):
    try:
        if value == "":
            return "ADH_CTRL_005"
        else:
            return ""
    except Exception as err:
        logger.error(err)


def import_org_ctrl_006(value):
    try:
        pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if value is not None:
            if re.match(pat, value):
                return ""
            else:
                return "ADH_CTRL_006"
        else:
            return ""
    except Exception as err:
        logger.error(err)


def import_org_enr_007(titre):
    try:
        if titre == "M ET MME":
            return 2
        elif titre == "MAIRIE DE":
            return 4
        else:
            return 1
    except Exception as err:
        logger.error(err)


def import_org_ctrl_008(s, tarif_cotisation_adherent):
    try:
        if tarif_cotisation_adherent != "SUBVENTION":
            res = s.query(assogestion_cotisation).filter_by(nom_cotisation=tarif_cotisation_adherent).first()
            if res:
                return "", res
            else:
                return "ADH_CTRL_008"
        else:
            return "", None
    except Exception as err:
        logger.error(err)


def global_control(s, ligne):
    try:
        code_adherent, titre_adherent, nom_adherent, prenom_adherent, adresse_adherent, cp_adherent, ville_adherent, tel_adherent, email_adherent, tarif_cotisation_adherent = ligne
        adh_org_001 = import_org_ctrl_001(titre_adherent)
        adh_org_002 = import_org_ctrl_002(titre_adherent, nom_adherent, prenom_adherent)
        adh_org_003 = import_org_ctrl_003(adresse_adherent)
        adh_org_004 = import_org_ctrl_004(cp_adherent)
        adh_org_005 = import_org_ctrl_005(ville_adherent)
        adh_org_006 = import_org_ctrl_006(email_adherent)
        adh_org_008 = import_org_ctrl_008(s, tarif_cotisation_adherent)

        if adh_org_001 != "":
            return adh_org_001
        elif adh_org_002 != "":
            return adh_org_002
        elif adh_org_003 != "":
            return adh_org_004
        elif adh_org_004 != "":
            return adh_org_005
        elif adh_org_005 != "":
            return adh_org_006
        elif adh_org_006 != "":
            return adh_org_006
        elif adh_org_008[0] != "":
            return adh_org_008
        else:
            return "", adh_org_008[1]
    except Exception as err:
        logger.error(err)
