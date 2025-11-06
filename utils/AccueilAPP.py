from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon, QPixmap
from loguru import logger

from IHM import accueil
from utils.ListeActivitesApp import ListeActivitesAPP
from utils.ListeAdherentApp import ListeAdhAPP
from utils.ListeCollectiviteApp import ListeCollAPP
from utils.ListeCotisationsApp import ListeCotisationsAPP
from utils.ListeDevisApp import ListeDevisAPP
from utils.ListeFacturesApp import ListeFacturesAPP
from utils.ListeUserApp import ListeUsersAPP
from utils.message import pop_up
from utils.read_config import config_info


class AccueilApp(QtWidgets.QMainWindow, accueil.Ui_Accueil):

    def __init__(self, Session, res, parent=None):
        super(AccueilApp, self).__init__(parent)
        try:
            self.application = None
            self.res = res
            self.Session = Session
            self.setupUi(self)
            self.init_ihm()
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            pixmap = QPixmap("logo_abo_tech.png")
            self.label_logo.setPixmap(pixmap)
            self.button_adherents.setIcon(QIcon("adherent.png"))
            self.button_activite.setIcon(QIcon("chariot.png"))
            self.button_cotisation_dons.setIcon(QIcon('piece2.png'))
            self.button_gestion_facture.setIcon(QIcon('bill.png'))
            self.button_gestion_devis.setIcon(QIcon('bill.png'))
            self.button_collectivite.setIcon(QIcon('mairie.png'))
            self.button_gest_user.setIcon(QIcon('user.png'))
            self.button_gest_user.clicked.connect(self.open_liste_user)
            self.button_about.clicked.connect(self.a_propos)
            self.button_about.setIcon(QIcon('licence.png'))
            self.showMaximized()
        except Exception as err:
            logger.error(err)

    @staticmethod
    def none_to_false(input):
        if not input:
            return False
        else:
            return input

    def init_ihm(self):
        for r in self.res:
            self.button_adherents.setEnabled(self.none_to_false(r.adherents))
            self.button_adherents.clicked.connect(self.open_adherents)
            self.button_activite.setEnabled(self.none_to_false(r.activites))
            self.button_activite.clicked.connect(self.open_activite)
            self.button_cotisation_dons.setEnabled(self.none_to_false(r.cotisations))
            self.button_cotisation_dons.clicked.connect(self.open_cotisations)
            self.button_gestion_facture.setEnabled(self.none_to_false(r.devis_facture))
            self.button_gestion_facture.clicked.connect(self.open_facture)
            self.button_gestion_devis.setEnabled(self.none_to_false(r.devis_facture))
            self.button_gestion_devis.clicked.connect(self.open_devis)
            self.button_collectivite.clicked.connect(self.open_collectivite)

    def open_adherents(self):
        self.application = ListeAdhAPP(self.Session, self.res)
        self.application.finished.connect(self.show)
        self.hide()

    def open_collectivite(self):
        self.application = ListeCollAPP(self.Session)
        self.application.finished.connect(self.show)
        self.hide()

    def open_cotisations(self):
        self.application = ListeCotisationsAPP(self.Session)
        self.application.finished.connect(self.show)
        self.hide()

    def open_activite(self):
        try:
            self.application = ListeActivitesAPP(self.Session)
            self.application.finished.connect(self.show)
            self.hide()
        except Exception as err:
            logger.error(err)

    def open_facture(self):
        try:
            self.application = ListeFacturesAPP(self.Session)
            self.application.finished.connect(self.show)
            self.hide()
        except Exception as err:
            logger.error(err)

    def open_devis(self):
        try:
            self.application = ListeDevisAPP(self.Session)
            self.application.finished.connect(self.show)
            self.hide()
        except Exception as err:
            logger.error(err)

    def open_liste_user(self):
        try:
            self.application = ListeUsersAPP(self.Session)
            self.application.finished.connect(self.show)
            self.hide()
        except Exception as err:
            logger.error(err)

    def a_propos(self):
        try:
            info = config_info()
            self.info_about("Information à propos du logiciel", info, "INFO")
        except Exception as err:
            logger.error(err)

    def info_about(self, message, dic, level):
        texte = ""
        for d, v in dic.items():
            texte += f"{d.capitalize()}: {v}\n"
        pop_up(
            self,
            "Asso'Gestion - AMSE - A propos",
            message,
            texte,
            level
        )
