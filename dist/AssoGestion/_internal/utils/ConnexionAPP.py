import getpass
import sys
from getpass import getuser

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from loguru import logger

import utils.AccueilAPP as aa
from IHM import connexion
from utils.Auto_Updater_App import AutoUpdateApp
from utils.database import database_connexion, get_version_config
from utils.mail_sender import reset_password, send_error_report
from utils.message import pop_up
from utils.models import assogestion_users, assogestion_app_param
from utils.user_controls import user_email_control, user_database_control


class ConnexionApp(QtWidgets.QMainWindow, connexion.Ui_MyLoginForm):
    """
        Classe principale gérant la fenêtre de connexion de l'application
    """
    def __init__(self, parent: object = None) -> object:
        super(ConnexionApp, self).__init__(parent)
        self.application = None
        try:
            self.error_code = {
                "CTRL_USER_001": ("Le format de l’email n’est pas correct", "WARNING"),
                "CTRL_USER_002": ("L’email saisi ne correspond à aucun utilisateur existant", "WARNING"),
                "CTRL_USER_003": ("L'utilisateur est inactif", "WARNING"),
                "CTRL_USER_004": ('Le mot de passe saisi ne correspond pas pour l’utilisateur', 'WARNING'),
                "LAUNCH_APP_ERROR": ("Connexion impossible à la base de données", "ERROR")
            }
            self.application = None
            self.version = None
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            res, error, self.Session = database_connexion('prod')
            if res != 0:
                send_error_report(getuser(), type(error).__name__, error)
                sys.exit(error)
            self.button_login.setIcon(QIcon("connexion.png"))
            self.button_login.clicked.connect(self.user_login)
            self.butt_lost_password.clicked.connect(self.password_lost)
            self.butt_lost_password.setIcon(QIcon("oublie.png"))
            try:
                self.enrich_auto_user()
            except Exception as err:
                logger.error(err)
            self.show()
        except Exception as err:
            logger.exception(type(err).__name__)
            send_error_report(getuser(), type(err).__name__, err)
            sys.exit("LAUNCH_APP_ERROR")

    def check_version(self):
        s = self.Session()
        version = s.query(assogestion_app_param).filter_by(name_param="version").first()
        if version:

            res, error, self.version = get_version_config()
            if version.value_param != self.version:
                logger.info(f"{self.version} != {version.value_param}")
                self.application = AutoUpdateApp(self.version, version.value_param)
                s.close()
                return False
            else:
                logger.info(f"{self.version} == {version.value_param}")
                s.close()
                return True
        else:
            raise MissingParamException()

    def user_login(self):
        """
            Fonction qui vérifie les identifiants et mot de passe saisis par l'utilisateur afin de le connecter ou de refuser l'ouverture de l'application
        """
        s = self.Session()
        res = s.query(assogestion_users).filter_by(email=self.mail_edit.text()).all()
        s.close()
        code = user_email_control(self.mail_edit.text())
        if self.error_code.get(code) is not None:
            retour = self.error_code.get(code)
            self.erreur_login(code, retour[0], retour[1])
        else:
            code = user_database_control(res, self.password_edit.text())
            if self.error_code.get(code) is not None:
                retour = self.error_code.get(code)
                self.erreur_login(code, retour[0], retour[1])
            else:
                self.application = aa.AccueilApp(self.Session, res)
                self.close()

    def erreur_login(self, message, texte, level):
        """
            Fonction qui renvoie dans une pop-up un message en cas d'erreur remonté par les contrôles des données saisies par l'utilisateur
        :param message:
        :param texte:
        :param level:
        """
        pop_up(
            self,
            "Asso'Gestion - AMSE - Connexion",
            message,
            texte,
            level
        )

    def info_mail(self, message, texte, level):
        """
            Fonction qui renvoie dans une pop-up un message pour indiquer l'envoi du mail lors de l'oublie du mot de passe
        :param message:
        :param texte:
        :param level:
        """
        pop_up(
            self,
            "Asso'Gestion - AMSE - Mot de passe oublié",
            message,
            texte,
            level
        )

    def password_lost(self):
        """
            fonction de réinitialisation du mot de passe
        """
        res = reset_password(self.mail_edit.text())
        if res == 0:
            self.info_mail("Message envoyé", "Un mail a été envoyé à l'administrateur", "INFO")
        else:
            self.info_mail("Une erreur est survenue", "Erreur lors de l'envoi du mail, veuillez contacter l'administrateur", "ERROR")

    def enrich_auto_user(self):
        s = self.Session()
        username = getpass.getuser()

        user = s.query(assogestion_users).filter_by(username=username).first()
        if user:
            logger.success(f"Enrichissement des données de connexion avec le username {username}")
            self.mail_edit.setText(user.email)
            self.password_edit.setText(user.password)
        else:
            logger.error("Impossible d'enrichir les données de l'utilisateur")
        s.close()


class MissingParamException(Exception):
    message: str = "Le paramètre 'Version' n'existe pas dans la base de données"
    def __str__(self):
        return f"{self.message}"

class OldVersionException(Exception):
    message: str = "La version installée ne correspond pas à une version actuellement en production"
    def __str__(self):
        return f"{self.message}"
