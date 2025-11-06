from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from loguru import logger

from IHM import fic_recu_ind
from utils import TraitementRecu
from utils.message import pop_up
from utils.models import assogestion_adh_dons


class ExportRecuApp(QtWidgets.QMainWindow, fic_recu_ind.Ui_traitement_fic_ind_recu):
    finished = pyqtSignal(bool)

    def __init__(self, Session, adh, parent=None):
        try:
            super(ExportRecuApp, self).__init__(parent)
            self.setupUi(self)
            self.adh = adh
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.Session = Session
            self.nom_fic = ""
            self.init_ihm()
            self.traitement = None
            self.traitement_thread()
            self.show()
        except Exception as err:
            logger.error(err)

    def init_ihm(self):
        pass

    def count_changed_step(self, value):
        self.step_progress.setValue(value)

    def count_max_changed_step(self, value):
        self.step_progress.setMaximum(value)

    def step_changed(self, value):
        self.label_etape.setText(value)

    def fin_traitement(self, value):
        flag, res, err, pdf = value
        if flag:
            self.info_envoi("Envoi terminé avec succès", "Le reçu a bien été envoyé par mail", "INFO")
        else:
            if res == -1:
                self.info_envoi("Envoi échoué", f"Le reçu n'a pas pu être exporté\n {err}", "ERROR")
            elif res == -2:
                self.info_envoi("Envoi par email impossible", f"Le reçu n'a pas été envoyé. Il a été enregistré sur votre ordinateur", "WARNING")
        logger.info(value)
        self.close()

    def closeEvent(self, a0):
        self.finished.emit(True)
        a0.accept()
    def traitement_thread(self):
        s = self.Session()
        if self.adh:
            adh_dons = s.query(assogestion_adh_dons).filter_by(code_adherent=self.adh).all()
        else:
            adh_dons = s.query(assogestion_adh_dons).all()
        s.close()
        self.traitement = TraitementRecu.TraiterFichierRecu(adh_dons, self.Session)
        self.traitement.step_count_changed.connect(self.count_changed_step)
        self.traitement.step_count_max.connect(self.count_max_changed_step)
        self.traitement.step_changed.connect(self.step_changed)
        self.traitement.flag_fin.connect(self.fin_traitement)
        self.traitement.start()

    def info_envoi(self, message, texte, level):
        pop_up(
            self,
            "AssoGestion - AMSE - Adhérent - Envoi du reçu",
            message,
            texte,
            level
        )