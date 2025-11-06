import getpass
import os

from PyQt5 import QtWidgets, QtGui
from loguru import logger

import IHM.auto_updater_app
from utils import UpdateThread
from utils.message import pop_up


class AutoUpdateApp(QtWidgets.QDialog, IHM.auto_updater_app.Ui_Dialog):

    def __init__(self, v_install, v_user, parent=None):
        try:
            super(AutoUpdateApp, self).__init__(parent)
            self.traitement = ""
            self.v_install = v_install
            self.v_user = v_user
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.butt_ok.clicked.connect(self.traitement_thread)
            self.butt_cancel.clicked.connect(self.press_cancel)
            self.textEdit.setText(f"""
        Bonjour {getpass.getuser()},
        Votre version d'AssoGestion nécessite une mise à jour pour fonctionner.
        Version actuelle: {self.v_install}
        Version à installer: {self.v_user}
        
        Cliquez sur Ok pour la lancer. 
        """)
            self.show()
        except Exception as err:
            logger.error(err)

    def countchanged(self, value):
        self.progressBar.setValue(value)

    def stepchanged(self, step):
        self.label.setText(step)

    def getfin(self, param):
        try:
            flag, name = param
            if flag:
                self.close()
                os.system(name)
        except Exception as err:
            logger.error(err)
    def erreur(self, texte):
        """
            Fonction qui renvoie dans une pop-up un message en cas d'erreur remonté par les contrôles des données saisies par l'utilisateur
        :param texte:
        """
        try:
            pop_up(
                self,
                "Asso'Gestion - AMSE - Mise à jour",
                "Une erreur est survenue pendant la mise à jour",
                    texte,
                "INFO"
            )
        except Exception as err:
            logger.error(err)

    def traitement_thread(self):
        try:
            self.butt_cancel.setEnabled(False)
            self.traitement = UpdateThread.TraiterFichier(self.v_user)
            self.traitement.countchanged.connect(self.countchanged)
            self.traitement.stepchanged.connect(self.stepchanged)
            self.traitement.erreur.connect(self.erreur)
            self.traitement.flagfin.connect(self.getfin)
            self.traitement.start()
        except Exception as err:
            print(err)

    def press_cancel(self):
        self.close()
