from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from loguru import logger

from IHM import adh_cot
from utils.GenerationRecuAPP import ExportRecuApp
from utils.adhesion_controle import controle_adhesion_presence
from utils.format_input import format_date_to_database
from utils.message import pop_up
from utils.models import assogestion_cotisation, assogestion_adh_dons, assogestion_adherents


class AdhCotAPP(QtWidgets.QMainWindow, adh_cot.Ui_cotisation_adh):
    finished = pyqtSignal(bool)

    def __init__(self, Session, code_adh, edit, adh_dons, parent=None):
        super(AdhCotAPP, self).__init__(parent)
        try:
            self.Session = Session
            self.application = None
            self.code_adh = code_adh
            self.edit = edit
            self.adh_dons = adh_dons
            self.setupUi(self)
            self.init_ihm()
            self.cb_type_cot.currentIndexChanged.connect(self.set_data)
            self.dons_edit.textChanged.connect(self.calculer_total)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.button_save.clicked.connect(self.save)
            self.button_generer_recu.clicked.connect(self.generer_recu)
            self.button_generer_recu.setIcon(QIcon("recu.png"))
            self.dic_error = {
                "ADHESION_CTRL_001": "une adhesion identique existe déjà pour cet adhérent",
                "ADHESION_CTRL_002": "Une adhésion existe déjà pour cette adhérent sur l'année en cours",
                "": ""
            }
            self.show()
        except Exception as err:
            logger.error(err)

    def init_ihm(self):
        s = self.Session()
        self.code_edit.setText(str(self.code_adh))
        req_cot = s.query(assogestion_cotisation).filter_by(type="Cotisation").order_by(assogestion_cotisation.nom_cotisation).all()
        if req_cot:
            self.cb_type_cot.addItem("")
            for r in req_cot:
                self.cb_type_cot.addItem(r.nom_cotisation)
        s.close()
        if self.adh_dons:
            cot = s.query(assogestion_cotisation).filter_by(id_cotisation=self.adh_dons.id_cotisation).first()
            self.cb_type_cot.setCurrentText(cot.nom_cotisation)
        if self.edit:
            self.set_data()

    def set_data(self):
        logger.info(f"Valeur actuelle: {self.cb_type_cot.currentText()}")
        s = self.Session()
        try:
            req_cot = s.query(assogestion_cotisation).filter_by(nom_cotisation=self.cb_type_cot.currentText()).first()
            if req_cot:
                logger.info("Cotisation trouvée")
                if self.edit:
                    #
                    self.montant_edit.setText(str(req_cot.tarif))
                    self.montant_bulletin_edit.setText(str(req_cot.tarif_bulletin))
                    self.dons_edit.setText(str(req_cot.dons))
                    self.date_debut_edit.setDate(req_cot.date_debut_cotisation)
                    self.date_fin_edit.setDate(req_cot.date_fin_cotisation)
                    self.id_cotisation_edit.setText(str(req_cot.id_cotisation))
                    self.calculer_total()
                else:
                    self.montant_edit.setText(str(req_cot.tarif))
                    self.montant_bulletin_edit.setText(str(req_cot.tarif_bulletin))
                    self.dons_edit.setText(str(req_cot.dons))
                    self.date_debut_edit.setDate(req_cot.date_debut_cotisation)
                    self.date_fin_edit.setDate(req_cot.date_fin_cotisation)
                    self.id_cotisation_edit.setText(str(req_cot.id_cotisation))
            else:
                self.montant_edit.setText(str(0))
                self.montant_bulletin_edit.setText(str(0))
                self.dons_edit.setText(str(0))
                self.calculer_total()
        except Exception as err:
            logger.error(err)
        finally:
            s.close()

    def calculer_total(self):
        try:
            if self.montant_edit.text() != "" and self.montant_bulletin_edit.text() != "" and self.dons_edit.text() != "":
                total = float(self.montant_edit.text()) + float(self.montant_bulletin_edit.text()) + float(
                    self.dons_edit.text())
            else:
                total = 0
            self.total_edit.setText(str(total))
        except Exception as err:
            logger.error(err)

    def save(self):
        s = self.Session()
        try:
            # ETAPE 1: Contrôle
            liste_error_code = []
            if not self.adh_dons:
                error_code = controle_adhesion_presence(s, self.code_edit.text(), self.id_cotisation_edit.text(), self.date_debut_edit.text(), self.date_fin_edit.text())
                if error_code != "":
                    liste_error_code.append(error_code)
            # ETAPE 2: Sauvegarde
            if not liste_error_code:
                if self.edit:
                    try:
                        save_adh_dons = s.query(assogestion_adh_dons).filter_by(id_cotisation=self.adh_dons.id_cotisation, code_adherent=self.adh_dons.code_adherent).first()
                        save_adh_dons.code_adherent=self.code_edit.text()
                        save_adh_dons.id_cotisation=self.id_cotisation_edit.text()
                        save_adh_dons.montant_adh=float(self.montant_edit.text())
                        save_adh_dons.montant_bulletin=float(self.montant_bulletin_edit.text())
                        save_adh_dons.montant_dons=float(self.dons_edit.text())
                        save_adh_dons.date_debut_adh_don=format_date_to_database(self.date_debut_edit.text())
                        save_adh_dons.date_fin_adh_don=format_date_to_database(self.date_fin_edit.text())
                        s.commit()
                    except Exception as err:
                        logger.error(err)
                else:
                    try:
                        new_adh_dons = assogestion_adh_dons(
                            code_adherent=self.code_edit.text(),
                            id_cotisation=self.id_cotisation_edit.text(),
                            montant_adh=float(self.montant_edit.text()),
                            montant_bulletin=float(self.montant_bulletin_edit.text()),
                            montant_dons=float(self.dons_edit.text()),
                            date_debut_adh_don = format_date_to_database(self.date_debut_edit.text()),
                            date_fin_adh_don = format_date_to_database(self.date_fin_edit.text())
                        )
                        s.add(new_adh_dons)
                        s.commit()
                    except Exception as err:
                        logger.error(err)
                self.close()
            else:
                message = ""
                for c in liste_error_code:
                    message += f"{c}: {self.dic_error.get(c)}\n"
                self.erreur_saisie("Enregistrement impossible", message)
        except Exception as err:
            logger.error(err)
        finally:
            s.close()

    def closeEvent(self, event):
        self.finished.emit(True)
        event.accept()

    def erreur_saisie(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Adhérent- Adhésion",
            message,
            texte,
            "ERROR"
        )

    def generer_recu(self):
        try:
            s = self.Session()
            adh = s.query(assogestion_adherents).filter_by(code_adherent=self.code_edit.text()).first()
            if adh.email_adherent in ("", None):
                self.erreur_saisie("Envoi par mail impossible", "L'adhérent n'a pas d'email, le reçu ne pourra pas être envoyé par mail.\n Il sera enregistré localement pour un envoi papier")
            if not adh.adherent_date_adhesion:
                self.erreur_saisie("Génération du reçu impossible",
                                   "La date de réglement n'a pas été renseignée, le reçu ne peut pas être généré")

            else:
                self.application = ExportRecuApp(self.Session, self.code_edit.text())
                self.application.finished.connect(self.do_something)
                self.hide()
            s.close()
        except Exception as err:
            logger.error(err)

    def do_something(self):
        logger.info("do_something")
        self.show()