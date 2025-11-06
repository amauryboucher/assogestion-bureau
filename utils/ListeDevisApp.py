from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem
from loguru import logger

from IHM import liste_devis
from utils.DetailDevisApp import DetailDevisAPP
from utils.message import pop_up
from utils.models import assogestion_devis


class ListeDevisAPP(QtWidgets.QMainWindow, liste_devis.Ui_liste_devis):
    finished = pyqtSignal(bool)
    def __init__(self, Session, parent=None):
        super(ListeDevisAPP, self).__init__(parent)
        try:
            self.application = None
            self.s = Session()
            self.Session = Session
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.init_app()
            self.button_creation_devis.clicked.connect(self.open_new_devis)
            self.tab_devis.doubleClicked.connect(self.open_devis)
            self.button_retour.setIcon(QIcon('retour.png'))
            self.button_retour.clicked.connect(self.close)
            self.show()
        except Exception as err:
            logger.error(err)

    def init_app(self):
        self.show()
        res = self.s.query(assogestion_devis).order_by(assogestion_devis.numero_devis).all()
        self.tab_devis.clear()
        self.tab_devis.setRowCount(0)
        self.tab_devis.setColumnCount(4)
        self.tab_devis.setHorizontalHeaderLabels(["Numéro", "Code client", "Date", "Total"])
        if res:
            for i, r in enumerate(res):
                self.tab_devis.insertRow(i)
                result = r.numero_devis, r.code_client, r.date, r.total_ttc
                for j, res in enumerate(result):
                    self.tab_devis.setItem(i, j, QTableWidgetItem(f'{result[j]}'))
        self.tab_devis.resizeColumnsToContents()

    def open_new_devis(self):
        pass
        #try:
        #    dev = self.s.query(assogestion_devis).order_by(assogestion_devis.id).all()
        #    if dev:
        #        id_devis = int(dev[-1].numero_devis.split('DEV')[1]) + 1
        #    else:
        #        id_devis = 1
        #    logger.info(f"DEV000{id_devis}")
        #    temp_dev = self.s.query(assogestion_temp_devis).filter_by(numero_devis=f"DEV000{id_devis}").first()
        #    if temp_dev:
        #        logger.warning("devis déjà existant")
        #    else:
        #        dev = assogestion_temp_devis(
        #            numero_devis=f"DEV000{id_devis}",
        #            date=datetime.now()
        #        )
        #
        #        self.s.add(dev)
        #        self.s.commit()
        #        temp_dev = self.s.query(assogestion_temp_devis).filter_by(numero_devis=f"DEV000{id_devis}").first()
        #        if temp_dev:
        #            ligne_dev = assogestion_temp_ligne_devis(
        #                id_devis=temp_dev.id
        #            )
        #            self.s.add(ligne_dev)
        #            self.s.commit()
        #            self.application = DetailDevisAPP(self.s, self.Session, False, temp_dev)
        #            self.application.finished.connect(self.init_app)
        #except Exception as err:
        #    logger.error(err)

    def open_devis(self):
        try:
            if self.tab_devis.currentItem().isSelected():
                if self.tab_devis.currentItem().column() == 0:
                    dev = self.s.query(assogestion_devis).filter_by(
                        numero_devis=self.tab_devis.currentItem().text()).first()
                    if dev:
                        self.application = DetailDevisAPP(self.s, self.Session, True, dev)
                        self.application.finished.connect(self.init_app)
        except Exception as err:
            logger.error(err)

    def warning_fac(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Devis",
            message,
            texte,
            "WARNING"
        )

    def closeEvent(self, event):
        self.s.close()
        self.finished.emit(True)
        event.accept()



