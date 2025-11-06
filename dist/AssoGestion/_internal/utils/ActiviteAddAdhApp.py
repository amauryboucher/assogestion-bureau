from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTableWidgetItem
from loguru import logger
from sqlalchemy import or_

from IHM import activite_add_adh
from utils.PopUpPartApp import PopupPartApp
from utils.message import pop_up
from utils.models import assogestion_act_adh, assogestion_activite, assogestion_adherents


class ActiviteAddAdhAPP(QtWidgets.QMainWindow, activite_add_adh.Ui_activite_add_adh):
    add = pyqtSignal(bool)

    def __init__(self, Session, act, parent=None):
        super(ActiviteAddAdhAPP, self).__init__(parent)
        try:
            self.Session = Session
            self.act = act
            self.application = None
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.init_app()
            self.search_edit.textChanged.connect(self.search_app)
            self.tab_adh.doubleClicked.connect(self.ask_add_participant)

            self.show()
        except Exception as err:
            logger.error(err)

    def init_app(self):
        s = self.Session()
        res = s.query(assogestion_adherents).order_by(
            assogestion_adherents.code_adherent).all()
        self.tab_adh.clear()
        self.tab_adh.setRowCount(0)
        if res:
            self.tab_adh.setColumnCount(5)
            self.tab_adh.setHorizontalHeaderLabels(["Ajouter", "Code", "Titre", "Nom", "Prenom"])
            for i, r in enumerate(res):
                self.tab_adh.insertRow(i)
                self.tab_adh.setItem(i, 0, QTableWidgetItem(f'{r.code_adherent}'))
                self.tab_adh.setItem(i, 1, QTableWidgetItem(f'{r.titre_adherent}'))
                self.tab_adh.setItem(i, 2, QTableWidgetItem(f'{r.nom_adherent}'))
                self.tab_adh.setItem(i, 3, QTableWidgetItem(f'{r.prenom_adherent}'))

            self.tab_adh.resizeColumnsToContents()
        s.close()

    def ask_add_participant(self):
        try:
            code = self.tab_adh.currentItem().text()
            logger.info(code)
            s = self.Session()
            act = s.query(assogestion_activite).filter_by(id_activite=self.act).first()
            adh = s.query(assogestion_adherents).filter_by(code_adherent=code).first()
            adh_act = s.query(assogestion_act_adh).filter_by(code_adherent=adh.code_adherent,
                                                             id_activite=self.act).first()
            if adh_act:

                pop_up(self, "Asso'Gestion - AMSE - Activité",
                       f"Ajout d'un participant à l'activité {act.libelle_activite}",
                       f"L'adhérent {adh.prenom_adherent} {adh.nom_adherent} participe déjà à l'activité {act.libelle_activite}",
                       "WARNING")
            else:
                self.application = PopupPartApp(act, adh)
                self.application.flag.connect(self.add_participant)
        except Exception as err:
            logger.error(err)

    def add_participant(self, value):
        try:
            montant, nb, a_payer, adh, act = value
            s = self.Session()
            new_adh_act = assogestion_act_adh(
                code_adherent=adh.code_adherent,
                id_activite=act.id_activite,
                montant=montant,
                nombre=nb,
                a_payer=a_payer
            )
            s.add(new_adh_act)
            s.commit()
            res = s.query(assogestion_activite).filter_by(id_activite=act.id_activite).first()
            res.nb_participant_activite += nb
            s.commit()
            s.close()
            self.add.emit(True)
        except Exception as err:
            logger.error(err)

    def closeEvent(self, event):
        event.accept()

    def search_app(self):
        if self.search_edit.text() != "":
            s = self.Session()
            try:
                res = s.query(assogestion_adherents).filter(or_(
                    assogestion_adherents.nom_adherent.ilike(f"%{self.search_edit.text()}%"),
                    assogestion_adherents.prenom_adherent.ilike(f"%{self.search_edit.text()}%"))).all()
                self.tab_adh.clear()
                self.tab_adh.setRowCount(0)
                if res:
                    self.tab_adh.setColumnCount(5)
                    self.tab_adh.setHorizontalHeaderLabels(["Ajouter", "Code", "Titre", "Nom", "Prenom"])
                    for i, r in enumerate(res):
                        self.tab_adh.insertRow(i)
                        self.tab_adh.setItem(i, 0, QTableWidgetItem(f'{r.code_adherent}'))
                        self.tab_adh.setItem(i, 1, QTableWidgetItem(f'{r.titre_adherent}'))
                        self.tab_adh.setItem(i, 2, QTableWidgetItem(f'{r.nom_adherent}'))
                        self.tab_adh.setItem(i, 3, QTableWidgetItem(f'{r.prenom_adherent}'))

                    self.tab_adh.resizeColumnsToContents()
            except Exception as err:
                logger.error(err)
            s.close()
        else:
            self.init_app()
