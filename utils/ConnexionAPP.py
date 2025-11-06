import getpass
import sys
from getpass import getuser

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from loguru import logger

import utils.AccueilAPP as aa
from IHM import connexion
from utils.Auto_Updater_App import AutoUpdateApp
from utils.config_loader import get_config_path, resource_dir
from utils.database import database_connexion, get_version_config
from utils.mail_sender import reset_password, send_error_report
from utils.message import pop_up
from utils.models import assogestion_users, assogestion_app_param
from utils.user_controls import user_email_control, user_database_control


class ConnexionApp(QtWidgets.QMainWindow, connexion.Ui_MyLoginForm):
    """
    Fenêtre principale de connexion de l'application AssoGestion.
    """
    def __init__(self, parent: object = None) -> object:
        super(ConnexionApp, self).__init__(parent)
        self.application = None
        self.version = None

        try:
            self.error_code = {
                "CTRL_USER_001": ("Le format de l’email n’est pas correct", "WARNING"),
                "CTRL_USER_002": ("L’email saisi ne correspond à aucun utilisateur existant", "WARNING"),
                "CTRL_USER_003": ("L'utilisateur est inactif", "WARNING"),
                "CTRL_USER_004": ("Le mot de passe saisi ne correspond pas pour l’utilisateur", "WARNING"),
                "LAUNCH_APP_ERROR": ("Connexion impossible à la base de données", "ERROR")
            }

            # --- UI setup ---
            self.setupUi(self)
            base = resource_dir()
            self.icon = QtGui.QIcon(str(base / "logo_abo_tech.png"))
            self.setWindowIcon(self.icon)
            self.button_login.setIcon(QIcon(str(base / "connexion.png")))
            self.butt_lost_password.setIcon(QIcon(str(base / "oublie.png")))
            self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)

            # --- Connexion à la BDD ---
            res, error, self.Session = database_connexion("prod", config_path=get_config_path())
            if res != 0:
                pop_up(self, "Erreur", "Connexion impossible à la base de données", str(error), "ERROR")
                send_error_report(getuser(), type(error).__name__, error)
                sys.exit(1)

            # --- Vérification de la version ---
            if not self.check_version():
                logger.warning("Arrêt de l'application : version obsolète ou erreur de version.")
                sys.exit(0)

            # --- Signaux / slots ---
            self.button_login.clicked.connect(self.user_login)
            self.butt_lost_password.clicked.connect(self.password_lost)

            # --- Pré-remplissage utilisateur local ---
            try:
                self.enrich_auto_user()
            except Exception as err:
                logger.error(f"Erreur enrichissement user : {err}")

            self.show()

        except Exception as err:
            logger.exception(f"Erreur critique : {err}")
            send_error_report(getuser(), type(err).__name__, err)
            sys.exit("LAUNCH_APP_ERROR")

    # -------------------- Vérification de version -------------------- #
    def check_version(self):
        """Compare la version locale (INI) à celle en base et déclenche la mise à jour si besoin."""
        logger.info("Vérification de la version de l'application...")

        s = self.Session()
        try:
            version_param = s.query(assogestion_app_param).filter_by(name_param="version").first()
            if not version_param:
                raise MissingParamException()

            res, error, self.version = get_version_config(get_config_path())
            if res != 0 or not self.version:
                logger.error(f"Impossible de lire la version locale : {error}")
                pop_up(self, "Erreur de version", "Impossible de lire la version locale", str(error), "ERROR")
                send_error_report(getuser(), "Erreur de version", f"Impossible de lire la version locale : {error}")
                return False

            if version_param.value_param != self.version:
                logger.warning(f"Version locale {self.version} ≠ version distante {version_param.value_param}")
                #send_error_report(getuser(), "BAD VERSION",
                #                  f"Version locale {self.version} ≠ version distante {version_param.value_param}")
                dlg = AutoUpdateApp(self.version, version_param.value_param, parent=self)
                if dlg.exec_() == QtWidgets.QDialog.Accepted:
                    logger.info("Mise à jour effectuée avec succès.")
                else:
                    logger.warning("Mise à jour annulée ou échouée.")
                return False
            else:
                logger.success(f"Version locale {self.version} == version distante {version_param.value_param}")
                return True

        except MissingParamException as err:
            logger.error(str(err))
            pop_up(self, "Erreur", str(err), "Section manquante dans la base de données", "ERROR")
            return False

        except Exception as err:
            logger.exception(f"Erreur lors de la vérification de version : {err}")
            send_error_report(getuser(), type(err).__name__, err)
            return False

        finally:
            s.close()

    # -------------------- Connexion utilisateur -------------------- #
    def user_login(self):
        """Vérifie les identifiants utilisateur et ouvre l’application."""
        s = self.Session()
        res = s.query(assogestion_users).filter_by(email=self.mail_edit.text()).all()
        s.close()

        code = user_email_control(self.mail_edit.text())
        if self.error_code.get(code):
            message, texte, level = self.error_code[code]
            self.erreur_login(code, texte, level)
            return

        code = user_database_control(res, self.password_edit.text())
        if self.error_code.get(code):
            message, texte, level = self.error_code[code]
            self.erreur_login(code, texte, level)
            return

        self.application = aa.AccueilApp(self.Session, res)
        self.close()

    # -------------------- Fonctions diverses -------------------- #
    def erreur_login(self, message, texte, level):
        pop_up(self, "Asso'Gestion - Connexion", message, texte, level)

    def info_mail(self, message, texte, level):
        pop_up(self, "Asso'Gestion - Mot de passe oublié", message, texte, level)

    def password_lost(self):
        res = reset_password(self.mail_edit.text())
        if res == 0:
            self.info_mail("Message envoyé", "Un mail a été envoyé à l'administrateur", "INFO")
        else:
            self.info_mail("Erreur", "Erreur lors de l'envoi du mail, veuillez contacter l'administrateur", "ERROR")

    def enrich_auto_user(self):
        """Préremplit automatiquement l'utilisateur courant s’il existe dans la base."""
        s = self.Session()
        username = getpass.getuser()
        user = s.query(assogestion_users).filter_by(username=username).first()
        if user:
            logger.success(f"Enrichissement automatique avec le username {username}")
            self.mail_edit.setText(user.email)
            self.password_edit.setText(user.password)
        else:
            logger.warning(f"Aucun utilisateur trouvé pour {username}")
        s.close()


# -------------------- Exceptions personnalisées -------------------- #
class MissingParamException(Exception):
    message: str = "Le paramètre 'Version' n'existe pas dans la base de données"
    def __str__(self):
        return self.message


class OldVersionException(Exception):
    message: str = "La version installée ne correspond pas à une version actuellement en production"
    def __str__(self):
        return self.message
