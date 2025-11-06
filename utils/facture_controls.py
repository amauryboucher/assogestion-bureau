import re

from loguru import logger

from utils.models import assogestion_annuaire, assogestion_ligne_facture


def CF_CLI_001(self):
    if self.code_client_edit.text () == "":
        logger.warning(self.dic_error.get("CF_CLI_001"))
        return "CF_CLI_001"
    else:
        return ""

def CF_CLI_002(self):
    if self.client_rs.text() == "":
        logger.warning(self.dic_error.get("CF_CLI_002"))
        return "CF_CLI_002"
    else:
        return ""

def ENR_CLI_003(self):
    s = self.Session()
    try:
        self.cb_ville.clear()
        if len(self.client_cp.text()) == 5:
            logger.info("Enrichissement de la ville du client à partir du code postal")
            res = s.query(assogestion_annuaire).filter_by(cp=self.client_cp.text()).all()
            if res:
                for r in res:
                    self.cb_ville.addItem(r.ville)
            else:
                self.error_facture("Une erreur est survenue", "Impossible d'enrichir la ville automatiquement")
    except Exception as err:
        logger.error(err)
        self.error_facture("Une erreur est survenue", str(err))
    finally:
        s.close()

def CF_CLI_004(self):
    if self.client_adresse.text() == "":
        logger.warning(self.dic_error.get("CF_CLI_004"))
        return "CF_CLI_004"
    else:
        return ""

def CF_CLI_005(self):
    if self.client_cp.text() == "":
        logger.warning(self.dic_error.get("CF_CLI_005"))
        return "CF_CLI_005"
    else:
        return ""

def CF_CLI_006(self):
    if self.cb_ville.currentText() == "":
        logger.warning(self.dic_error.get("CF_CLI_006"))
        return "CF_CLI_006"
    else:
        return ""

def CF_CLI_007(self):
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if self.client_mail.text() != "":
        if re.match(pat, self.client_mail.text()):
            return ""
        else:
            logger.warning(self.dic_error.get("CF_CLI_007"))
            return "CF_CLI_007"
    else:
        return ""

def CM_FAC_008(self):
    # Vérifier que la somme des lignes de la facture soit > 0
    s = self.Session()
    res = s.query(assogestion_ligne_facture).filter_by(inv_no=self.data_dict.get('inv_no')).all()
    s.close()
    if res:
        for r in res:
            if (float(r.qty) * r.prix_unitaire) == 0:
                logger.warning(self.dic_error.get("CM_FAC_008"))
                return "CM_FAC_008"
        else:
            return ""
    else:
        logger.warning(self.dic_error.get("CM_FAC_008"))
        return "CM_FAC_008"

def CF_FAC_009(self):
    if self.code_client_edit.text() in ("CLXXXX", ""):
        logger.warning(self.dic_error.get("CF_FAC_009"))
        return "CF_FAC_009"
    else:
        return ""

