from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from loguru import logger

from IHM import pop_up_part
from utils.add_adh_act_control import adh_act_001


class PopupPartApp(QtWidgets.QMainWindow, pop_up_part.Ui_pop_up):

    def __init__(self, act, adh, parent=None):
        try:
            super(PopupPartApp, self).__init__(parent)
            self.application = None
            self.act = act
            self.adh = adh
            self.code = ""
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.nb_edit.textChanged.connect(self.calculer_montant)
            self.button_valider.clicked.connect(self.ajouter_participant)
            self.show()
        except Exception as err:
            logger.error(err)

    flag = pyqtSignal(list)

    def calculer_montant(self):
        try:
            if self.nb_edit.text() != "":
                montant = float(self.nb_edit.text()) * self.act.tarif_activite
                self.montant_edit.setText(str(montant))
                self.code = adh_act_001(self)
                if self.code != "":
                    self.label_nb_error.setText(
                        f"Nombre maximum de participant atteint. Impossible d'ajouter {self.nb_edit.text()} participant(s) supplémentaire(s)")
                else:
                    self.label_nb_error.setText("")
            else:
                self.montant_edit.setText("0.00")
        except Exception as err:
            logger.error(err)

    def ajouter_participant(self):
        if self.code == "":
            a_payer = False
            if not self.solde_cb.isChecked():
                a_payer = True
            self.flag.emit([float(self.montant_edit.text()), int(self.nb_edit.text()), a_payer, self.adh, self.act])
            self.close()
