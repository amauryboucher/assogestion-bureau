import getpass
import os
import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from loguru import logger

import IHM.auto_updater_app
from utils import UpdateThread
from utils.message import pop_up
from utils.config_loader import resource_dir


class AutoUpdateApp(QtWidgets.QDialog, IHM.auto_updater_app.Ui_Dialog):
    """
    Fenêtre de mise à jour automatique de l'application AssoGestion.
    Compare les versions et déclenche le téléchargement/mise à jour via UpdateThread.
    """

    def __init__(self, v_install, v_user, parent=None):
        super(AutoUpdateApp, self).__init__(parent)

        try:
            self.v_install = v_install
            self.v_user = v_user
            self.traitement = None

            self.setupUi(self)
            self._setup_ui()
            self._connect_signals()

            self._display_intro_message()
            self.show()

        except Exception as err:
            logger.exception(f"Erreur d'initialisation AutoUpdateApp : {err}")
            pop_up(
                self,
                "Erreur de mise à jour",
                "Erreur à l’ouverture du module de mise à jour.",
                str(err),
                "ERROR",
            )

    # -------------------- Configuration UI -------------------- #
    def _setup_ui(self):
        """Charge les icônes et configure les composants graphiques."""
        base = resource_dir()
        self.icon = QtGui.QIcon(str(base / "logo_abo_tech.png"))
        self.setWindowIcon(self.icon)
        self.butt_ok.setIcon(QIcon(str(base / "connexion.png")))
        self.butt_cancel.setIcon(QIcon(str(base / "oublie.png")))
        self.progressBar.setValue(0)

    def _connect_signals(self):
        """Connecte les signaux aux slots."""
        self.butt_ok.clicked.connect(self.traitement_thread)
        self.butt_cancel.clicked.connect(self.press_cancel)

    def _display_intro_message(self):
        """Affiche le message d’introduction personnalisé."""
        self.textEdit.setText(
            f"""
Bonjour {getpass.getuser()},
Votre version d'AssoGestion nécessite une mise à jour.

📦 Version actuelle : {self.v_install}
🆕 Version à installer : {self.v_user}

Cliquez sur "OK" pour lancer la mise à jour.
        """
        )

    # -------------------- Slots de progression -------------------- #
    def countchanged(self, value: int):
        self.progressBar.setValue(value)

    def stepchanged(self, step: str):
        self.label.setText(step)

    def getfin(self, param):
        """Slot appelé à la fin du thread de mise à jour."""
        try:
            flag, name = param
            if flag:
                logger.success(f"Mise à jour terminée avec succès. Lancement de {name}.")
                self.close()
                os.system(name)
            else:
                logger.error(f"La mise à jour a échoué : {name}")
                self.erreur(name)
        except Exception as err:
            logger.exception(f"Erreur lors de la finalisation : {err}")
            self.erreur(str(err))

    def erreur(self, texte):
        """Affiche une pop-up d’erreur."""
        pop_up(
            self,
            "Asso'Gestion - Mise à jour",
            "Une erreur est survenue pendant la mise à jour",
            texte,
            "ERROR",
        )

    # -------------------- Thread principal -------------------- #
    def traitement_thread(self):
        """Lance le thread de mise à jour (téléchargement, copie, etc.)."""
        try:
            self.butt_cancel.setEnabled(False)
            self.butt_ok.setEnabled(False)
            self.traitement = UpdateThread.TraiterFichier(self.v_user)

            # Connexion des signaux
            self.traitement.countchanged.connect(self.countchanged)
            self.traitement.stepchanged.connect(self.stepchanged)
            self.traitement.erreur.connect(self.erreur)
            self.traitement.flagfin.connect(self.getfin)

            self.traitement.start()
            logger.info("Thread de mise à jour démarré.")
        except Exception as err:
            logger.exception(f"Erreur lors du lancement du thread de mise à jour : {err}")
            self.erreur(str(err))

    def press_cancel(self):
        """Ferme la fenêtre sans exécuter la mise à jour."""
        logger.warning("Mise à jour annulée par l'utilisateur.")
        self.close()
