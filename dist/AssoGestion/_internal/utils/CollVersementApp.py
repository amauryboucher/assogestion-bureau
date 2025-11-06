from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from loguru import logger

from IHM import coll_cot
from utils.format_input import format_date_to_database
from utils.message import pop_up
from utils.models import assogestion_collectivite_paiement


class CollVersementApp(QtWidgets.QMainWindow, coll_cot.Ui_cotisation_adh):
    finished = pyqtSignal(bool)

    def __init__(self, Session, code_coll, edit, coll_paiement, parent=None):
        super(CollVersementApp, self).__init__(parent)
        try:
            self.Session = Session
            self.application = None
            self.code_coll = code_coll
            self.edit = edit
            self.coll_paiement = coll_paiement
            self.setupUi(self)
            self.init_ihm()
            self.button_save.clicked.connect(self.save)
            self.show()
        except Exception as err:
            logger.error(err)

    def init_ihm(self):
        self.code_edit.setText(str(self.code_coll))

    def save(self):
        s = self.Session()
        try:
            if self.edit:
                pass
            else:
                new_coll_paiement = assogestion_collectivite_paiement(
                    code_collectivite = int(self.code_edit.text()),
                    date_paiement = format_date_to_database(self.date_versement_edit.text()),
                    montant_paiement = float(self.montant_edit.text())
                )
                s.add(new_coll_paiement)
                s.commit()
                self.finished.emit(True)
                self.close()
        except Exception as err:
            logger.error(err)
        finally:
            s.close()
    def erreur_saisie(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Adhérent- Adhésion",
            message,
            texte,
            "ERROR"
        )