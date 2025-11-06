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

from IHM import liste_collectivite
from utils.DetailCollectiviteApp import DetailCollectiviteAPP
from utils.GenerationRecuAPP import ExportRecuApp
from utils.ImportAPP import ImportApp
from utils.MailingCollApp import MailingCollAPP
from utils.message import pop_up
from utils.models import assogestion_collectivite


class ListeCollAPP(QtWidgets.QMainWindow, liste_collectivite.Ui_liste_coll):
    finished = pyqtSignal(bool)

    def __init__(self, Session,parent=None):
        super(ListeCollAPP, self).__init__(parent)
        try:
            self.application = None
            self.Session = Session
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.init_app(None)
            self.button_creation_coll.clicked.connect(self.open_new_collectivite)
            self.button_creation_coll.setIcon(QIcon("creer.png"))
            #self.button_import_adherent.clicked.connect(self.open_import)
            #self.button_import_adherent.setIcon(QIcon("importer.png"))
            self.button_retour.clicked.connect(self.retour)
            self.button_retour.setIcon(QIcon("retour.png"))
            self.button_rechercher.clicked.connect(self.rechercher)
            self.tab_coll.doubleClicked.connect(self.open_edit_collectivite)
            self.button_send_mail.clicked.connect(self.envoyer_mail)
            self.button_maj_coll.clicked.connect(self.maj_coll)
            self.button_export_coll.clicked.connect(self.export_coll)
            self.showMaximized()
        except Exception as err:
            logger.error(err)
            self.close()

    def export_coll(self):
        try:
            q = self.search_app()
            wb = openpyxl.Workbook()
            sheet = wb.active
            sheet.title = "Export Collectivités"
            sheet[f"A1"].value = "Code collectivité"
            sheet[f"B1"].value = "Titre collectivité"
            sheet[f"C1"].value = "Raison sociale collectivité"
            sheet[f"D1"].value = "Contact collectivité"
            sheet[f"E1"].value = "Adresse collectivité"
            sheet[f"F1"].value = "Email collectivité"
            sheet[f"G1"].value = "Téléphone collectivité"
            sheet[f"H1"].value = "Bulletin"
            sheet[f"I1"].value = "Type"
            for i, r in enumerate(q, 2):
                sheet[f"A{i}"].value = r.code_collectivite
                sheet[f"B{i}"].value = r.titre_collectivite
                sheet[f"C{i}"].value = r.raison_sociale_collectivite
                sheet[f"D{i}"].value = r.contact_collectivite
                sheet[f"E{i}"].value = f"{self.transco_val(r.adresse_collectivite)} {self.transco_val(r.adresse_comp_collectivite)} {self.transco_val(r.cp_collectivite)} {self.transco_val(r.ville_collectivite)}"
                sheet[f"F{i}"].value = self.transco_val(r.email_collectivite)
                sheet[f"G{i}"].value = self.transco_val(r.telephone_collectivite)
                sheet[f"H{i}"].value = self.transco_val(r.collectivite_bulletin)
                sheet[f"I{i}"].value = self.transco_val(r.categorie_collectivite)
            name = QFileDialog.getSaveFileName(self, 'Save File', f"Export_Collectivités_{datetime.now().strftime('%Y_%m_%d')}.xlsx")
            wb.save(name[0])
        except Exception as err:
            logger.error(err)
            self.warning_adh("Une erreur est survenue", str(err))

    def maj_coll(self):
        s = self.Session()
        res = s.query(assogestion_collectivite).filter_by(locked=True).all()
        for r in res:
            r.locked = False
        s.commit()
        s.close()
        self.warning_adh("Fiches mises à jour", f"{len(res)} fiche(s) mise(s) à jour")
        self.init_app(None)
    def envoyer_recu(self):
        try:
            self.application = ExportRecuApp(self.Session, None)
        except Exception as err:
            logger.error(err)

    def envoyer_mail(self):
        s = self.Session()
        if self.cb_type_coll.currentText() != "":
            liste_dest = s.query(assogestion_collectivite).filter_by(categorie_collectivite=self.cb_type_coll.currentText()).all()
        else:
            liste_dest = s.query(assogestion_collectivite).all()
        self.application = MailingCollAPP(self.Session, liste_dest)
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

    def init_app(self, data):
        self.tab_coll.clear()
        s = self.Session()
        try:
            if data is not None:
                if data:
                    res = data
                else:
                    res = []
            else:
                res = s.query(assogestion_collectivite).order_by(assogestion_collectivite.code_collectivite).all()
            self.tab_coll.clear()
            self.tab_coll.setRowCount(0)
            self.tab_coll.setColumnCount(11)
            self.tab_coll.setHorizontalHeaderLabels(
                ["Code", "Titre", "Raison sociale","Contact", "Adresse", "CP", "Ville", "Email", "Verrouillé",
                 "Verrouillé par", "Edité par"])
            if res:
                for i, r in enumerate(res):
                    self.tab_coll.insertRow(i)
                    result = r.code_collectivite, r.titre_collectivite, r.raison_sociale_collectivite, r.contact_collectivite, r.adresse_collectivite, r.cp_collectivite, r.ville_collectivite, r.email_collectivite, self.transco_val(
                        r.locked), self.transco_val(r.locked_by), self.transco_val(r.edited_by)
                    for j, res in enumerate(result):
                        self.tab_coll.setItem(i, j, QTableWidgetItem(f'{result[j]}'))
                self.tab_coll.resizeColumnsToContents()
        except Exception as err:
            logger.error(err)
        s.close()

    def open_new_collectivite(self):
        try:
            self.application = DetailCollectiviteAPP(self.Session, False, None)
            self.application.finished.connect(self.do_something)
            self.hide()
        except Exception as err:
            logger.error(err)

    def open_edit_collectivite(self):
        s = self.Session()
        adh = None
        if self.tab_coll.currentItem().isSelected():
            if self.tab_coll.currentItem().column() == 0:
                logger.info(self.tab_coll.currentItem().text())
                coll = s.query(assogestion_collectivite).filter_by(
                    code_collectivite=self.tab_coll.currentItem().text()).first()
                if coll:
                    if coll.locked:
                        self.warning_adh("Modification impossible",
                                         f"La fiche est déjà en cours de modification par {coll.locked_by}")
                        s.close()
                    else:
                        try:
                            coll.locked = True
                            coll.locked_by = getpass.getuser()
                            s.commit()
                            self.application = DetailCollectiviteAPP(self.Session, True, coll.code_collectivite)
                            self.application.finished.connect(self.do_something)
                            self.hide()
                        except Exception as err:
                            logger.error(err)
        else:
            logger.info(f"Pas de collectivité trouvée avec le code {self.tab_coll.currentItem().text()}")
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
                (assogestion_collectivite, 'raison_sociale_collectivite'): self.search_rs.text(),
                (assogestion_collectivite, 'contact_collectivite'): self.search_contact.text(),
                (assogestion_collectivite, 'adresse_collectivite'): self.search_adresse.text(),
                (assogestion_collectivite, 'cp_collectivite'): self.search_cp.text(),
                (assogestion_collectivite, 'ville_adherent'): self.search_ville.text(),
                (assogestion_collectivite, 'email_collectivite'): self.search_email.text(),
                (assogestion_collectivite, 'telephone_collectivite'): self.search_tel.text(),
            }
            fields_cb = {
                (assogestion_collectivite, 'categorie_collectivite'): self.cb_type_coll.currentText(),
            }
            filters_text = list()
            for table_field, value in fields_text.items():
                table, field = table_field
                if value:
                    filters_text.append((table, field, value))

            filters_cb = list()
            for table_field, value in fields_cb.items():
                table, field = table_field
                if value:
                    filters_cb.append((table, field, value))
            binary_expressions_text = [getattr(table, attribute).ilike(f"%{value}%") for table, attribute, value in filters_text]
            binary_expressions_cb = [getattr(table, attribute) == value for table, attribute, value in
                                       filters_cb]
            if filters_text and filters_cb:
                query = s.query(assogestion_collectivite).filter(and_(or_(*binary_expressions_text), or_(*binary_expressions_cb))).all()
            elif filters_text:
                query = s.query(assogestion_collectivite).filter(or_(*binary_expressions_text)).all()
            elif filters_cb:
                query = s.query(assogestion_collectivite).filter(or_(*binary_expressions_cb)).all()
            else:
                query = s.query(assogestion_collectivite).order_by(assogestion_collectivite.code_collectivite).all()
        except Exception as err:
            logger.error(err)
        finally:
            s.close()
            if query:
                self.label_res_search.setText(f"LA RECHERCHE RETOURNE {len(query)} RESULTAT(S)")
            else:
                self.label_res_search.setText(f"LA RECHERCHE RETOURNE 0 RESULTAT")
            return query
