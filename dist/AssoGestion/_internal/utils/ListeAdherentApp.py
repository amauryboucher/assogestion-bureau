import getpass
from datetime import datetime
from operator import and_

import openpyxl
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem, QFileDialog
from loguru import logger
from sqlalchemy import or_

from IHM import liste_adherents
from utils.DetailAdherentApp import DetailAdhAPP
from utils.GenerationRecuAPP import ExportRecuApp
from utils.ImportAPP import ImportApp
from utils.MailingAdherentApp import MailingAdhAPP
from utils.message import pop_up
from utils.models import assogestion_adherents


class ListeAdhAPP(QtWidgets.QMainWindow, liste_adherents.Ui_liste_adherent):
    finished = pyqtSignal(bool)

    def __init__(self, Session, res, parent=None):
        super(ListeAdhAPP, self).__init__(parent)
        try:
            self.application = None
            self.Session = Session
            self.res = res
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.init_app(None)

            self.button_creation_adherents.clicked.connect(self.open_new_adherent)
            self.button_creation_prospect.clicked.connect(self.open_new_prospect)
            self.button_creation_adherents.setIcon(QIcon("creer.png"))
            self.button_creation_prospect.setIcon(QIcon("creer.png"))
            self.button_import_adherent.clicked.connect(self.open_import)
            self.button_import_adherent.setIcon(QIcon("importer.png"))
            self.button_retour.clicked.connect(self.retour)
            self.button_retour.setIcon(QIcon("retour.png"))
            self.button_rechercher.clicked.connect(self.rechercher)
            self.tab_adherent.doubleClicked.connect(self.open_edit_adherent)
            self.button_send_recu.clicked.connect(self.envoyer_recu)
            self.button_send_mail.clicked.connect(self.envoyer_mail)
            self.button_maj_membre.clicked.connect(self.maj_adh)
            self.button_export_adherents.clicked.connect(self.exporter_liste)
            self.showMaximized()
        except Exception as err:
            logger.error(err)
            self.close()

    def maj_adh(self):
        #nb_update = 0
        #s = self.Session()
        #res = s.query(assogestion_adherents).all()
        #for r in res:
        #    res_adh = s.query(assogestion_adh_dons).where(assogestion_adh_dons.id_cotisation.in_([26, 28, 30, 31])).filter_by(code_adherent=r.code_adherent).all()
        #    if res_adh:
        #        r.adherent_bulletin = True
        #        s.commit()
        #        nb_update += 1
        #logger.info(nb_update)
        #s.close()
        s = self.Session()
        res = s.query(assogestion_adherents).filter_by(locked=True).all()
        for r in res:
            r.locked = False
        s.commit()
        s.close()
        self.warning_adh("Adhérents mis à jour", f"{len(res)} adhérent(s) mis à jour")
        self.init_app(None)
    def envoyer_recu(self):
        try:
            self.application = ExportRecuApp(self.Session, None)
        except Exception as err:
            logger.error(err)

    def envoyer_mail(self):
        liste_dest = self.search_app()
        self.application = MailingAdhAPP(self.Session, liste_dest)

    def exporter_liste(self):
        try:
            q = self.search_app()
            wb = openpyxl.Workbook()
            sheet = wb.active
            sheet.title = "Export Adhérents"
            sheet[f"A1"].value = "Code adhérent"
            sheet[f"B1"].value = "Titre adhérent"
            sheet[f"C1"].value = "Nom adhérent"
            sheet[f"D1"].value = "Prénom adhérent"
            sheet[f"E1"].value = "Adresse adhérent"
            sheet[f"F1"].value = "Email adhérent"
            sheet[f"G1"].value = "Téléphone adhérent"
            sheet[f"H1"].value = "Bulletin"
            sheet[f"I1"].value = "Type"
            for i, r in enumerate(q,2):
                logger.info(r.code_adherent)
                sheet[f"A{i}"].value = r.code_adherent
                sheet[f"B{i}"].value = r.titre_adherent
                sheet[f"C{i}"].value = r.nom_adherent
                sheet[f"D{i}"].value = r.prenom_adherent
                sheet[f"E{i}"].value = f"{self.transco_val(r.adresse_adherent)} {self.transco_val(r.adresse_comp_adherent)} {self.transco_val(r.cp_adherent)} {self.transco_val(r.ville_adherent)}"
                sheet[f"F{i}"].value = self.transco_val(r.email_adherent)
                sheet[f"G{i}"].value = self.transco_val(r.telephone_adherent)
                sheet[f"H{i}"].value = self.transco_val(r.adherent_bulletin)
                sheet[f"I{i}"].value = self.transco_val(r.adherent_type)
            name = QFileDialog.getSaveFileName(self, 'Save File',
                                               f"Export_Adherents_{datetime.now().strftime('%Y_%m_%d')}.xlsx")
            wb.save(name[0])
        except Exception as err:
            logger.error(err)
            self.warning_adh("Une erreur est survenue", str(err))
    def retour(self):
        self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.finished.emit(True)
        a0.accept()

    @staticmethod
    def transco_val(value):
        if isinstance(value, bool):
            if value:
                return "Oui"
            else:
                return "Non"
        elif value is None:
            return ""
        else:
            return value

    @staticmethod
    def transco_bool(value):
        if value == "Oui":
            return True
        elif value == "Non":
            return False
        else:
            return ""

    def init_app(self, data):
        self.tab_adherent.clear()
        s = self.Session()
        try:
            if data is not None:
                if data:
                    res = data
                else:
                    res = []
            else:
                res = s.query(assogestion_adherents).order_by(assogestion_adherents.code_adherent).all()
            self.tab_adherent.clear()
            self.tab_adherent.setRowCount(0)
            self.tab_adherent.setColumnCount(11)
            self.tab_adherent.setHorizontalHeaderLabels(
                ["Code", "Titre", "Nom", "Prenom", "Adresse", "CP", "Ville", "Email","Bulletin", "Verrouillé",
                 "Verrouillé par"])
            if res:
                for i, r in enumerate(res):
                    self.tab_adherent.insertRow(i)
                    result = r.code_adherent, r.titre_adherent, r.nom_adherent, r.prenom_adherent, r.adresse_adherent, r.cp_adherent, r.ville_adherent, r.email_adherent,  self.transco_val(r.adherent_bulletin), self.transco_val(
                        r.locked), self.transco_val(r.locked_by)
                    for j, res in enumerate(result):
                        self.tab_adherent.setItem(i, j, QTableWidgetItem(f'{result[j]}'))
                self.tab_adherent.resizeColumnsToContents()
        except Exception as err:
            logger.error(err)
        s.close()

    def open_new_adherent(self):
        self.application = DetailAdhAPP(self.Session, False, None, "Membre")
        self.application.finished.connect(self.do_something)
        self.hide()

    def open_new_prospect(self):
        self.application = DetailAdhAPP(self.Session, False, None, "Prospect")
        self.application.finished.connect(self.do_something)
        self.hide()

    def open_edit_adherent(self):
        s = self.Session()
        adh = None
        if self.tab_adherent.currentItem().isSelected():
            if self.tab_adherent.currentItem().column() == 0:
                logger.info(self.tab_adherent.currentItem().text())
                adh = s.query(assogestion_adherents).filter_by(
                    code_adherent=self.tab_adherent.currentItem().text()).first()
                if adh:
                    if adh.locked:
                        self.warning_adh("Modification impossible",
                                         f"La fiche est déjà en cours de modification par {adh.locked_by}")
                        s.close()
                    else:
                        try:
                            adh.locked = True
                            adh.locked_by = getpass.getuser()
                            s.commit()
                            self.application = DetailAdhAPP(self.Session, True, adh.code_adherent, None)
                            self.application.finished.connect(self.do_something)
                            self.hide()
                        except Exception as err:
                            logger.error(err)
        else:
            logger.info(f"Pas d'adhérent trouvée avec le code {self.tab_adherent.currentItem().text()}")
        s.close()


    def do_something(self):
        try:
            self.show()
            self.init_app(None)
        except Exception as err:
            logger.error(err)

    def open_import(self):
        try:
            self.application = ImportApp(self.Session, "Adhérents")
            self.application.finished.connect(self.do_something)
        except Exception as err:
            logger.error(err)

    def warning_adh(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Adhérents",
            message,
            texte,
            "WARNING"
        )

    def rechercher(self):
        query = self.search_app()
        self.init_app(query)
    def search_app(self):
        query = None
        s = self.Session()
        try:
            fields_text = {
                (assogestion_adherents, 'nom_adherent'): self.search_nom.text(),
                (assogestion_adherents, 'prenom_adherent'): self.search_prenom.text(),
                (assogestion_adherents, 'adresse_adherent'): self.search_adresse.text(),
                (assogestion_adherents, 'cp_adherent'): self.search_cp.text(),
                (assogestion_adherents, 'ville_adherent'): self.search_ville.text(),
                (assogestion_adherents, 'email_adherent'): self.search_email.text(),
                (assogestion_adherents, 'telephone_adherent'): self.search_tel.text(),
            }
            fields_cb = {
                (assogestion_adherents, 'adherent_type'): self.cb_type_membre.currentText(),
                (assogestion_adherents, 'adherent_categorie'): self.cb_cat_membre.currentText(),
            }
            filters_text = list()
            for table_field, value in fields_text.items():
                table, field = table_field
                if value != '':
                    filters_text.append((table, field, value))

            filters_cb = list()
            for table_field, value in fields_cb.items():
                table, field = table_field
                if value:
                    filters_cb.append((table, field, value))
            logger.info(filters_text)
            binary_expressions_text = [getattr(table, attribute).ilike(f"%{value}%") for table, attribute, value in filters_text]
            binary_expressions_cb = [getattr(table, attribute) == value for table, attribute, value in
                                       filters_cb]
            if filters_text and filters_cb:
                query = s.query(assogestion_adherents).filter(and_(or_(*binary_expressions_text), or_(*binary_expressions_cb))).order_by(assogestion_adherents.code_adherent).all()
            elif filters_text:
                query = s.query(assogestion_adherents).filter(or_(*binary_expressions_text)).order_by(assogestion_adherents.code_adherent).all()
            elif filters_cb:
                query = s.query(assogestion_adherents).filter(or_(*binary_expressions_cb)).order_by(assogestion_adherents.code_adherent).all()
            else:
                query = s.query(assogestion_adherents).order_by(assogestion_adherents.code_adherent).all()
        except Exception as err:
            logger.error(err)
            query = None
        finally:
            s.close()
            if query:
                self.label_res_search.setText(f"LA RECHERCHE RETOURNE {len(query)} RESULTAT(S)")
            else:
                self.label_res_search.setText(f"LA RECHERCHE RETOURNE 0 RESULTAT")
            return query
