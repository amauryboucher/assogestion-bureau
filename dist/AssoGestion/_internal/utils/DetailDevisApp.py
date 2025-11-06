from datetime import datetime, timedelta
from os import getcwd

import openpyxl
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem
from loguru import logger
from win32com import client

from IHM import devis
from utils.DetailFactureApp import DetailFactAPP
from utils.DetailLigneDevisApp import DetailLigneDevAPP
from utils.devis_controls import *
from utils.enrichissement import controle_enrichissement_ville
from utils.message import pop_up
from utils.models import assogestion_client, assogestion_devis, assogestion_ligne_devis, assogestion_facture, \
    assogestion_ligne_facture


class DetailDevisAPP(QtWidgets.QMainWindow, devis.Ui_devis):
    finished = pyqtSignal(bool)

    def __init__(self, Session, session, edit, dev, parent=None):
        super(DetailDevisAPP, self).__init__(parent)
        try:
            self.s = Session
            self.Session = session
            self.edit = edit
            self.dev = dev
            self.setupUi(self)
            self.application = None
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.butt_save.setIcon(QIcon("save.png"))
            self.cb_client.currentTextChanged.connect(self.set_client_via_cb)
            self.butt_save.clicked.connect(self.save_client)
            self.tab_ligne.doubleClicked.connect(self.open_ligne_devis)
            self.button_ligne.clicked.connect(self.open_new_ligne_devis)
            self.button_valider.clicked.connect(self.save_devis)
            if self.edit:
                self.button_transform_facture.setEnabled(True)
            else:
                self.button_transform_facture.setEnabled(False)
            self.button_transform_facture.clicked.connect(self.facturer_devis)
            self.button_pdf.clicked.connect(self.export_pdf)
            self.cp_edit.textChanged.connect(self.client_enr_005)
            self.dic_error = {
                "CM_DEV_001": "La raison sociale du client est obligatoire",
                "CM_DEV_002": "L'adresse du client est obligatoire",
                "CM_DEV_003": "Le code postal de l’adhérent est obligatoire",
                "CM_DEV_004": "La ville de l’adhérent ne doit pas être vide",
                "CM_DEV_005": "Le format de l’email n’est pas correct",
                "CM_DEV_006": "Le devis doit être attachée à un client",
                "CM_DEV_007": "Le montant doit être supérieur à 0.00 €",
                "": ""
            }
            self.init_app()
            self.show()
        except Exception as err:
            logger.error(err)

    def valider_saisie_client(self):
        nb_error = 0
        if CM_DEV_001(self) != "":
            nb_error += 1

        if CM_DEV_002(self) != "":
            nb_error += 1

        if CM_DEV_003(self) != "":
            nb_error += 1

        if CM_DEV_004(self) != "":
            nb_error += 1

        if CM_DEV_005(self) != "":
            nb_error += 1
        self.label_error_rs.setText(self.dic_error.get(CM_DEV_001(self)))
        self.label_error_adresse.setText(self.dic_error.get(CM_DEV_002(self)))
        self.label_error_cp.setText(self.dic_error.get(CM_DEV_003(self)))
        self.label_error_ville.setText(self.dic_error.get(CM_DEV_004(self)))
        self.label_error_mail.setText(self.dic_error.get(CM_DEV_005(self)))
        return nb_error

    def init_app(self):
        try:
            self.numero_edit.setText(self.dev.numero_devis)
            self.spin_base.setValue(self.dev.base)
            self.spin_tva.setValue(self.dev.tva_montant)
            self.spin_total_ht.setValue(self.dev.total_ht)
            self.spin_total_tva.setValue(self.dev.total_tva)
            self.spin_total_ttc.setValue(self.dev.total_ttc)
            self.spin_net_a_payer.setValue(self.dev.total_a_payer)
        except Exception as err:
            logger.error(err)
        self.init_client_list()
        self.init_ligne_devis()

    def calculer_montant_devis(self):
        base = 0.00
        try:
            if not self.edit:
                lignes = self.s.query(assogestion_temp_ligne_devis).filter_by(id_devis=self.dev.id).all()
            else:
                lignes = self.s.query(assogestion_ligne_devis).filter_by(id_devis=self.dev.id).all()
            if lignes:
                for ligne in lignes:
                    base += ligne.total_ht

            montant_tva = self.spin_tva.value()
            total_ht = base + montant_tva
            total_tva = montant_tva
            total_ttc = total_ht + total_tva
            net_a_payer = total_ttc
            self.spin_base.setValue(base)
            self.spin_total_ht.setValue(total_ht)
            self.spin_total_tva.setValue(total_tva)
            self.spin_total_ttc.setValue(total_ttc)
            self.spin_net_a_payer.setValue(net_a_payer)
            self.label_error_base.setText(self.dic_error.get(CM_DEV_007(base)))

        except Exception as err:
            logger.error(err)

    def init_client_list(self):
        self.cb_client.clear()
        try:
            clients = self.s.query(assogestion_client).all()
            if clients:
                self.cb_client.addItem("")
                for c in clients:
                    self.cb_client.addItem(f"{c.id_client}-{c.raison_sociale}")
            if not self.edit:
                dev = self.s.query(assogestion_temp_devis).filter_by(id=self.dev.id).first()
            else:
                dev = self.s.query(assogestion_devis).filter_by(id=self.dev.id).first()
            c = self.s.query(assogestion_client).filter_by(id_client=dev.code_client).first()
            if c:
                self.cb_client.setCurrentText(f"{c.id_client}-{c.raison_sociale}")
        except Exception as err:
            logger.error(err)

    def set_client_via_cb(self):
        if self.cb_client.currentText().split('-')[0] != self.code_client_edit.text():
            self.set_client()

    def set_client(self):
        try:
            c = self.s.query(assogestion_client).filter_by(id_client=self.cb_client.currentText().split('-')[0]).first()
            if c:
                self.code_client_edit.setText(c.id_client)
                self.rs_edit.setText(c.raison_sociale)
                self.add_edit.setText(c.adresse_client)
                self.cp_edit.setText(c.cp_client)
                self.cb_ville.setCurrentText(c.ville_client)
                self.mail_edit.setText(c.mail_client)
            else:
                self.code_client_edit.setText("")
                self.rs_edit.setText("")
                self.add_edit.setText("")
                self.cp_edit.setText("")
                self.cb_ville.setCurrentText("")
                self.mail_edit.setText("")
                self.label_error_ville.setText("")
        except Exception as err:
            logger.error(err)

    def init_ligne_devis(self):
        try:
            if not self.edit:
                res = self.s.query(assogestion_temp_ligne_devis).filter_by(id_devis=self.dev.id).all()
            else:
                res = self.s.query(assogestion_ligne_devis).filter_by(id_devis=self.dev.id).all()
            self.tab_ligne.clear()
            self.tab_ligne.setRowCount(0)
            self.tab_ligne.setColumnCount(6)
            self.tab_ligne.setHorizontalHeaderLabels(
                ["ID", "Code", "Description", "Quantité", "Prix HT", "Total HT"])
            if res:
                for i, r in enumerate(res):
                    logger.info(i)
                    self.tab_ligne.insertRow(i)
                    result = r.id, r.code, r.desc, r.qty, r.pu_ht, r.total_ht
                    for j, res in enumerate(result):
                        self.tab_ligne.setItem(i, j, QTableWidgetItem(f'{result[j]}'))
                self.tab_ligne.resizeColumnsToContents()
                self.calculer_montant_devis()
        except Exception as err:
            logger.error(err)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        try:
            res = self.s.query(assogestion_temp_devis).filter_by(numero_devis=self.dev.numero_devis).first()
            if res:
                self.s.delete(res)
                self.s.commit()
            self.finished.emit(True)
            event.accept()
        except Exception as err:
            logger.error(err)

    def client_enr_005(self):
        controle_enrichissement_ville(self)

    def save_client(self):
        try:
            validation = self.valider_saisie_client()
            if validation == 0:
                c = self.s.query(assogestion_client).filter_by(
                    id_client=self.cb_client.currentText().split('-')[0]).first()
                if c:
                    c.raison_sociale = self.rs_edit.text()
                    c.adresse_client = self.add_edit.text()
                    c.cp_client = self.cp_edit.text()
                    c.ville_client = self.cb_ville.currentText()
                    c.mail_client = self.mail_edit.text()
                else:
                    c = self.s.query(assogestion_client).order_by(assogestion_client.id_client).all()
                    if c:
                        id_client = int(c[-1].id_client.split('CL')[1]) + 1
                        id_client = f"CL00{id_client}"
                    else:
                        id_client = f"CL001"
                    new_client = assogestion_client(
                        id_client=id_client,
                        raison_sociale=self.rs_edit.text(),
                        adresse_client=self.add_edit.text(),
                        cp_client=self.cp_edit.text(),
                        ville_client=self.cb_ville.currentText(),
                        mail_client=self.mail_edit.text()
                    )
                    self.s.add(new_client)
                self.s.commit()
                if not self.edit:
                    dev = self.s.query(assogestion_temp_devis).filter_by(id=self.dev.id).first()
                else:
                    dev = self.s.query(assogestion_devis).filter_by(id=self.dev.id).first()
                c = self.s.query(assogestion_client).filter_by(raison_sociale=self.rs_edit.text()).first()
                if dev:
                    dev.code_client = c.id_client
                self.s.commit()
                self.info_client_dev("Client sauvegardé", f"Le client {self.cb_client.currentText()} a été sauvegardé")
                self.init_client_list()

        except Exception as err:
            logger.error(err)

    def open_new_ligne_devis(self):
        try:
            self.application = DetailLigneDevAPP(self.s, False, self.dev, None, self.edit)
            self.application.finished.connect(self.init_app)
        except Exception as err:
            logger.error(err)

    def open_ligne_devis(self):
        try:
            if self.tab_ligne.currentItem().isSelected():
                if self.tab_ligne.currentItem().column() == 0:
                    if not self.edit:
                        ligne = self.s.query(assogestion_temp_ligne_devis).filter_by(
                            id=self.tab_ligne.currentItem().text()).first()
                    else:
                        ligne = self.s.query(assogestion_ligne_devis).filter_by(
                            id=self.tab_ligne.currentItem().text()).first()
                    if ligne:
                        self.application = DetailLigneDevAPP(self.s, True, self.dev, ligne, self.edit)
                        self.application.finished.connect(self.init_app)
        except Exception as err:
            logger.error(err)

    def valider_saisie_devis(self):
        nb_error = 0
        try:
            if CM_DEV_007(self.spin_base.value()) != "":
                nb_error += 1
            if CM_DEV_006(self) != "":
                nb_error += 1
            self.label_error_select_client.setText(self.dic_error.get(CM_DEV_006(self)))
            self.label_error_base.setText(self.dic_error.get(CM_DEV_007(self.spin_base.value())))
        except Exception as err:
            logger.error(err)
            nb_error += 1
        return nb_error

    def save_devis(self):
        validation_client = self.valider_saisie_client()
        validation_devis = self.valider_saisie_devis()
        logger.info(f"Client valide : {validation_client} | devis_valide: {validation_devis}")
        if validation_client == 0 and validation_devis == 0:
            try:
                if not self.edit:

                    try:
                        temp_dev = self.s.query(assogestion_temp_devis).filter_by(
                            numero_devis=self.numero_edit.text()).first()
                        if temp_dev:

                            new_dev = assogestion_devis(
                                numero_devis=self.numero_edit.text(),
                                code_client=temp_dev.code_client,
                                date=datetime.now(),
                                base=self.spin_base.value(),
                                tva_montant=self.spin_tva.value(),
                                total_ht=self.spin_total_ht.value(),
                                total_tva=self.spin_total_tva.value(),
                                total_ttc=self.spin_total_ttc.value(),
                                total_a_payer=self.spin_net_a_payer.value(),
                            )
                            self.s.add(new_dev)
                            self.s.commit()
                            dev = self.s.query(assogestion_devis).filter_by(
                                numero_devis=self.numero_edit.text()).first()
                            lignes_temp_dev = self.s.query(assogestion_temp_ligne_devis).filter_by(
                                id_devis=temp_dev.id).all()
                            for ltd in lignes_temp_dev:
                                new_ligne_dev = assogestion_ligne_devis(
                                    id_devis=dev.id,
                                    code=ltd.code,
                                    desc=ltd.desc,
                                    qty=ltd.qty,
                                    pu_ht=ltd.pu_ht,
                                    total_ht=ltd.total_ht
                                )
                                self.s.add(new_ligne_dev)
                                self.s.commit()
                    except Exception as err:
                        logger.error(err)

                else:
                    dev = self.s.query(assogestion_devis).filter_by(numero_devis=self.numero_edit.text()).first()
                    c = self.s.query(assogestion_client).filter_by(raison_sociale=self.rs_edit.text()).first()

                    dev.code_client = c.id_client
                    dev.base = self.spin_base.value()
                    dev.tva_montant = self.spin_tva.value()
                    dev.total_ht = self.spin_total_ht.value()
                    dev.total_tva = self.spin_total_tva.value()
                    dev.total_ttc = self.spin_total_ttc.value()
                    dev.total_a_payer = self.spin_net_a_payer.value()
                    self.s.commit()
            except Exception as err:
                logger.error(err)
            finally:
                self.close()

    def facturer_devis(self):
        if self.edit:
            dev = self.s.query(assogestion_devis).filter_by(id=self.dev.id).first()
            lignes_dev = self.s.query(assogestion_ligne_devis).filter_by(id_devis=dev.id).all()
            try:
                fac = self.s.query(assogestion_facture).order_by(assogestion_facture.id).all()
                if fac:
                    id_facture = int(fac[-1].numero_facture.split('FC')[1]) + 1
                else:
                    id_facture = 1
                new_fac = assogestion_facture(
                    prefixe_facture="FC",
                    numero_facture=f"FC000{id_facture}",
                    code_client=dev.code_client,
                    date=datetime.now(),
                    base=dev.base,
                    tva_montant=dev.tva_montant,
                    total_ht=dev.total_ht,
                    total_tva=dev.total_tva,
                    total_ttc=dev.total_ttc,
                    total_a_payer=dev.total_a_payer,
                )
                self.s.add(new_fac)
                self.s.commit()

                fac = self.s.query(assogestion_facture).filter_by(numero_facture=f"FC000{id_facture}").first()
                for ld in lignes_dev:
                    new_ligne_fac = assogestion_ligne_facture(
                        id_facture=fac.id,
                        code=ld.code,
                        desc=ld.desc,
                        qty=ld.qty,
                        pu_ht=ld.pu_ht,
                        total_ht=ld.total_ht
                    )
                    self.s.add(new_ligne_fac)
                    self.s.commit()
                self.application = DetailFactAPP(self.Session, True, fac)
                self.close()
            except Exception as err:
                logger.error(err)

    def info_client_dev(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Détail Devis",
            message,
            texte,
            "INFO"
        )

    def error_client_dev(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Détail Devis",
            message,
            texte,
            "ERROR"
        )

    def export_pdf(self):
        excel = None
        try:
            dev = self.s.query(assogestion_devis).filter_by(id=self.dev.id).first()
            c = self.s.query(assogestion_client).filter_by(id_client=dev.code_client).first()
            lignes_dev = self.s.query(assogestion_ligne_devis).filter_by(id_devis=dev.id).all()
            wb = openpyxl.load_workbook(f"{getcwd()}\\modele\\modele_devis.xlsx")
            sheet = wb.active
            sheet["F3"] = dev.numero_devis
            sheet["G3"] = datetime.strftime(dev.date, "%d-%m-%Y")
            sheet["H3"] = dev.code_client
            sheet["F9"] = c.raison_sociale
            sheet["F10"] = c.adresse_client
            sheet["F11"] = f"{c.cp_client} {c.ville_client}"
            sheet["C17"] = datetime.strftime(dev.date  + timedelta(days=30), "%d-%m-%Y")
            if lignes_dev:
                for i, ligne in enumerate(lignes_dev):
                    logger.info(i)
                    sheet[f"B2{i}"] = ligne.code
                    sheet[f"C2{i}"] = ligne.qty
                    sheet[f"D2{i}"] = ligne.desc
                    sheet[f"G2{i}"] = ligne.pu_ht
                    sheet[f"H2{i}"] = ligne.total_ht
            sheet[f"C36"] = dev.base
            sheet[f"D36"] = dev.tva_montant
            sheet[f"E36"] = dev.total_ht
            sheet[f"F36"] = dev.total_tva
            sheet[f"G36"] = dev.total_ttc
            sheet[f"H36"] = dev.total_a_payer
            wb.save(f"{getcwd()}\\Export\\Devis\\{dev.numero_devis}_{datetime.now().strftime('%Y%m%d')}.xlsx")
            wb.close()

            # Open Microsoft Excel
            excel = client.Dispatch("Excel.Application")

            # Read Excel File
            sheets = excel.Workbooks.Open(
                f"{getcwd()}\\Export\\Devis\\{dev.numero_devis}_{datetime.now().strftime('%Y%m%d')}.xlsx")
            work_sheets = sheets.Worksheets[0]

            # Convert into PDF File
            work_sheets.ExportAsFixedFormat(0,
                                            f"{getcwd()}\\Export\\Devis\\{dev.numero_devis}_{datetime.now().strftime('%Y%m%d')}.pdf")

        except Exception as err:
            logger.error(err)
        finally:
            if excel:
                excel.Quit()
            self.info_client_dev("Export réussie", "Le document a bien été exporté en PDF")

