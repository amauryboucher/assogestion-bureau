import getpass

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem
from loguru import logger

from IHM import liste_activite
from utils.DetailActiviteApp import DetailActAPP
from utils.ImportAPP import ImportApp
from utils.message import pop_up
from utils.models import assogestion_activite


class ListeActivitesAPP(QtWidgets.QMainWindow, liste_activite.Ui_liste_activite):
    finished = pyqtSignal(bool)

    def __init__(self, Session, parent=None):

        super(ListeActivitesAPP, self).__init__(parent)
        try:
            self.application = None
            self.Session = Session
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.button_creation_activite.clicked.connect(self.open_new_activite)
            self.button_creation_activite.setIcon(QIcon("creer.png"))
            self.tab_activite.doubleClicked.connect(self.open_edit_activite)
            #self.button_import_activite.clicked.connect(self.open_import)
            #self.button_import_activite.setIcon(QIcon("importer.png"))
            self.button_retour.setIcon(QIcon('retour.png'))
            self.button_retour.clicked.connect(self.close)
            self.init_app()
            self.show()
        except Exception as err:
            logger.error(err)

    def init_app(self):
        try:
            s = self.Session()
            res = s.query(assogestion_activite).order_by(assogestion_activite.id_activite).all()
            self.tab_activite.clear()
            self.tab_activite.setRowCount(0)
            if res:
                self.tab_activite.setColumnCount(6)
                self.tab_activite.setHorizontalHeaderLabels(
                    ["ID", "Libellé", "Date", "Nb participant", "Nb places max", "Montant"])
                for i, r in enumerate(res):
                    self.tab_activite.insertRow(i)
                    result = r.id_activite, r.libelle_activite, r.date_activite, r.nb_participant_activite, r.nb_participant_max_activite, r.tarif_activite
                    for j, res in enumerate(result):
                        self.tab_activite.setItem(i, j, QTableWidgetItem(f'{result[j]}'))
            self.tab_activite.resizeColumnsToContents()
            self.tab_activite.horizontalHeader().setStretchLastSection(True)
            s.close()
        except Exception as err:
            logger.error(err)

    def open_new_activite(self):
        self.application = DetailActAPP(self.Session, False, None)
        self.application.finished.connect(self.do_something)

    def open_edit_activite(self):
        s = self.Session()
        act = None
        if self.tab_activite.currentItem().isSelected():
            if self.tab_activite.currentItem().column() == 0:
                act = s.query(assogestion_activite).filter_by(
                    id_activite=self.tab_activite.currentItem().text()).first()

        if act:
            if act.locked:
                self.warning_act("Modification impossible",
                                 f"L'activité est déjà en cours de modification par {act.locked_by}")
                s.close()
            else:
                try:
                    act.locked = True
                    act.locked_by = getpass.getuser()
                    s.commit()
                    try:
                        self.application = DetailActAPP(self.Session, True, act.id_activite)
                        self.application.finished.connect(self.do_something)
                    except Exception as err:
                        logger.error(err)
                except Exception as err:
                    logger.error(err)
                finally:
                    s.close()

    def open_import(self):
        try:
            self.application = ImportApp(self.Session, "Activités")
            self.application.finished.connect(self.do_something)
        except Exception as err:
            logger.error(err)

    def do_something(self):
        self.init_app()

    def warning_act(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Activités",
            message,
            texte,
            "WARNING"
        )

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.finished.emit(True)
        a0.accept()