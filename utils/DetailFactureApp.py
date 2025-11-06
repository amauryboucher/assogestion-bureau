from datetime import datetime
from os import getcwd

import openpyxl
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem
from win32com import client

from IHM import facture
from utils.DetailLigneFactureApp import DetailLigneFactAPP
from utils.enrichissement import controle_enrichissement_ville
from utils.facture_controls import *
from utils.message import pop_up
from utils.models import assogestion_client, assogestion_facture, assogestion_ligne_facture


class DetailFactAPP(QtWidgets.QMainWindow, facture.Ui_facture):
    finished = pyqtSignal(bool)

    def __init__(self, Session, edit, fac, parent=None):
        super(DetailFactAPP, self).__init__(parent)
        try:
            self.Session = Session
            self.edit = edit
            self.fac = fac
            self.setupUi(self)
            self.application = None
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.butt_save.setIcon(QIcon("save.png"))

            self.dic_error = {
                "CM_FAC_001": "La raison sociale du client est obligatoire",
                "CM_FAC_002": "L'adresse du client est obligatoire",
                "CM_FAC_003": "Le code postal de l’adhérent est obligatoire",
                "CM_FAC_004": "La ville de l’adhérent ne doit pas être vide",
                "CM_FAC_005": "Le format de l’email n’est pas correct",
                "CM_FAC_006": "La facture doit être attachée à un client",
                "CM_FAC_007": "Le montant doit être supérieur à 0.00 €",
                "CM_FAC_008": "Le montant déjà reglé ne peut pas être supérieur à la base",
                "": ""
            }
            self.cb_client.currentTextChanged.connect(self.set_client)
            self.butt_save.clicked.connect(self.save_client)
            self.tab_ligne.doubleClicked.connect(self.open_ligne_facture)
            self.button_ligne.clicked.connect(self.open_new_ligne_facture)
            self.button_valider.clicked.connect(self.save_facture)
            self.cp_edit.textChanged.connect(self.client_enr_005)
            self.spin_regle.valueChanged.connect(self.valider_saisie_facture)
            self.button_pdf.clicked.connect(self.export_pdf)
            self.init_app()
            self.show()
        except Exception as err:
            logger.error(err)

    def set_client(self):
        logger.info("Initialisation du client de la facture")
        try:
            s = self.Session()
            c = s.query(assogestion_client).filter_by(id_client=self.cb_client.currentText().split('-')[0]).first()
            if c:
                self.code_client_edit.setText(c.id_client)
                self.rs_edit.setText(c.raison_sociale)
                self.add_edit.setText(c.adresse_client)
                self.cp_edit.setText(c.cp_client)
                self.client_enr_005()
                self.cb_ville.setCurrentText(c.ville_client)
                self.mail_edit.setText(c.mail_client)
                # self.valider_saisie_client()
            else:
                self.code_client_edit.setText("")
                self.rs_edit.setText("")
                self.add_edit.setText("")
                self.cp_edit.setText("")
                self.cb_ville.setCurrentText("")
                self.mail_edit.setText("")
                self.label_error_ville.setText("")
            s.close()
        except Exception as err:
            logger.error(err)

    def valider_saisie_client(self):
        nb_error = 0
        if CM_FAC_001(self) != "":
            nb_error += 1

        if CM_FAC_002(self) != "":
            nb_error += 1

        if CM_FAC_003(self) != "":
            nb_error += 1

        if CM_FAC_004(self) != "":
            nb_error += 1

        if CM_FAC_005(self) != "":
            nb_error += 1
        self.label_error_rs.setText(self.dic_error.get(CM_FAC_001(self)))
        self.label_error_adresse.setText(self.dic_error.get(CM_FAC_002(self)))
        self.label_error_cp.setText(self.dic_error.get(CM_FAC_003(self)))
        self.label_error_ville.setText(self.dic_error.get(CM_FAC_004(self)))
        self.label_error_mail.setText(self.dic_error.get(CM_FAC_005(self)))
        return nb_error

    def save_client(self):
        s = self.Session()
        try:
            validation = self.valider_saisie_client()
            if validation == 0:
                c = s.query(assogestion_client).filter_by(id_client=self.cb_client.currentText().split('-')[0]).first()
                if c:
                    c.raison_sociale = self.rs_edit.text()
                    c.adresse_client = self.add_edit.text()
                    c.cp_client = self.cp_edit.text()
                    c.ville_client = self.cb_ville.currentText()
                    c.mail_client = self.mail_edit.text()
                else:
                    c = s.query(assogestion_client).order_by(assogestion_client.id_client).all()
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
                    s.add(new_client)
                s.commit()
                if not self.edit:
                    fac = s.query(assogestion_temp_facture).filter_by(id=self.fac.id).first()
                else:
                    fac = s.query(assogestion_facture).filter_by(id=self.fac.id).first()
                c = s.query(assogestion_client).filter_by(raison_sociale=self.rs_edit.text()).first()
                if fac:
                    fac.code_client = c.id_client
                s.commit()
                self.info_client_fac("Client sauvegardé", f"Le client {self.cb_client.currentText()} a été sauvegardé")
                self.init_client_list()

        except Exception as err:
            logger.error(err)
        finally:
            s.close()

    def init_app(self):
        try:
            self.numero_edit.setText(self.fac.numero_facture)
            self.spin_base.setValue(self.fac.base)
            self.spin_tva.setValue(self.fac.tva_montant)
            self.spin_total_ht.setValue(self.fac.total_ht)
            self.spin_total_tva.setValue(self.fac.total_tva)
            self.spin_total_ttc.setValue(self.fac.total_ttc)
            self.spin_regle.setValue(self.fac.total_regle)
            self.spin_net_a_payer.setValue(self.fac.total_a_payer)
        except Exception as err:
            logger.error(err)
        self.init_client_list()
        self.init_ligne_facture()
        # self.calculer_montant_facture()

    def calculer_montant_facture(self):
        base = 0.00
        logger.info("Calcul du montant de la facture")
        s = self.Session()
        try:
            if not self.edit:
                lignes = s.query(assogestion_temp_ligne_facture).filter_by(id_facture=self.fac.id).all()
            else:
                lignes = s.query(assogestion_ligne_facture).filter_by(id_facture=self.fac.id).all()
            if lignes:
                for ligne in lignes:
                    base += ligne.total_ht

            montant_tva = self.spin_tva.value()
            total_ht = base + montant_tva
            total_tva = montant_tva
            total_ttc = total_ht + total_tva
            net_a_payer = total_ttc - self.spin_regle.value()
            self.spin_base.setValue(base)
            self.spin_total_ht.setValue(total_ht)
            self.spin_total_tva.setValue(total_tva)
            self.spin_total_ttc.setValue(total_ttc)
            self.spin_net_a_payer.setValue(net_a_payer)
            self.label_error_base.setText(self.dic_error.get(CM_FAC_007(base)))
            self.label_error_regle.setText(self.dic_error.get(CM_FAC_008(self)))

        except Exception as err:
            logger.error(err)
        finally:
            s.close()

    def init_client_list(self):
        logger.info("Initialisation de la liste client")
        self.cb_client.clear()
        try:
            s = self.Session()
            clients = s.query(assogestion_client).all()
            if clients:
                self.cb_client.addItem("")
                for c in clients:
                    self.cb_client.addItem(f"{c.id_client}-{c.raison_sociale}")
            s.close()
            if not self.edit:
                fac = s.query(assogestion_temp_facture).filter_by(id=self.fac.id).first()
            else:
                fac = s.query(assogestion_facture).filter_by(id=self.fac.id).first()
            c = s.query(assogestion_client).filter_by(id_client=fac.code_client).first()
            if c:
                self.cb_client.setCurrentText(f"{c.id_client}-{c.raison_sociale}")
            #self.set_client()
        except Exception as err:
            logger.error(err)

    def init_ligne_facture(self):
        logger.info("Initialisation des lignes de la factures")
        s = self.Session()
        try:
            if not self.edit:
                res = s.query(assogestion_temp_ligne_facture).filter_by(id_facture=self.fac.id).all()
            else:
                res = s.query(assogestion_ligne_facture).filter_by(id_facture=self.fac.id).all()
            self.tab_ligne.clear()
            self.tab_ligne.setRowCount(0)
            self.tab_ligne.setColumnCount(6)
            self.tab_ligne.setHorizontalHeaderLabels(
                ["ID", "Code", "Description", "Quantité", "Prix HT", "Total HT"])
            if res:
                self.calculer_montant_facture()
                for i, r in enumerate(res):
                    self.tab_ligne.insertRow(i)
                    result = r.id, r.code, r.desc, r.qty, r.pu_ht, r.total_ht
                    for j, res in enumerate(result):
                        self.tab_ligne.setItem(i, j, QTableWidgetItem(f'{result[j]}'))
                self.tab_ligne.resizeColumnsToContents()
        except Exception as err:
            logger.error(err)
        finally:
            s.close()

    def open_ligne_facture(self):
        s = self.Session()
        if self.tab_ligne.currentItem().isSelected():
            if self.tab_ligne.currentItem().column() == 0:
                if not self.edit:
                    ligne = s.query(assogestion_temp_ligne_facture).filter_by(
                        id=self.tab_ligne.currentItem().text()).first()
                else:
                    ligne = s.query(assogestion_ligne_facture).filter_by(
                        id=self.tab_ligne.currentItem().text()).first()
                if ligne:
                    self.application = DetailLigneFactAPP(self.Session, True, self.fac, ligne, self.edit)
                    self.application.finished.connect(self.init_app)
        s.close()

    def open_new_ligne_facture(self):
        self.application = DetailLigneFactAPP(self.Session, False, self.fac, None, self.edit)
        self.application.finished.connect(self.init_app)

    def valider_saisie_facture(self):
        nb_error = 0
        try:
            if CM_FAC_007(self.spin_base.value()) != "":
                nb_error += 1
            if CM_FAC_008(self) != "":
                nb_error += 1
            if CM_FAC_006(self) != "":
                nb_error += 1
            self.label_error_select_client.setText(self.dic_error.get(CM_FAC_006(self)))
            self.label_error_base.setText(self.dic_error.get(CM_FAC_007(self.spin_base.value())))
            self.label_error_regle.setText(self.dic_error.get(CM_FAC_008(self)))
        except Exception as err:
            logger.error(err)
            nb_error += 1
        return nb_error

    def save_facture(self):
        validation_client = self.valider_saisie_client()
        validation_facture = self.valider_saisie_facture()
        if validation_client == 0 and validation_facture == 0:
            s = self.Session()
            try:
                if not self.edit:

                    try:
                        temp_fac = s.query(assogestion_temp_facture).filter_by(
                            numero_facture=self.numero_edit.text()).first()
                        if temp_fac:

                            new_fac = assogestion_facture(
                                prefixe_facture="FC",
                                numero_facture=self.numero_edit.text(),
                                code_client=temp_fac.code_client,
                                date=datetime.now(),
                                base=self.spin_base.value(),
                                tva_montant=self.spin_tva.value(),
                                total_ht=self.spin_total_ht.value(),
                                total_tva=self.spin_total_tva.value(),
                                total_ttc=self.spin_total_ttc.value(),
                                total_regle=self.spin_regle.value(),
                                total_a_payer=self.spin_net_a_payer.value(),
                            )
                            s.add(new_fac)
                            s.commit()
                            fac = s.query(assogestion_facture).filter_by(numero_facture=self.numero_edit.text()).first()
                            lignes_temp_fac = s.query(assogestion_temp_ligne_facture).filter_by(
                                id_facture=temp_fac.id).all()
                            for ltf in lignes_temp_fac:
                                new_ligne_fac = assogestion_ligne_facture(
                                    id_facture=fac.id,
                                    code=ltf.code,
                                    desc=ltf.desc,
                                    qty=ltf.qty,
                                    pu_ht=ltf.pu_ht,
                                    total_ht=ltf.total_ht
                                )
                                s.add(new_ligne_fac)
                                s.commit()
                    except Exception as err:
                        logger.error(err)

                else:
                    fac = s.query(assogestion_facture).filter_by(numero_facture=self.numero_edit.text()).first()
                    c = s.query(assogestion_client).filter_by(raison_sociale=self.rs_edit.text()).first()

                    fac.code_client = c.id_client
                    fac.base = self.spin_base.value()
                    fac.tva_montant = self.spin_tva.value()
                    fac.total_ht = self.spin_total_ht.value()
                    fac.total_tva = self.spin_total_tva.value()
                    fac.total_ttc = self.spin_total_ttc.value()
                    fac.total_regle = self.spin_regle.value()
                    fac.total_a_payer = self.spin_net_a_payer.value()
                    s.commit()
            except Exception as err:
                logger.error(err)
            finally:
                s.close()
                self.close()

    def closeEvent(self, event):
        s = self.Session()
        try:
            logger.info("Suppression des factures temporaires")
            temp_fac = s.query(assogestion_temp_facture).filter_by(numero_facture=self.fac.numero_facture).delete()
            s.commit()
            self.finished.emit(True)
            event.accept()
        except Exception as err:
            logger.error(err)
        finally:
            s.close()

    def info_client_fac(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Détail Facture",
            message,
            texte,
            "INFO"
        )

    def error_client_fac(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Détail Facture",
            message,
            texte,
            "ERROR"
        )

    def client_enr_005(self):
        controle_enrichissement_ville(self)

    def export_pdf(self):
        excel = None
        try:
            s = self.Session()
            fac = s.query(assogestion_facture).filter_by(id=self.fac.id).first()
            c = s.query(assogestion_client).filter_by(id_client=fac.code_client).first()
            lignes_fac = s.query(assogestion_ligne_facture).filter_by(id_facture=fac.id).all()
            wb = openpyxl.load_workbook(f"{getcwd()}\\modele\\modele_facture.xlsx")
            sheet = wb.active
            sheet["F3"] = fac.numero_facture
            sheet["G3"] = datetime.strftime(fac.date, "%d-%m-%Y")
            sheet["H3"] = fac.code_client
            sheet["F9"] = c.raison_sociale
            sheet["F10"] = c.adresse_client
            sheet["F11"] = f"{c.cp_client} {c.ville_client}"
            sheet["C17"] = datetime.strftime(fac.date, "%d-%m-%Y")
            if lignes_fac:
                for i, ligne in enumerate(lignes_fac):
                    logger.info(i)
                    sheet[f"B2{i}"] = ligne.code
                    sheet[f"C2{i}"] = ligne.qty
                    sheet[f"D2{i}"] = ligne.desc
                    sheet[f"G2{i}"] = ligne.pu_ht
                    sheet[f"H2{i}"] = ligne.total_ht
            sheet[f"C36"] = fac.base
            sheet[f"D36"] = fac.tva_montant
            sheet[f"E36"] = fac.total_ht
            sheet[f"F36"] = fac.total_tva
            sheet[f"G36"] = fac.total_ttc
            sheet[f"H36"] = fac.total_a_payer
            wb.save(f"{getcwd()}\\Export\\Facture\\{fac.numero_facture}_{datetime.now().strftime('%Y%m%d')}.xlsx")
            wb.close()

            # Open Microsoft Excel
            excel = client.Dispatch("Excel.Application")

            # Read Excel File
            sheets = excel.Workbooks.Open(
                f"{getcwd()}\\Export\\Facture\\{fac.numero_facture}_{datetime.now().strftime('%Y%m%d')}.xlsx")
            work_sheets = sheets.Worksheets[0]

            # Convert into PDF File
            work_sheets.ExportAsFixedFormat(0,
                                            f"{getcwd()}\\Export\\Facture\\{fac.numero_facture}_{datetime.now().strftime('%Y%m%d')}.pdf")

            s.close()
        except Exception as err:
            logger.error(err)
        finally:
            self.info_client_fac("Export réussie", "Le document a bien été exporté en PDF")
            if excel:
                excel.Quit()
