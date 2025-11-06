from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QTableWidgetItem
from loguru import logger

from IHM import pop_up


class PopupApp(QtWidgets.QMainWindow, pop_up.Ui_pop_up):

    def __init__(self, message, texte, level, errors, parent=None):
        super(PopupApp, self).__init__(parent)
        self.application = None
        self.setupUi(self)
        self.message = message
        self.texte = texte
        self.level = level
        self.errors = errors
        dic_level_icone = {
            "INFO": "info.png",
            "WARNING": "warning.png",
            "ERROR": 'croix.png'
        }
        logger.debug(self.level)
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap("logo_abo_tech.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(self.icon)
        pixmap = QPixmap(dic_level_icone.get(self.level))
        self.label_icone.setPixmap(pixmap)
        self.button_ok.clicked.connect(self.ok_clicked)
        self.label_texte.setText(self.message)
        self.label_texte_info.setText(self.texte)
        self.set_tab_error()
        self.show()

    def set_tab_error(self):
        for i, e in enumerate(self.errors):
            logger.debug(f"{i} {e}")
            self.tab_error.insertRow(i)
            self.tab_error.setItem(i, 0, QTableWidgetItem(f'{e}'))

        self.tab_error.resizeColumnsToContents()
    def ok_clicked(self):
        self.close()
