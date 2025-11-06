from datetime import datetime

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from loguru import logger

from IHM import detail_cot
from utils.message import pop_up
from utils.models import assogestion_cotisation


class DetailCotAPP(QtWidgets.QMainWindow, detail_cot.Ui_detail_cotisation):
    finished = pyqtSignal(bool)

    def __init__(self, Session, edit, cot, parent=None):
        super(DetailCotAPP, self).__init__(parent)
        try:
            self.Session = Session
            self.edit = edit
            self.cot = cot
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.init_app()
            self.button_save.clicked.connect(self.save)
            self.montant_edit.textChanged.connect(self.calculer_total)
            self.montant_bulletin_edit.textChanged.connect(self.calculer_total)
            self.dons_edit.textChanged.connect(self.calculer_total)
            self.button_save.setIcon(QIcon("save.png"))
            self.button_retour.setIcon(QIcon('retour.png'))
            self.button_retour.clicked.connect(self.close)
            self.show()
        except Exception as err:
            logger.error(err)

    def init_app(self):
        if self.edit:
            s = self.Session()
            cot = s.query(assogestion_cotisation).filter_by(
                id_cotisation=self.cot).first()
            s.close()
            if cot:
                self.nom_edit.setText(cot.nom_cotisation)
                self.date_debut_edit.setDate(cot.date_debut_cotisation)
                self.date_fin_edit.setDate(cot.date_fin_cotisation)
                self.montant_edit.setText(str(cot.tarif))
                self.montant_bulletin_edit.setText(str(cot.tarif_bulletin))
                self.dons_edit.setText(str(cot.dons))
                self.calculer_total()
                self.check_bulletin.setChecked(cot.bulletin)

    def calculer_total(self):
        try:
            if self.montant_edit.text() != "" and self.montant_bulletin_edit.text() != "" and self.dons_edit.text() != "":
                total = float(self.montant_edit.text()) + float(self.montant_bulletin_edit.text()) + float(
                    self.dons_edit.text())
            else:
                total = 0
            self.total_edit.setText(str(total))
            if float(self.montant_bulletin_edit.text()) > 0:
                self.check_bulletin.setChecked(True)
            else:
                self.check_bulletin.setChecked(False)
        except Exception as err:
            logger.error(err)

    def save(self):
        if not self.edit:
            date_debut = None
            date_fin = None
            if self.nom_edit.text() != "":
                s = self.Session()
                try:
                    date_debut = self.date_debut_edit.text()
                    date_fin = self.date_fin_edit.text()
                    date_debut = datetime.strptime(date_debut, "%d/%m/%Y")
                    date_fin = datetime.strptime(date_fin, "%d/%m/%Y")
                    new_cotisation = assogestion_cotisation(
                        nom_cotisation=self.nom_edit.text(),
                        date_debut_cotisation=date_debut,
                        date_fin_cotisation=date_fin,
                        tarif=float(self.montant_edit.text()),
                        tarif_bulletin=float(self.montant_bulletin_edit.text()),
                        dons=float(self.dons_edit.text()),
                        bulletin = self.check_bulletin.isChecked()
                    )
                    s.add(new_cotisation)
                    s.commit()
                except Exception as err:
                    logger.error(err)
                finally:
                    s.close()
                    self.close()
            else:
                self.erreur_saisie("Saisie impossible", "Le type de la cotisation ne doit pas être vide")
        else:
            s = self.Session()
            cot = s.query(assogestion_cotisation).filter_by(
                id_cotisation=self.cot).first()

            if cot:
                date_debut = self.date_debut_edit.text()
                date_fin = self.date_fin_edit.text()
                date_debut = datetime.strptime(date_debut, "%d/%m/%Y")
                date_fin = datetime.strptime(date_fin, "%d/%m/%Y")
                cot.nom_cotisation = self.nom_edit.text(),
                cot.date_debut_cotisation = date_debut,
                cot.date_fin_cotisation = date_fin,
                cot.tarif = float(self.montant_edit.text()),
                cot.tarif_bulletin = float(self.montant_bulletin_edit.text()),
                cot.dons = float(self.dons_edit.text())
                cot.bulletin = self.check_bulletin.isChecked()
                s.commit()
            s.close()
            self.close()

    def closeEvent(self, event):
        if self.edit:
            s = self.Session()
            cot = s.query(assogestion_cotisation).filter_by(
                nom_cotisation=self.nom_edit.text()).first()
            cot.locked = False
            cot.locked_by = None
            s.commit()
            s.close()
        self.finished.emit(True)
        event.accept()

    def erreur_saisie(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Cotisation",
            message,
            texte,
            "ERROR"
        )
