from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem
from loguru import logger

from IHM import liste_facture
# from utils.DetailFactureApp import DetailFactAPP
from utils.DetailFactureAppV2 import DetailFactAPPV2
from utils.format_input import object_as_dict
from utils.message import pop_up
from utils.models import assogestion_facture


class ListeFacturesAPP(QtWidgets.QMainWindow, liste_facture.Ui_liste_facture):
    finished = pyqtSignal(bool)
    def __init__(self, Session, parent=None):
        super(ListeFacturesAPP, self).__init__(parent)
        try:
            self.application = None
            self.Session = Session
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.init_app()
            self.button_creation_facture.clicked.connect(self.open_new_facture)
            self.tab_facture.doubleClicked.connect(self.open_facture)
            self.button_retour.setIcon(QIcon('retour.png'))
            self.button_retour.clicked.connect(self.close)
            self.show()
        except Exception as err:
            logger.error(err)

    def init_app(self):
        s = self.Session()
        res = s.query(assogestion_facture).order_by(assogestion_facture.inv_no).all()
        self.tab_facture.clear()
        self.tab_facture.setRowCount(0)
        self.tab_facture.setColumnCount(4)
        self.tab_facture.setHorizontalHeaderLabels(["Numéro", "Code client", "Date", "Total"])
        if res:
            for i, r in enumerate(res):
                self.tab_facture.insertRow(i)
                result = r.inv_number_full, r.code_client, r.date, r.total_ttc
                for j, res in enumerate(result):
                    self.tab_facture.setItem(i, j, QTableWidgetItem(f'{result[j]}'))
        self.tab_facture.resizeColumnsToContents()
        s.close()

    def closeEvent(self, a0):
        self.finished.emit(True)
        a0.accept()

    def open_new_facture(self):
        s = self.Session()
        try:
            self.application = DetailFactAPPV2(self.Session, False, {})
            self.application.finished.connect(self.init_app)
        except Exception as err:
            logger.error(err)
        finally:
            s.close()

    def open_facture(self):
        s = self.Session()
        try:
            if self.tab_facture.currentItem().isSelected():
                if self.tab_facture.currentItem().column() == 0:
                    fac = s.query(assogestion_facture).filter_by(
                        inv_number_full=self.tab_facture.currentItem().text()).first()
                    if fac:
                        fac_dic = object_as_dict(fac)
                        self.application = DetailFactAPPV2(self.Session, True, fac_dic)
                        self.application.finished.connect(self.init_app)
        except Exception as err:
            logger.error(err)
        finally:
            s.close()

    def warning_fac(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Factures",
            message,
            texte,
            "WARNING"
        )
