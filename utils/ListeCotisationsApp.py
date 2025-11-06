import getpass

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem
from loguru import logger

from IHM import liste_tarif
from utils.DetailCotisationApp import DetailCotAPP
from utils.ImportAPP import ImportApp
from utils.message import pop_up
from utils.models import assogestion_cotisation


class ListeCotisationsAPP(QtWidgets.QMainWindow, liste_tarif.Ui_liste_tarif):
    finished = pyqtSignal(bool)

    def __init__(self, Session, parent=None):
        super(ListeCotisationsAPP, self).__init__(parent)
        try:
            self.application = None
            self.Session = Session
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.button_creation_cotisation.clicked.connect(self.open_new_cotisation)
            self.button_creation_cotisation.setIcon(QIcon("creer.png"))
            self.tab_cotisation.doubleClicked.connect(self.open_edit_cotisation)
            #self.button_import_cotisation.clicked.connect(self.open_import)
            #self.button_import_cotisation.setIcon(QIcon("importer.png"))
            self.button_retour.clicked.connect(self.close)
            self.button_retour.setIcon(QIcon('retour.png'))
            self.button_retour.clicked.connect(self.close)
            self.init_app()
            self.show()
        except Exception as err:
            logger.error(err)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.finished.emit(True)
        a0.accept()

    def init_app(self):
        s = self.Session()
        res = s.query(assogestion_cotisation).order_by(assogestion_cotisation.nom_cotisation).all()
        self.tab_cotisation.clear()
        self.tab_cotisation.setRowCount(0)
        if res:
            self.tab_cotisation.setColumnCount(6)
            self.tab_cotisation.setHorizontalHeaderLabels(["Type", "Début", "Fin", "Tarif", "Bulletin", "Dons"])
            for i, r in enumerate(res):
                self.tab_cotisation.insertRow(i)
                result = r.nom_cotisation, r.date_debut_cotisation, r.date_fin_cotisation, r.tarif, r.tarif_bulletin, r.dons
                for j, res in enumerate(result):
                    self.tab_cotisation.setItem(i, j, QTableWidgetItem(f'{result[j]}'))
            self.tab_cotisation.resizeColumnsToContents()
        s.close()

    def open_new_cotisation(self):
        self.application = DetailCotAPP(self.Session, False, None)
        self.application.finished.connect(self.do_something)

    def open_edit_cotisation(self):
        s = self.Session()
        cot = None
        if self.tab_cotisation.currentItem().isSelected():
            if self.tab_cotisation.currentItem().column() == 0:
                cot = s.query(assogestion_cotisation).filter_by(
                    nom_cotisation=self.tab_cotisation.currentItem().text()).first()

        if cot:
            if cot.locked:
                self.warning_cot("Modification impossible",
                                 f"La cotisation est déjà en cours de modification par {cot.locked_by}")
                s.close()
            else:
                try:
                    cot.locked = True
                    cot.locked_by = getpass.getuser()
                    s.commit()
                    try:
                        self.application = DetailCotAPP(self.Session, True, cot.id_cotisation)
                        self.application.finished.connect(self.do_something)
                    except Exception as err:
                        logger.error(err)
                except Exception as err:
                    logger.error(err)
                finally:
                    s.close()

    def open_import(self):
        try:
            self.application = ImportApp(self.Session, "Cotisations")
            self.application.finished.connect(self.do_something)
        except Exception as err:
            logger.error(err)

    def do_something(self):
        logger.info("do something")
        self.init_app()

    def warning_cot(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Cotisations",
            message,
            texte,
            "WARNING"
        )
