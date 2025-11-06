import re

from loguru import logger


def import_adh_ctrl_001(value):
    try:
        if value is None:
            return "ADH_CTRL_001"
        else:
            return ""
    except Exception as err:
        logger.error(err)


def import_adh_ctrl_002(titre, nom, prenom):
    try:
        if titre in (
                "MONSIEUR", "MADEMOISELLE", "MADAME", "M ET MME", "DOCTEUR", "PÈRE") and nom == "" and prenom == "":
            return "ADH_CTRL_002"
        else:
            return ""
    except Exception as err:
        logger.error(err)


def import_adh_ctrl_003(value):
    try:
        if value == "":
            return "ADH_CTRL_003"
        else:
            return ""
    except Exception as err:
        logger.error(err)


def import_adh_ctrl_004(value):
    try:
        if value == "":
            return "ADH_CTRL_004"
        else:
            return ""
    except Exception as err:
        logger.error(err)


def import_adh_ctrl_005(value):
    try:
        if value == "":
            return "ADH_CTRL_005"
        else:
            return ""
    except Exception as err:
        logger.error(err)


def import_adh_ctrl_006(value):
    try:
        pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if value != "":
            if re.match(pat, value):
                return ""
            else:
                return "ADH_CTRL_006"
        else:
            return ""
    except Exception as err:
        logger.error(err)

def global_control(num, ligne):
    try:
        code_adherent, titre_adherent, nom_adherent, prenom_adherent, adresse_adherent, adresse_2_adherent, cp_adherent, ville_adherent, tel_adherent, email_adherent = ligne
        adh_ctrl_001 = import_adh_ctrl_001(titre_adherent)
        adh_ctrl_002 = import_adh_ctrl_002(titre_adherent, nom_adherent, prenom_adherent)
        adh_ctrl_003 = import_adh_ctrl_003(adresse_adherent)
        adh_ctrl_004 = import_adh_ctrl_004(cp_adherent)
        adh_ctrl_005 = import_adh_ctrl_005(ville_adherent)
        adh_ctrl_006 = import_adh_ctrl_006(email_adherent)

        if adh_ctrl_001 != "":
            return adh_ctrl_001
        elif adh_ctrl_002 != "":
            return adh_ctrl_002
        elif adh_ctrl_003 != "":
            return adh_ctrl_003
        elif adh_ctrl_004 != "":
            return adh_ctrl_004
        elif adh_ctrl_005 != "":
            return adh_ctrl_005
        elif adh_ctrl_006 != "":
            logger.info(f"{num}, {email_adherent}")
            return adh_ctrl_006
        else:
            return ""
    except Exception as err:
        logger.error(err)
