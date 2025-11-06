import re
from datetime import datetime

import requests
from loguru import logger


def adh_ctrl_001(self):
    if self.cb_titre.currentText() == "":
        return "ADH_CTRL_001"
    else:
        return ""


def adh_ctrl_002(self):
    if self.nom_edit.text() == "" or self.prenom_edit.text() == "":
        return "ADH_CTRL_002"
    else:
        return ""


def adh_ctrl_003(self):
    if self.adresse_edit.text() == "":
        return "ADH_CTRL_003"
    else:
        return ""


def adh_ctrl_004(self):
    if self.cp_edit.text() == "":
        return "ADH_CTRL_004"
    else:
        return ""


def import_adh_enr_005():
    pass


def adh_ctrl_005(self):
    if self.cb_ville.currentText() == "":
        return "ADH_CTRL_005"
    else:
        return ""


def adh_ctrl_006(self):
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if self.email_edit.text() != "":
        if re.match(pat, self.email_edit.text()):
            return ""
        else:
            return "ADH_CTRL_006"
    else:
        return ""


def adh_ctrl_007(self):
    try:
        now = datetime.now()
        date_debut = datetime.strptime(f"01-01-{now.year}", "%d-%m-%Y")
        date_fin = datetime.strptime(f"31-12-{now.year}", "%d-%m-%Y")
        date_adhesion = datetime.strptime(self.adhesion_edit.text(), "%Y/%m/%d")
        logger.info(f"{date_debut} - {date_adhesion} - {date_fin}")
        if date_debut <= self.adhesion_edit.date() <= date_fin:
            return ""
        else:
            return "ADH_CTRL_007"
    except Exception as err:
        logger.error(err)