import getpass
from datetime import datetime

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem
from loguru import logger

from IHM import detail_adherent
from utils.AdhCotisationApp import AdhCotAPP
from utils.AdhDonsApp import AdhDonsAPP
from utils.adherent_controls import adh_ctrl_001, adh_ctrl_002, adh_ctrl_003, adh_ctrl_004, adh_ctrl_005, adh_ctrl_006
from utils.enrichissement import controle_enrichissement_ville
from utils.message import pop_up
from utils.models import assogestion_titre, assogestion_adherents, assogestion_adh_dons, assogestion_cotisation, \
    assogestion_act_adh, assogestion_activite


class DetailAdhAPP(QtWidgets.QMainWindow, detail_adherent.Ui_detail_adherent):
    finished = pyqtSignal(bool)

    def __init__(self, Session, edit, adh, type, parent=None):
        super(DetailAdhAPP, self).__init__(parent)
        self.code_adherent = None
        try:
            self.application = None
            self.Session = Session
            self.edit = edit
            self.adh = adh
            self.type = type
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.butt_valider.clicked.connect(self.enregistrer_adherent)
            self.butt_valider.setIcon(QIcon("save.png"))
            self.cp_edit.textChanged.connect(self.adh_enr_005)
            self.cb_titre.currentIndexChanged.connect(self.cb_titre_changed)
            self.button_add_adh.clicked.connect(self.open_new_adhesion)
            self.tab_adh_dons.doubleClicked.connect(self.edit_adh_dons)
            self.button_add_adh.setIcon(QIcon("bank.png"))
            self.button_add_don.clicked.connect(self.open_new_dons)
            self.button_add_don.setIcon(QIcon("bank.png"))

            self.button_retour.clicked.connect(self.retour)
            self.init_ihm()
            self.dic_error = {
                "ADH_CTRL_001": "Le titre de l’adhérent ne peut pas être vide",
                "ADH_CTRL_002": "Le nom et le prénom de l’adhérent sont des données obligatoire",
                "ADH_CTRL_003": "L’adresse de l’adhérent est obligatoire",
                "ADH_CTRL_004": "Le code postal de l’adhérent ne doit pas être vide",
                "ADH_CTRL_005": "La ville de l’adhérent ne doit pas être vide",
                "ADH_CTRL_006": "Le format de l’email n’est pas correct",
                "": ""
            }
            self.show()
        except Exception as err:
            logger.error(err)

    def open_new_adhesion(self):
        try:
            self.application = AdhCotAPP(self.Session, self.code_edit.text(), False, None)
            self.application.finished.connect(self.do_something)
        except Exception as err:
            logger.error(err)

    def open_new_dons(self):
        try:
            self.application = AdhDonsAPP(self.Session, self.code_edit.text(), False, None)
            self.application.finished.connect(self.do_something)
        except Exception as err:
            logger.error(err)


    def init_ihm(self):
        s = self.Session()
        try:
            if self.type:
                self.cb_type_membre.setCurrentText(self.type)

            res = s.query(assogestion_titre).filter_by(adherent=True).all()
            if res:
                self.cb_titre.addItem("")
                for r in res:
                    self.cb_titre.addItem(r.nom_titre)
            if self.adh is None:
                if not self.edit:
                    self.code_adherent = 0
                    res_adh = s.query(assogestion_adherents).order_by(assogestion_adherents.code_adherent.desc()).first()
                    if res_adh:
                        self.code_adherent = int(res_adh.code_adherent) + 1
                    else:
                        self.code_adherent += 1
                self.code_edit.setText(str(self.code_adherent))
                self.adhesion_edit.setDate(datetime.now())
            else:
                adh = s.query(assogestion_adherents).filter_by(
                    code_adherent=self.adh).first()
                logger.info(adh.adherent_bulletin)
                self.check_bulletin.setChecked(adh.adherent_bulletin)
                self.code_edit.setText(str(adh.code_adherent))
                self.cb_titre.setCurrentText(adh.titre_adherent)
                self.fonction_edit.setText(adh.fonction_adherent)
                self.nom_edit.setText(adh.nom_adherent)
                self.prenom_edit.setText(adh.prenom_adherent)
                self.tel_edit.setText(adh.telephone_adherent)
                self.email_edit.setText(adh.email_adherent)
                self.adresse_edit.setText(adh.adresse_adherent)
                self.adress_comp_edit.setText(adh.adresse_comp_adherent)
                self.cp_edit.setText(adh.cp_adherent)
                self.cb_ville.setCurrentText(adh.ville_adherent)

                if adh.adherent_date_naissance:
                    self.naissance_edit.setDate(adh.adherent_date_naissance)
                if adh.adherent_date_prospection:
                    self.prospection_edit.setDate(adh.adherent_date_prospection)
                if adh.adherent_date_adhesion:
                    self.adhesion_edit.setDate(adh.adherent_date_adhesion)
                self.textEdit.setText(adh.adherent_commentaire)
                self.cb_type_membre.setCurrentText(adh.adherent_type)
                res_adh_dons = s.query(assogestion_adh_dons).filter_by(code_adherent=adh.code_adherent).all()
                self.tab_adh_dons.clear()
                self.tab_adh_dons.setRowCount(0)
                if res_adh_dons:
                    self.tab_adh_dons.setColumnCount(6)
                    self.tab_adh_dons.setHorizontalHeaderLabels(
                        ["Code", "Type", "Montant ADH", "Montant Bulletin", "Montant dons", "Début", "Fin"])
                    for i, r in enumerate(res_adh_dons):
                        res_cot = s.query(assogestion_cotisation).filter_by(id_cotisation=r.id_cotisation).first()
                        if res_cot:
                            self.tab_adh_dons.insertRow(i)
                            result = r.id_adh_don, res_cot.nom_cotisation, r.montant_adh, r.montant_bulletin, r.montant_dons, r.date_debut_adh_don, r.date_fin_adh_don
                            for j, res in enumerate(result):
                                self.tab_adh_dons.setItem(i, j, QTableWidgetItem(f'{result[j]}'))
                    self.tab_adh_dons.resizeColumnsToContents()
                res_adh_act = s.query(assogestion_act_adh).filter_by(code_adherent=adh.code_adherent).all()
                self.tab_activites_adherent.clear()
                self.tab_activites_adherent.setRowCount(0)
                if res_adh_act:
                    self.tab_activites_adherent.setColumnCount(2)
                    self.tab_activites_adherent.setHorizontalHeaderLabels(
                        ["Activité", "Date"])
                    for i, r in enumerate(res_adh_act):
                        res_act = s.query(assogestion_activite).filter_by(id_activite=r.id_activite).first()
                        if res_act:
                            self.tab_activites_adherent.insertRow(i)
                            result = res_act.libelle_activite, res_act.date_activite
                            for j, res in enumerate(result):
                                self.tab_activites_adherent.setItem(i, j, QTableWidgetItem(f'{result[j]}'))
                    self.tab_activites_adherent.resizeColumnsToContents()
        except Exception as err:
            logger.error(err)
        finally:
            s.close()

    def cb_titre_changed(self):
        if self.cb_titre.currentText() in ["MAIRIE DE", "ASSOCIATION", "ARCHIVES DE", "SERVICE", "SOCIETE", "C Agglo",
                                           "INTERCOM", "CC"]:
            self.naissance_edit.setEnabled(False)
        else:
            self.naissance_edit.setEnabled(True)

    def adh_enr_005(self):
        controle_enrichissement_ville(self)

    def enregistrer_adherent(self):
        nb_error = 0
        try:
            label_error_titre = adh_ctrl_001(self)
            if label_error_titre != "":
                nb_error += 1
            self.label_error_titre.setText(self.dic_error.get(label_error_titre))

            label_error_nom = adh_ctrl_002(self)
            if label_error_nom != "":
                nb_error += 1
            self.label_error_nom.setText(self.dic_error.get(label_error_nom))

            label_error_prenom = adh_ctrl_002(self)
            if label_error_prenom != "":
                nb_error += 1
            self.label_error_prenom.setText(self.dic_error.get(label_error_prenom))

            label_error_email = adh_ctrl_006(self)
            if label_error_email != "":
                nb_error += 1
            self.label_error_email.setText(self.dic_error.get(label_error_email))
            if self.cb_type_membre.currentText() != "Prospect":
                label_error_adresse = adh_ctrl_003(self)
                if label_error_adresse != "":
                    nb_error += 1
                label_error_cp = adh_ctrl_004(self)
                if label_error_cp != "":
                    nb_error += 1
                label_error_ville = adh_ctrl_005(self)
                if label_error_ville != "":
                    nb_error += 1
                self.label_error_adresse.setText(self.dic_error.get(label_error_adresse))
                self.label_error_cp.setText(self.dic_error.get(label_error_cp))
                self.label_error_ville.setText(self.dic_error.get(label_error_ville))
            if nb_error > 0:
                self.erreur_saisie("Enregistrement impossible",
                                   f"Il y a {nb_error} erreur(s) dans votre formulaire. Vérifiez votre saisie")
            else:
                s = self.Session()
                date_naissance = datetime.strptime(self.naissance_edit.text(), "%d/%m/%Y").__format__("%Y/%m/%d")
                date_prospection = datetime.strptime(self.prospection_edit.text(), "%d/%m/%Y").__format__("%Y/%m/%d")
                date_adhesion = datetime.strptime(self.adhesion_edit.text(), "%d/%m/%Y").__format__("%Y/%m/%d")
                if self.edit:
                    adh = s.query(assogestion_adherents).filter_by(
                        code_adherent=self.adh).first()
                    adh.code_adherent = self.code_edit.text()
                    adh.titre_adherent = self.cb_titre.currentText()
                    adh.fonction_adherent = self.fonction_edit.text()
                    adh.nom_adherent = self.nom_edit.text()
                    adh.prenom_adherent = self.prenom_edit.text()
                    adh.adresse_adherent = self.adresse_edit.text()
                    adh.adresse_comp_adherent = self.adress_comp_edit.text()
                    adh.cp_adherent = self.cp_edit.text()
                    adh.ville_adherent = self.cb_ville.currentText()
                    adh.email_adherent = self.email_edit.text()
                    adh.telephone_adherent = self.tel_edit.text()
                    adh.adherent_date_naissance = date_naissance
                    adh.adherent_date_prospection = date_prospection
                    adh.adherent_date_adhesion = date_adhesion
                    adh.adherent_moyen_paiement = self.cb_paiement_means.currentText()
                    adh.adherent_commentaire = self.textEdit.toPlainText()
                    adh.adherent_type = self.cb_type_membre.currentText()
                    adh.edited_by = getpass.getuser()
                    adh.adherent_bulletin = self.check_bulletin.isChecked()
                    s.commit()
                    self.success_save("Enregistrement terminé",
                                      f"L'adhérent {self.code_edit.text()} - {self.nom_edit.text()} {self.prenom_edit.text()} a été modifié")
                else:
                    new_adherent = assogestion_adherents(
                        code_adherent=self.code_edit.text(),
                        titre_adherent=self.cb_titre.currentText(),
                        fonction_adherent = self.fonction_edit.text(),
                        nom_adherent=self.nom_edit.text(),
                        prenom_adherent=self.prenom_edit.text(),
                        adresse_adherent=self.adresse_edit.text(),
                        adresse_comp_adherent=self.adress_comp_edit.text(),
                        cp_adherent=self.cp_edit.text(),
                        ville_adherent=self.cb_ville.currentText(),
                        email_adherent=self.email_edit.text(),
                        telephone_adherent=self.tel_edit.text(),
                        adherent_date_naissance=date_naissance,
                        adherent_date_prospection=date_prospection,
                        adherent_date_adhesion=date_adhesion,
                        adherent_moyen_paiement=self.cb_paiement_means.currentText(),
                        adherent_commentaire=self.textEdit.toPlainText(),
                        adherent_type=self.cb_type_membre.currentText(),
                        edited_by = getpass.getuser(),
                        adherent_bulletin = self.check_bulletin.isChecked()
                    )
                    s.add(new_adherent)
                    s.commit()
                    s.close()

                    self.success_save("Enregistrement terminé",
                                      f"L'adhérent {self.code_edit.text()} - {self.nom_edit.text()} {self.prenom_edit.text()} a été enregistré")
                self.finished.emit(True)
                self.close()
        except Exception as err:
            logger.error(err)
            self.erreur_import("Enregistrement impossible", str(err))

    def retour(self):

        self.close()
    def erreur_saisie(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Adhérent",
            message,
            texte,
            "ERROR"
        )


    def success_save(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Adhérent",
            message,
            texte,
            "INFO"
        )

    def do_something(self):
        try:
            self.init_ihm()
        except Exception as err:
            logger.error(err)
    def closeEvent(self, event):
        if self.edit:
            s = self.Session()
            adh = s.query(assogestion_adherents).filter_by(
                code_adherent=self.adh).first()
            adh.locked = False
            adh.locked_by = None
            s.commit()
            s.close()
        self.finished.emit(True)
        event.accept()


    def edit_adh_dons(self):
        try:
            if self.tab_adh_dons.currentItem().isSelected():
                if self.tab_adh_dons.currentItem().column() == 0:
                    s = self.Session()
                    res = s.query(assogestion_adh_dons).filter_by(id_adh_don=self.tab_adh_dons.currentItem().text()).first()
                    if res:
                        cot = s.query(assogestion_cotisation).filter_by(id_cotisation=res.id_cotisation).first()
                        if cot.type != "Dons":
                            self.application = AdhCotAPP(self.Session, self.code_edit.text(), True, res)
                        else:
                            self.application = AdhDonsAPP(self.Session, self.code_edit.text(), True, res)
                        self.application.finished.connect(self.do_something)
                    s.close()
        except Exception as err:
            logger.error(err)