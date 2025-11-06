import os
import shutil
from datetime import datetime

import pythoncom
from PyQt5.QtCore import QThread, pyqtSignal
from docx import Document
from docx2pdf import convert
from loguru import logger
from num2words import num2words

from utils.mail_sender import send_recu_fiscal
from utils.models import assogestion_adh_dons, assogestion_adherents


class TraiterFichierRecu(QThread):
    def __init__(self, items, Session, parent=None):
        try:
            QThread.__init__(self, parent)
            self.items = items
            self.Session = Session
        except Exception as err:
            logger.error(err)

    line_count_changed = pyqtSignal(int)
    line_count_max = pyqtSignal(int)
    step_count_changed = pyqtSignal(int)
    step_count_max = pyqtSignal(int)
    step_changed = pyqtSignal(str)
    flag_fin = pyqtSignal(list)

    def run(self):
        pythoncom.CoInitialize()
        try:
            for i in self.items:
                self.step_count_max.emit(3)
                try:
                    doc = Document(f"{os.getcwd()}\\modele\\recu_don_modele.docx")
                except Exception as err:
                    logger.error(err)
                s = self.Session()
                adh = s.query(assogestion_adherents).filter_by(code_adherent=i.code_adherent).first()
                montant = i.montant_adh + i.montant_dons

                Dictionary = {
                    "recu_num": f"RE{i.id_adh_don}",
                    "nom_adherent": adh.nom_adherent,
                    "pre_adherent": adh.prenom_adherent,
                    "adresse_adherent": adh.adresse_adherent,
                    "cp_adherent": adh.cp_adherent,
                    "ville_adherent": adh.ville_adherent,
                    "montant": str(montant),
                    "m_lettre": f"{num2words(montant, lang='fr')} euros",
                    "date_versement_don": adh.adherent_date_adhesion.strftime("%d/%m/%Y")
                }
                now = datetime.now().strftime("%Y%m%d")
                doc_word = f"{os.getcwd()}\\Export\\Dons\\Doc\\{Dictionary.get('recu_num')}_recu_fiscal_{now}.docx"
                doc_pdf = f"{os.getcwd()}\\Export\\Dons\\Pdf\\TO_SEND\\{Dictionary.get('recu_num')}_recu_fiscal_{now}.pdf"
                nom_fichier = f"RE{i.id_adh_don}.pdf"
                doc_pdf_save = f"{os.getcwd()}\\Export\\Dons\\Pdf\\SEND_OK\\{nom_fichier}", f"{os.getcwd()}\\Export\\Dons\\Pdf\\SEND_KO\\{nom_fichier}"
                self.step_changed.emit("Génération du fichier doc")
                for d in Dictionary:
                    for p in doc.paragraphs:
                        if p.text.find(d) >= 0:
                            p.text = p.text.replace(d, Dictionary[d])
                doc.save(doc_word)
                self.step_count_changed.emit(1)
                self.step_changed.emit("Génération du fichier pdf")
                try:
                    convert(doc_word, doc_pdf)
                    self.step_count_changed.emit(2)
                    self.step_changed.emit("Envoi du reçu par mail")
                    if adh.email_adherent not in ("", None):
                        logger.debug(adh.adherent_date_adhesion.year)
                        res, err = send_recu_fiscal(adh, nom_fichier, doc_pdf, adh.adherent_date_adhesion.year)
                    else:
                        os.startfile(doc_pdf)
                        res = -3
                        self.flag_fin.emit([False, -3, "", doc_pdf])
                    if res == 0:
                        self.step_count_changed.emit(3)
                        os.remove(doc_word)
                        shutil.move(doc_pdf, doc_pdf_save[res])
                        dons = s.query(assogestion_adh_dons).filter_by(id_adh_don=i.id_adh_don).first()
                        dons.date_export = now
                        dons.export = True
                        s.commit()
                        s.close()
                        self.flag_fin.emit([True, 0, "", doc_pdf])
                except Exception as err:
                    logger.error(err)
                    self.flag_fin.emit([False, -1, err, None])

        except Exception as err:
            logger.error(err)
            self.flag_fin.emit([False, -1, err, None])
