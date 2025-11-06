from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem
from loguru import logger

from IHM import detail_collectivite
from utils.CollVersementApp import CollVersementApp
from utils.SearchVilleApp import SearchVilleApp
from utils.collectivite_controls import coll_ctrl_001, coll_ctrl_002, coll_ctrl_004, coll_ctrl_005, \
    coll_ctrl_006
from utils.enrichissement import controle_enrichissement_ville
from utils.format_input import format_date_to_database
from utils.message import pop_up
from utils.models import assogestion_collectivite, assogestion_titre, assogestion_collectivite_paiement


class DetailCollectiviteAPP(QtWidgets.QMainWindow, detail_collectivite.Ui_detail_collectivite):
    finished = pyqtSignal(bool)

    def __init__(self, Session, edit, coll, parent=None):
        super(DetailCollectiviteAPP, self).__init__(parent)
        self.code_collectivite = None
        try:
            self.application = None
            self.Session = Session
            self.edit = edit
            self.coll = coll
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.butt_valider.setIcon(QIcon("save.png"))
            self.button_add_adh_dons.setIcon(QIcon("bank.png"))
            self.button_retour.clicked.connect(self.close)
            self.cp_edit.textChanged.connect(self.ctrl_enr_005)
            self.butt_valider.clicked.connect(self.enregistrer_collectivite)
            self.button_search_ville.clicked.connect(self.search_ville)
            self.cb_titre.currentTextChanged.connect(self.cb_titre_changed)
            self.button_add_adh_dons.clicked.connect(self.open_paiement_coll)
            self.init_ihm()
            self.dic_error = {
                "COLL_CTRL_001": "Le titre de la collectivité ne peut pas être vide",
                "COLL_CTRL_002": "La raison sociale de la collectivité est une donnée obligatoire",
                "COLL_CTRL_003": "L’adresse de la collectivité est obligatoire",
                "COLL_CTRL_004": "Le code postal de la collectivité ne doit pas être vide",
                "COLL_CTRL_005": "La ville de la collectivité ne doit pas être vide",
                "COLL_CTRL_006": "Le format de l’email n’est pas correct",
                "": ""
            }
            self.show()
        except Exception as err:
            logger.error(err)

    def search_ville(self):
        try:
            self.application = SearchVilleApp(self.Session)
            self.application.cp_sig.connect(self.set_cp_edit)
        except Exception as err:
            logger.error(err)

    def open_paiement_coll(self):
        self.application = CollVersementApp(self.Session, self.coll, False, None)
        self.application.finished.connect(self.do_something)

    def do_something(self):
        self.init_ihm()

    def set_cp_edit(self, value):
        try:
            self.cp_edit.setText(str(value[0]))
            self.cb_ville.setCurrentText(str(value[1]))
        except Exception as err:
            logger.error(err)

    def ctrl_enr_005(self):
        controle_enrichissement_ville(self)

    def cb_titre_changed(self):
        if self.cb_titre.currentText() in ("MAIRIE DE", "INTERCOM", "CC", "C AGGLO"):
            self.cb_type_membre.setCurrentText("Collectivité")
        elif self.cb_titre.currentText() == "ARCHIVE DE":
            self.cb_type_membre.setCurrentText("Archives et centre de doc")
        elif self.cb_titre.currentText() == "ASSOCIATION":
            self.cb_type_membre.setCurrentText("Association")
        elif self.cb_titre.currentText() == "SOCIETE":
            self.cb_type_membre.setCurrentText("Société")
        elif self.cb_titre.currentText() == "SERVICE":
            self.cb_type_membre.setCurrentText("Service")
        else:
            self.cb_type_membre.setCurrentText("")

    def closeEvent(self, a0):
        self.finished.emit(True)
        if self.edit:
            s = self.Session()
            coll = s.query(assogestion_collectivite).filter_by(
                code_collectivite=self.coll).first()
            logger.info(coll.locked_by)
            coll.locked = False
            coll.locked_by = None
            s.commit()
            s.close()
        a0.accept()

    def init_ihm(self):
        s = self.Session()
        try:
            res = s.query(assogestion_titre).filter_by(adherent=False).all()
            if res:
                self.cb_titre.addItem("")
                for r in res:
                    self.cb_titre.addItem(r.nom_titre)
            if self.coll is None:
                try:
                    if not self.edit:
                        self.code_collectivite = 0
                        res_coll = s.query(assogestion_collectivite).order_by(
                            assogestion_collectivite.code_collectivite.desc()).first()
                        if res_coll:
                            self.code_collectivite = int(res_coll.code_collectivite) + 1
                        else:
                            self.code_collectivite += 1
                    self.code_edit.setText(str(self.code_collectivite))
                except Exception as err:
                    logger.error(err)
            else:
                coll = s.query(assogestion_collectivite).filter_by(
                    code_collectivite=self.coll).first()
                self.code_edit.setText(str(coll.code_collectivite))
                self.cb_titre.setCurrentText(coll.titre_collectivite)
                self.cb_titre_changed()
                self.rs_edit.setText(coll.raison_sociale_collectivite)
                self.tel_edit.setText(coll.telephone_collectivite)
                self.email_edit.setText(coll.email_collectivite)
                self.adresse_edit.setText(coll.adresse_collectivite)
                self.contact_edit.setText(coll.contact_collectivite)
                self.cp_edit.setText(coll.cp_collectivite)
                self.cb_ville.setCurrentText(coll.ville_collectivite)
                self.comm_edit.setText(coll.commentaire_collectivite)
                self.cb_type_membre.setCurrentText(coll.categorie_collectivite)
                pai_coll = s.query(assogestion_collectivite_paiement).filter_by(code_collectivite=self.coll).all()
                self.tab_paiement.clear()
                self.tab_paiement.setRowCount(0)
                self.tab_paiement.setColumnCount(3)
                self.tab_paiement.setHorizontalHeaderLabels(
                    ["ID", "Date", "Montant"])
                if res:
                    for i, r in enumerate(pai_coll):
                        self.tab_paiement.insertRow(i)
                        result = r.id_paiement, r.date_paiement, r.montant_paiement
                        for j, res in enumerate(result):
                            self.tab_paiement.setItem(i, j, QTableWidgetItem(f'{result[j]}'))
                    self.tab_paiement.resizeColumnsToContents()
        except Exception as err:
            logger.error(err)
        finally:
            s.close()

    def enregistrer_collectivite(self):
        s = self.Session()
        try:
            nb_error = 0
            label_error_titre = coll_ctrl_001(self)
            if label_error_titre != "":
                nb_error += 1
            self.label_error_titre.setText(self.dic_error.get(label_error_titre))

            label_error_rs = coll_ctrl_002(self)
            if label_error_rs != "":
                nb_error += 1
            self.label_error_rs.setText(self.dic_error.get(label_error_rs))

            # label_error_adresse = coll_ctrl_003(self)
            # if label_error_adresse != "":
            #    nb_error += 1
            # self.label_error_adresse.setText(self.dic_error.get(label_error_adresse))

            label_error_cp = coll_ctrl_004(self)
            if label_error_cp != "":
                nb_error += 1
            self.label_error_cp.setText(self.dic_error.get(label_error_cp))

            label_error_ville = coll_ctrl_005(self)
            if label_error_ville != "":
                nb_error += 1
            self.label_error_ville.setText(self.dic_error.get(label_error_ville))

            label_error_mail = coll_ctrl_006(self)
            if label_error_mail != "":
                nb_error += 1
            self.label_error_email.setText(self.dic_error.get(label_error_mail))

            if nb_error == 0:
                logger.info("save")
                try:
                    if self.edit:
                        coll = s.query(assogestion_collectivite).filter_by(code_collectivite=self.coll).first()
                        coll.code_collectivite = self.code_edit.text()
                        coll.titre_collectivite = self.cb_titre.currentText()
                        coll.raison_sociale_collectivite = self.rs_edit.text()
                        coll.contact_collectivite = self.contact_edit.text()
                        coll.adresse_collectivite = self.adresse_edit.text()
                        coll.adresse_comp_collectivite = self.adresse_comp_edit.text()
                        coll.cp_collectivite = self.cp_edit.text()
                        coll.ville_collectivite = self.cb_ville.currentText()
                        coll.email_collectivite = self.email_edit.text()
                        coll.telephone_collectivite = self.tel_edit.text()
                        coll.date_prospection_collectivite = format_date_to_database(self.prospection_edit.text())
                        coll.commentaire_collectivite = self.comm_edit.toPlainText()
                        coll.categorie_collectivite = self.cb_type_membre.currentText()
                        coll.collectivite_bulletin = self.check_bulletin.isChecked()
                        s.commit()
                        self.success_save("Enregistrement réussi", "La fiche collectivité a bien été enregistrée")
                        self.close()
                    else:
                        new_collectivite = assogestion_collectivite(
                            code_collectivite=self.code_edit.text(),
                            titre_collectivite=self.cb_titre.currentText(),
                            raison_sociale_collectivite=self.rs_edit.text(),
                            contact_collectivite=self.contact_edit.text(),
                            adresse_collectivite=self.adresse_edit.text(),
                            adresse_comp_collectivite=self.adresse_comp_edit.text(),
                            cp_collectivite=self.cp_edit.text(),
                            ville_collectivite=self.cb_ville.currentText(),
                            email_collectivite=self.email_edit.text(),
                            telephone_collectivite=self.tel_edit.text(),
                            date_prospection_collectivite=format_date_to_database(self.prospection_edit.text()),
                            commentaire_collectivite=self.comm_edit.toPlainText(),
                            categorie_collectivite=self.cb_type_membre.currentText(),
                            collectivite_bulletin=False
                        )
                        logger.info(new_collectivite)
                        s.add(new_collectivite)
                        s.commit()
                        self.success_save("Enregistrement réussi", "La fiche collectivité a bien été enregistrée")
                        self.close()
                except Exception as err:
                    logger.error(err)
            else:
                self.erreur_saisie("Enregistrement impossible",
                                   f"Il y a {nb_error} erreur(s) dans votre formulaire, merci de vérifier votre saisie")
        except Exception as err:
            logger.error(err)
        finally:
            s.close()

    def erreur_saisie(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Collectivités",
            message,
            texte,
            "ERROR"
        )

    def success_save(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Collectivités",
            message,
            texte,
            "INFO"
        )
