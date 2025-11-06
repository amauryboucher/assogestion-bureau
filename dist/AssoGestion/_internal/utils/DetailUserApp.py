from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from loguru import logger
from sqlalchemy.exc import IntegrityError

from IHM import detail_user
from utils.message import pop_up
from utils.models import assogestion_users
from utils.user_controls import user_email_control, user_username_control, user_password_control


class DetailUserAPP(QtWidgets.QMainWindow, detail_user.Ui_detail_user):
    finished = pyqtSignal(bool)

    def __init__(self, Session, edit, user, parent=None):
        super(DetailUserAPP, self).__init__(parent)
        try:
            self.dic_error = {
                "CTRL_USER_001":"Le format de l'email n'est pas valide",
                "CTRL_USER_002": "Le nom d'utilisateur ne doit pas être vide",
                "CTRL_USER_003": "Le mot de passe doit avoir au moins 6 caractères",
                "CTRL_USER_005": "Le mot de passe doit contenir au moins un nombre",
                "CTRL_USER_006": "Le mot de passe doit contenir au moins une majuscule",
                "CTRL_USER_007": "Le mot de passe doit contenir au moins une minuscule",
                "CTRL_USER_008": "Le mot de passe doit avoir au moins un caractère spécial parmis les suivants: $@#!",
                "": ""
            }
            self.Session = Session
            self.edit = edit
            self.user = user
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            if user:
                self.init_app()
            self.button_valider.setIcon(QIcon("save.png"))
            self.button_valider.clicked.connect(self.save)
            self.button_retour.setIcon(QIcon('retour.png'))
            self.button_retour.clicked.connect(self.close)
            self.show()
        except Exception as err:
            logger.error(err)

    def init_app(self):
        s = self.Session()
        res = s.query(assogestion_users).filter_by(email=self.user.email).first()
        self.mail_edit.setText(res.email)
        self.username_edit.setText(res.username)
        self.password_edit.setText(res.password)
        self.cb_actif.setChecked(res.actif)
        self.cb_locked.setChecked(res.locked)
        self.cb_adh.setChecked(res.adherents)
        self.cb_act.setChecked(res.activites)
        self.cb_cot.setChecked(res.cotisations)
        self.cb_devis.setChecked(res.devis_facture)
        self.cb_users.setChecked(res.utilisateurs)
        s.close()

    def save(self):
        try:
            errors_ctrl = []
            error_message = ""
            ctrl_user_001 = user_email_control(self.mail_edit.text())
            self.error_mail.setText(self.dic_error.get(ctrl_user_001))
            ctrl_user_002 = user_username_control(self.username_edit.text())
            self.error_username.setText(self.dic_error.get(ctrl_user_002))
            ctrl_user_003 = user_password_control(self.password_edit.text())
            if ctrl_user_001 != "":
                errors_ctrl.append(f"{ctrl_user_001}: {self.dic_error.get(ctrl_user_001)}")
            if ctrl_user_002 != "":
                errors_ctrl.append(f"{ctrl_user_002}: {self.dic_error.get(ctrl_user_002)}")
            for c in ctrl_user_003:
                errors_ctrl.append(f"{c}: {self.dic_error.get(c)}")
                error_message += f"{self.dic_error.get(c)}\n"
            logger.error(error_message)
            self.error_password.setText(error_message)
            message = ""
            for e in errors_ctrl:
                if e != ": ":
                    message += f"{e}\n"
            if errors_ctrl:
                self.erreur_saisie("Enregistrement impossible", message)
            else:
                s = self.Session()
                if self.edit:
                    user = s.query(assogestion_users).filter_by(email=self.user.email).first()
                    user.email = self.mail_edit.text()
                    user.username = self.username_edit.text()
                    user.password = self.password_edit.text()
                    user.actif = self.cb_actif.isChecked()
                    user.locked = self.cb_locked.isChecked()
                    user.adherents = self.cb_adh.isChecked()
                    user.activites = self.cb_act.isChecked()
                    user.cotisations = self.cb_cot.isChecked()
                    user.devis_facture = self.cb_devis.isChecked()
                    user.utilisateurs = self.cb_users.isChecked()
                    s.commit()
                else:
                    try:
                        new_user = assogestion_users(
                            email=self.mail_edit.text(),
                            username = self.username_edit.text(),
                            password = self.password_edit.text(),
                            actif = self.cb_actif.isChecked(),
                            locked = self.cb_locked.isChecked(),
                            adherents = self.cb_adh.isChecked(),
                            activites = self.cb_act.isChecked(),
                            cotisations = self.cb_cot.isChecked(),
                            devis_facture = self.cb_devis.isChecked(),
                            utilisateurs = self.cb_users.isChecked(),
                        )
                        s.add(new_user)
                        s.commit()
                    except IntegrityError as err:
                        logger.error(err.orig.diag.message_detail)
                        self.erreur_saisie("Enregistrement impossible", str(err.orig.diag.message_detail))
                s.close()
                self.close()
        except Exception as err:
            logger.error(err)

    def closeEvent(self, event):
        self.finished.emit(True)
        event.accept()

    def erreur_saisie(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Utilisateur",
            message,
            texte,
            "ERROR"
        )
