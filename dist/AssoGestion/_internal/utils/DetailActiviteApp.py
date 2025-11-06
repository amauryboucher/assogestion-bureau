from datetime import datetime

import openpyxl
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QFileDialog
from loguru import logger

from IHM import detail_activite
from utils.ActiviteAddAdhApp import ActiviteAddAdhAPP
from utils.MailingActiviteApp import MailingAPP
from utils.activite_control import ACT_CTRL_001, ACT_CTRL_002
from utils.format_input import format_date_to_database
from utils.message import pop_up
from utils.models import assogestion_activite, assogestion_act_adh, assogestion_adherents


class DetailActAPP(QtWidgets.QMainWindow, detail_activite.Ui_detail_activite):
    finished = pyqtSignal(bool)

    def __init__(self, Session, edit, act, parent=None):
        super(DetailActAPP, self).__init__(parent)
        try:
            self.Session = Session
            self.application = None
            self.edit = edit
            self.act = act
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.set_tab_participant_active()
            self.init_app()
            self.button_save.clicked.connect(self.save)
            self.button_add_adherent.setIcon(QIcon("creer.png"))
            self.button_mail_participant.setIcon(QIcon("invitation.png"))
            self.button_save.setIcon(QIcon("save.png"))
            self.button_add_adherent.clicked.connect(self.open_add_participant)
            self.tab_participant.doubleClicked.connect(self.remove_participant)
            self.button_mail_participant.clicked.connect(self.send_mail)
            self.button_retour.setIcon(QIcon('retour.png'))
            self.button_retour.clicked.connect(self.close)
            self.button_export.clicked.connect(self.export_participant)
            self.dic_error = {
                "ACT_CTRL_001": "Le libellé de l'activité ne peut pas être vide",
                "ACT_CTRL_002": "Le nombre maximum de participant doit être différent de 0",
                "": ""
            }
            self.show()
        except Exception as err:
            logger.error(err)

    def export_participant(self):
        s = self.Session()
        try:
            act = s.query(assogestion_activite).filter_by(id_activite=self.act).first()
            q = s.query(assogestion_act_adh).filter_by(id_activite=self.act).all()
            wb = openpyxl.Workbook()
            sheet = wb.active
            sheet.title = f"Export Participants"
            sheet[f"A1"].value = "Code adhérent"
            sheet[f"B1"].value = "Nom adhérent"
            sheet[f"C1"].value = "Prénom adhérent"
            sheet[f"D1"].value = "Nombre participant"
            sheet[f"E1"].value = "Montant activité"
            sheet[f"F1"].value = "A régler"
            for i, r in enumerate(q, 2):
                res_adh = s.query(assogestion_adherents).filter_by(code_adherent=r.code_adherent).first()
                sheet[f"A{i}"].value = res_adh.code_adherent
                sheet[f"B{i}"].value = res_adh.nom_adherent
                sheet[f"C{i}"].value = res_adh.prenom_adherent
                sheet[f"D{i}"].value = r.nombre
                sheet[f"E{i}"].value = r.montant
                sheet[f"F{i}"].value = self.transco_val(r.a_payer)
            name = QFileDialog.getSaveFileName(self, 'Save File', f"Export_Participants_{act.id_activite}_{datetime.now().strftime('%Y_%m_%d')}.xlsx")
            if name[0] != '':
                wb.save(name[0])
        except Exception as err:
            logger.error(err)
            self.warning_adh("Une erreur est survenue", str(err))

    @staticmethod
    def transco_val(value):
        if value:
            return "Oui"
        else:
            return "Non"
    def set_tab_participant_active(self):
        self.button_add_adherent.setEnabled(self.edit)
        self.button_mail_participant.setEnabled(self.edit)

    def remove_participant(self):
        s = self.Session()
        if self.tab_participant.currentItem().column() == 0:
            adh_act = s.query(assogestion_act_adh).filter_by(code_adherent=self.tab_participant.currentItem().text(),
                                                             id_activite=self.act).first()
            if adh_act:
                act = s.query(assogestion_activite).filter_by(id_activite=self.act).first()
                buttonReply = QMessageBox.question(self, f'Activité {act.libelle_activite}',
                                                   "Voulez-vous supprimer le participant?",
                                                   QMessageBox.Yes | QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    delete_adh_act = s.query(assogestion_act_adh).filter_by(
                        code_adherent=self.tab_participant.currentItem().text(), id_activite=self.act).delete()
                    if act.nb_participant_activite > 0:
                        act.nb_participant_activite -= adh_act.nombre
                    else:
                        act.nb_participant_activite = 0
                    s.commit()
                    self.init_app()
                    self.finished.emit(True)
                if buttonReply == QMessageBox.No:
                    pass

        s.close()

    def open_add_participant(self):
        self.application = ActiviteAddAdhAPP(self.Session, self.act)
        self.application.add.connect(self.init_app)

    def init_app(self):
        self.finished.emit(True)
        if self.edit:
            s = self.Session()
            act = s.query(assogestion_activite).filter_by(
                id_activite=self.act).first()
            self.libelle_edit.setText(act.libelle_activite)
            self.date_debut_edit.setDate(act.date_activite)
            self.nb_part_edit.setText(str(act.nb_participant_activite))
            self.place_max_edit.setText(str(act.nb_participant_max_activite))
            self.tarif_edit.setText(str(act.tarif_activite))
            res_act_adh = s.query(assogestion_act_adh).filter_by(id_activite=self.act).all()
            self.tab_participant.clear()
            self.tab_participant.setRowCount(0)

            self.tab_participant.setColumnCount(6)
            self.tab_participant.setHorizontalHeaderLabels(["Code", "Nom", "Prenom", "Nombre", "Montant", "A payer"])

            if res_act_adh:
                for i, r in enumerate(res_act_adh):
                    res_adh = s.query(assogestion_adherents).filter_by(code_adherent=r.code_adherent).first()
                    if res_adh:
                        self.tab_participant.insertRow(i)
                        if r.a_payer:
                            result = res_adh.code_adherent, res_adh.nom_adherent, res_adh.prenom_adherent, r.nombre, r.montant, "Oui"
                        else:
                            result = res_adh.code_adherent, res_adh.nom_adherent, res_adh.prenom_adherent, r.nombre, r.montant, "Non"
                        for j, res in enumerate(result):
                            self.tab_participant.setItem(i, j, QTableWidgetItem(f'{result[j]}'))
            self.tab_participant.resizeColumnsToContents()
            self.tab_participant.horizontalHeader().setStretchLastSection(True)
            s.close()
        else:
            self.date_debut_edit.setDate(datetime.now())

    def save(self):
        s = self.Session()
        nb_error = 0
        try:
            if not self.edit:
                label_error_libelle = ACT_CTRL_001(self.libelle_edit.text())
                if label_error_libelle != "":
                    nb_error += 1
                self.label_error_libelle.setText(self.dic_error.get(label_error_libelle))
                label_error_max = ACT_CTRL_002(int(self.place_max_edit.text()))
                if label_error_max != "":
                    nb_error +=1
                self.label_error_max.setText(self.dic_error.get(label_error_max))
                if nb_error > 0:
                    self.erreur_saisie("Enregistrement impossible",
                                       f"Il y a {nb_error} erreur(s) dans votre formulaire. Vérifiez votre saisie")
                else:
                    new_activite = assogestion_activite(
                        libelle_activite=self.libelle_edit.text(),
                        date_activite=format_date_to_database(self.date_debut_edit.text()),
                        nb_participant_activite=int(self.nb_part_edit.text()),
                        nb_participant_max_activite=int(self.place_max_edit.text()),
                        tarif_activite=float(self.tarif_edit.text())
                    )
                    s.add(new_activite)
                    s.commit()
                    self.close()

            else:
                activite = s.query(assogestion_activite).filter_by(id_activite=self.act).first()
                activite.libelle_activite = self.libelle_edit.text()
                activite.date_activite = format_date_to_database(self.date_debut_edit.text())
                activite.nb_participant_activite = int(self.nb_part_edit.text())
                activite.nb_participant_max_activite = int(self.place_max_edit.text())
                activite.tarif_activite = float(self.tarif_edit.text())
                s.commit()
                self.close()
        except Exception as err:
            logger.error(err)
        finally:
            s.close()

    def closeEvent(self, event):
        if self.edit:
            s = self.Session()
            act = s.query(assogestion_activite).filter_by(
                libelle_activite=self.libelle_edit.text()).first()
            act.locked = False
            act.locked_by = None
            s.commit()
            s.close()
        self.finished.emit(True)
        event.accept()

    def send_mail(self):
        s = self.Session()
        act = s.query(assogestion_activite).filter_by(
            libelle_activite=self.libelle_edit.text()).first()
        s.close()
        if act.nb_participant_activite > 0:
            adh_act = s.query(assogestion_act_adh).filter_by(id_activite=self.act).all()
            self.application = MailingAPP(act.libelle_activite, self.Session, adh_act)
        else:
            self.warning_mail("Envoi d'email impossible",
                              f"Il n'y aucun participant à l'activité {act.libelle_activite}")

    def warning_mail(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Activités",
            message,
            texte,
            "WARNING"
        )

    def erreur_saisie(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Activités",
            message,
            texte,
            "ERROR"
        )