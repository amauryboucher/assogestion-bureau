from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem
from loguru import logger

from IHM import gest_user
from utils.DetailUserApp import DetailUserAPP
from utils.message import pop_up
from utils.models import assogestion_users


class ListeUsersAPP(QtWidgets.QMainWindow, gest_user.Ui_gest_user):
    finished = pyqtSignal(bool)
    def __init__(self, Session, parent=None):
        super(ListeUsersAPP, self).__init__(parent)
        try:
            self.application = None
            self.Session = Session
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.button_retour.setIcon(QIcon('retour.png'))
            self.button_retour.clicked.connect(self.close)
            self.tab_user.doubleClicked.connect(self.open_edit_user)
            self.button_add_user.clicked.connect(self.open_new_user)
            self.init_app()
            self.show()
        except Exception as err:
            logger.error(err)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.finished.emit(True)
        a0.accept()

    def init_app(self):
        s = self.Session()
        users = s.query(assogestion_users).all()
        self.tab_user.clear()
        self.tab_user.setRowCount(0)
        if users:
            self.tab_user.setColumnCount(4)
            self.tab_user.setHorizontalHeaderLabels(["Email", "Nom d'utilisateur", "Actif", "Verrouillé"])
            for i, r in enumerate(users):
                self.tab_user.insertRow(i)
                result = r.email, r.username, self.bool_to_str(r.actif), self.bool_to_str(r.locked)
                for j, res in enumerate(result):
                    self.tab_user.setItem(i, j, QTableWidgetItem(f'{result[j]}'))
            self.tab_user.resizeColumnsToContents()
        s.close()

    def open_edit_user(self):
        s = self.Session()
        res = s.query(assogestion_users).filter_by(email=self.tab_user.currentItem().text()).first()
        self.application = DetailUserAPP(self.Session, True, res)
        self.application.finished.connect(self.do_something)
        self.hide()
        s.close()

    def open_new_user(self):
        s = self.Session()
        self.application = DetailUserAPP(self.Session, False, None)
        self.application.finished.connect(self.do_something)
        self.hide()
        s.close()
    def do_something(self):
        logger.info("do something")
        self.init_app()
        self.show()

    def warning_user(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Utilisateurs",
            message,
            texte,
            "WARNING"
        )
    @staticmethod
    def bool_to_str(value):
        if value:
            return "Oui"
        else:
            return "Non"

