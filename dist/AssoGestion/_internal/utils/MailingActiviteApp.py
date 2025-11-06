from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog
from loguru import logger

from IHM import mailing
from utils.TraitementEmail import TraiterEmail
from utils.message import pop_up
from utils.models import assogestion_adherents


class MailingAPP(QtWidgets.QMainWindow, mailing.Ui_mailing):

    def __init__(self, act, Session, liste_dest, parent=None):
        super(MailingAPP, self).__init__(parent)
        try:
            self.Session = Session
            self.traitement = None
            self.act = act
            self.liste = liste_dest
            self.liste_dest = []
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.butt_add_dest.hide()
            self.init_app()

            self.butt_add_pj.clicked.connect(self.add_pj)
            self.button_envoi.clicked.connect(self.send_mail)
            self.button_retour.setIcon(QIcon('retour.png'))
            self.button_retour.clicked.connect(self.close)
            self.show()
        except Exception as err:
            logger.error(err)

    def init_app(self):

        s = self.Session()
        for dest in self.liste:
            a = s.query(assogestion_adherents).filter_by(code_adherent=dest.code_adherent).first()
            self.liste_destinataire.addItem(a.email_adherent)
        for index in range(self.liste_destinataire.count()):
            self.liste_dest.append(self.liste_destinataire.item(index).text())
        s.close()

    def add_pj(self):
        try:
            fname = QFileDialog.getOpenFileName()
            self.liste_pj.addItem(fname[0])
        except Exception as err:
            logger.error(err)

    def set_max(self, value):
        self.pb.setMaximum(value)

    def set_value(self, value):
        self.pb.setValue(value)

    def finished(self, flag):
        try:
            if flag:
                pop_up(
                    self,
                    "AssoGestion - AMSE - Activités",
                    "Email envoyé",
                    "L'email a été envoyé avec succès",
                    "INFO"
                )
                self.close()
        except Exception as err:
            logger.error(err)

    def send_mail(self):
        liste_pj = []
        if self.sujet_edit.text() != "":
            sujet_mail = self.sujet_edit.text()
        else:
            sujet_mail = f"[AMSE] Information sur l'activité {self.act}"

        if self.mail_message_edit.toPlainText() != "":
            logger.info(self.liste_pj.count())
            for index in range(self.liste_pj.count()):
                pj = self.liste_pj.item(index).text()
                nom_pj = self.liste_pj.item(index).text().split('/')[-1]
                liste_pj.append((nom_pj, pj))
            try:
                self.traitement = TraiterEmail(self.liste_dest, liste_pj, sujet_mail,
                                               self.mail_message_edit.toPlainText())
                self.traitement.line_count_max.connect(self.set_max)
                self.traitement.line_count_changed.connect(self.set_value)
                self.traitement.flag_fin.connect(self.finished)
                self.traitement.start()
            except Exception as err:
                logger.error(err)
