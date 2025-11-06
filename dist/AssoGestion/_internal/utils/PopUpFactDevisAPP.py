from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog

from IHM import pop_up_dev_fac
from utils.ListeDevisApp import ListeDevisAPP
from utils.ListeFacturesApp import ListeFacturesAPP


class PopupFacDevApp(QDialog, pop_up_dev_fac.Ui_Dialog):

    def __init__(self, session, parent=None):
        super(PopupFacDevApp, self).__init__(parent)
        self.application = None
        self.Session = session
        self.setupUi(self)
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(self.icon)
        self.button_facture.clicked.connect(self.open_facture)
        self.button_devis.clicked.connect(self.open_devis)
        self.button_retour.setIcon(QIcon('retour.png'))
        self.button_retour.clicked.connect(self.close)
        self.show()

    def open_facture(self):
        self.application = ListeFacturesAPP(self.Session)
        self.close()

    def open_devis(self):
        self.application = ListeDevisAPP(self.Session)
        self.close()
