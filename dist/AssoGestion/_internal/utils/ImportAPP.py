import glob
import os

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
from loguru import logger

from IHM import fic_ind
from utils import TraitementFic
from utils.message import pop_up
from utils.models import assogestion_type_import


class ImportApp(QtWidgets.QMainWindow, fic_ind.Ui_traitement_fic_ind):
    finished = pyqtSignal(bool)

    def __init__(self, Session, type_import, parent=None):
        try:
            super(ImportApp, self).__init__(parent)
            self.setupUi(self)
            self.type_import = type_import
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.Session = Session
            self.nom_fic = ""
            self.init_ihm()
            self.traitement = None
            self.button_lancer_import.clicked.connect(self.traitement_thread)
            self.button_lancer_import.setIcon(QIcon("process.png"))
            self.cb_type_import.currentIndexChanged.connect(self.cb_changed)
            self.show()
        except Exception as err:
            logger.error(err)

    def init_ihm(self):
        s = self.Session()
        res = s.query(assogestion_type_import).all()
        if res:
            self.cb_type_import.addItem("")
            for r in res:
                self.cb_type_import.addItem(r.nom_import)
        s.close()
        self.cb_type_import.setCurrentText(self.type_import)
        self.cb_changed()

    def cb_changed(self):
        try:
            s = self.Session()
            res = s.query(assogestion_type_import).filter_by(nom_import=self.cb_type_import.currentText()).all()
            if res:
                for r in res:
                    self.text_fic_todo.setText(r.nommage_import)
                    self.nom_fic = r.nommage_import
            else:
                self.text_fic_todo.setText("")
            s.close()
        except Exception as err:
            logger.error(err)

    def count_changed(self, value):
        self.format_progress.setValue(value)

    def count_max_changed(self, value):
        self.format_progress.setMaximum(value)

    def step_changed(self, value):
        self.label_etape.setText(value)

    def fin_traitement(self, res):
        try:
            logger.info(res)
            self.resultat_import(res[1], res[2])
            self.finished.emit(True)
            self.close()
        except Exception as err:
            logger.error(err)
    def traitement_thread(self):
        try:
            if self.nom_fic != "":
                file = glob.glob(f"{os.getcwd()}\\Import\\{self.nom_fic}")
                if file:
                    self.button_lancer_import.setEnabled(False)
                    self.traitement = TraitementFic.TraiterFichier(file, self.Session,
                                                                   self.cb_type_import.currentText())
                    self.traitement.line_count_changed.connect(self.count_changed)
                    self.traitement.line_count_max.connect(self.count_max_changed)
                    self.traitement.step_changed.connect(self.step_changed)
                    self.traitement.flag_fin.connect(self.fin_traitement)
                    self.traitement.start()
                else:
                    self.erreur_import(f"Import {self.cb_type_import.currentText()} impossible",
                                       f"Pas de fichier {self.nom_fic} disponible")
            else:
                self.erreur_import(f"Import impossible", f"Veuillez sélectionner un type d'import")
        except Exception as err:
            logger.error(err)

    def erreur_import(self, message, texte):
        msgbox = QMessageBox()
        msgbox.setText(message)
        msgbox.setInformativeText(texte)
        msgbox.setWindowTitle("Import impossible")
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.exec_()

    def resultat_import(self, nb_error, texte):
        if nb_error > 0:
            message = "Traitement en erreur"
            level = "ERROR"
        else:
            message = "Traitement sans erreur"
            level = "INFO"

        pop_up(
            self,
            "Assogestion - AMSE - Import",
            message,
            texte,
            level
        )
