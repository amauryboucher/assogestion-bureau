from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from loguru import logger

from IHM import ligne_devis
from utils.models import assogestion_ligne_devis


class DetailLigneDevAPP(QtWidgets.QMainWindow, ligne_devis.Ui_ligne_devis):
    finished = pyqtSignal(bool)

    def __init__(self, Session, edit, dev, ligne_dev, edit_dev, parent=None):
        super(DetailLigneDevAPP, self).__init__(parent)
        try:
            self.s = Session
            self.edit = edit
            self.edit_dev = edit_dev
            self.dev = dev
            self.ligne_dev = ligne_dev
            self.setupUi(self)
            self.icon = QtGui.QIcon()
            self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.setWindowIcon(self.icon)
            self.button_ok.setIcon(QIcon("save.png"))
            self.spin_qty.valueChanged.connect(self.calculer_total_ht)
            self.spin_pu.valueChanged.connect(self.calculer_total_ht)
            self.button_ok.clicked.connect(self.save_ligne_devis)
            self.init_app()
            self.show()
        except Exception as err:
            logger.error(err)

    def init_app(self):
        if self.ligne_dev:
            self.code_edit.setText(self.ligne_dev.code)
            self.desc_edit.setText(self.ligne_dev.desc)
            self.spin_qty.setValue(self.ligne_dev.qty)
            self.spin_pu.setValue(self.ligne_dev.pu_ht)
            self.spin_total.setValue(self.ligne_dev.total_ht)

    def calculer_total_ht(self):
        qty = float(self.spin_qty.value())
        pu_ht = float(self.spin_pu.value())
        total_ht = qty * pu_ht
        self.spin_total.setValue(total_ht)

    def save_ligne_devis(self):
        try:
            if self.edit_dev:
                if self.edit:
                    ligne = self.s.query(assogestion_ligne_devis).filter_by(id=self.ligne_dev.id).first()
                    ligne.id_devis = self.dev.id,
                    ligne.code = self.code_edit.text(),
                    ligne.desc = self.desc_edit.toPlainText(),
                    ligne.qty = self.spin_qty.value(),
                    ligne.pu_ht = self.spin_pu.value(),
                    ligne.total_ht = self.spin_total.value()
                else:
                    new_ligne = assogestion_ligne_devis(
                        id_devis=self.dev.id,
                        code=self.code_edit.text(),
                        desc=self.desc_edit.toPlainText(),
                        qty=self.spin_qty.value(),
                        pu_ht=self.spin_pu.value(),
                        total_ht=self.spin_total.value()
                    )
                    self.s.add(new_ligne)
                self.s.commit()
            else:
                if self.edit:
                    ligne = self.s.query(assogestion_temp_ligne_devis).filter_by(id=self.ligne_dev.id).first()
                    ligne.id_devis = self.dev.id,
                    ligne.code = self.code_edit.text(),
                    ligne.desc = self.desc_edit.toPlainText(),
                    ligne.qty = self.spin_qty.value(),
                    ligne.pu_ht = self.spin_pu.value(),
                    ligne.total_ht = self.spin_total.value()
                else:
                    new_ligne = assogestion_temp_ligne_devis(
                        id_devis=self.dev.id,
                        code=self.code_edit.text(),
                        desc=self.desc_edit.toPlainText(),
                        qty=self.spin_qty.value(),
                        pu_ht=self.spin_pu.value(),
                        total_ht=self.spin_total.value()
                    )
                    self.s.add(new_ligne)
                self.s.commit()
        except Exception as err:
            logger.error(err)
        finally:
            self.close()

    def closeEvent(self, event):
        self.finished.emit(True)
        event.accept()
