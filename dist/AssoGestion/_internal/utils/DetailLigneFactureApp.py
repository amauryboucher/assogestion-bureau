from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from loguru import logger

from IHM import ligne_facture
from utils.message import pop_up


class DetailLigneFactAPP(QtWidgets.QMainWindow, ligne_facture.Ui_ligne_facture):
    finished = pyqtSignal(bool)

    def __init__(self, Session, fac, ligne_fac, edit, parent=None):
        super(DetailLigneFactAPP, self).__init__(parent)
        try:
            self.Session = Session
            self.fac = fac
            self.ligne_fac = ligne_fac
            self.edit = edit
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.button_ok.setIcon(QIcon("save.png"))
            #self.spin_qty.valueChanged.connect(self.calculer_total_ht)
            #self.spin_pu.valueChanged.connect(self.calculer_total_ht)
            #self.button_ok.clicked.connect(self.save_ligne_facture)
            self.init_app()
            self.show()
        except Exception as err:
            logger.error(err)

    def init_app(self):
        if self.ligne_fac:
            self.code_edit.setText(self.ligne_fac.code)
            self.desc_edit.setText(self.ligne_fac.desc)
            self.spin_qty.setValue(self.ligne_fac.qty)
            self.spin_pu.setValue(self.ligne_fac.pu_ht)
            self.spin_total.setValue(self.ligne_fac.total_ht)

    def calculer_total_ht(self):
        qty = float(self.spin_qty.value())
        pu_ht = float(self.spin_pu.value())
        total_ht = qty * pu_ht
        self.spin_total.setValue(total_ht)

    def closeEvent(self, event):
        self.finished.emit(True)
        event.accept()

    def error_facture(self, message, texte):
        pop_up(
            self,
            "AssoGestion - AMSE - Ligne facture",
            message,
            texte,
            "ERROR"
        )
