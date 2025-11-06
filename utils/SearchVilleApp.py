from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTableWidgetItem
from loguru import logger
from sqlalchemy import and_

from IHM import search_ville
from utils.message import pop_up
from utils.models import assogestion_annuaire


class SearchVilleApp(QtWidgets.QMainWindow, search_ville.Ui_search_ville):
    cp_sig = pyqtSignal(list)
    def __init__(self, Session, parent=None):
        super(SearchVilleApp, self).__init__(parent)
        try:
            self.setupUi(self)
            self.Session = Session
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.button_search.clicked.connect(self.rechercher_ville)
            self.tab_res_ville.doubleClicked.connect(self.imprime_value)
            self.show()
        except Exception as err:
            logger.error(err)

    def imprime_value(self):
        try:
            value = []
            if self.tab_res_ville.currentItem().column() == 0:
                s = self.Session()
                res = s.query(assogestion_annuaire).filter(and_(assogestion_annuaire.ville.ilike(f"%{self.search_name_edit.text()}%"), assogestion_annuaire.cp==self.tab_res_ville.currentItem().text())).first()
                s.close()
                try:
                    if res:
                        value.append(int(res.cp))
                        value.append(res.ville.upper())
                        self.cp_sig.emit(value)
                except Exception as err:
                    logger.error(err)
        except Exception as err:
            logger.error(err)
    def rechercher_ville(self):
        try:
            self.tab_res_ville.clear()
            self.tab_res_ville.setRowCount(0)
            self.tab_res_ville.setColumnCount(2)
            self.tab_res_ville.setHorizontalHeaderLabels(
                ["Code postal", "Ville"])
            if self.search_name_edit.text() != "":
                s = self.Session()
                res = s.query(assogestion_annuaire).filter(assogestion_annuaire.ville.ilike(f"%{self.search_name_edit.text()}%")).order_by(assogestion_annuaire.cp).all()
                if res:
                    for i, r in enumerate(res):
                        self.tab_res_ville.insertRow(i)
                        result = r.cp, r.ville
                        for j, res in enumerate(result):
                            self.tab_res_ville.setItem(i, j, QTableWidgetItem(f'{result[j]}'))
                    self.tab_res_ville.resizeColumnsToContents()
            else:
                try:
                    self.erreur_saisie("Recherche impossible", "Le champ ville ne peut pas être vide")
                except Exception as err:
                    logger.error(err)
        except Exception as err:
            logger.error(err)
    def erreur_saisie(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Recherche ville",
            message,
            texte,
            "ERROR"
        )
