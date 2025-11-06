# coding=utf-8
from datetime import datetime, timezone

import dropbox
from PyQt5.QtCore import QThread, pyqtSignal
from loguru import logger

date_in = datetime.now(timezone.utc)
date_out = datetime.strftime(date_in, '%Y%m%d%H%M%S')


class TraiterFichier(QThread):
    def __init__(self, version, parent=None):
        QThread.__init__(self, parent)
        self.version = version
    erreur = pyqtSignal(str)
    countchanged = pyqtSignal(int)
    stepchanged = pyqtSignal(str)
    flagfin = pyqtSignal(tuple)

    def run(self):
        updater_name = None
        self.stepchanged.emit(f"Recherche de l'installateur d'Asso'Gestion v{self.version}")
        self.countchanged.emit(50)
        dbx = dropbox.Dropbox('sl.BoYxl0TK2BdjJGJKs6pNYHmmvVPwyA82B7tAgByzGeidmmqfOnwKHaUui26TEbd-XX3XtAANQ-xT7KJPoZRC1IpZCJU1JEfp9BthLsxmMTPaz8iUyA1P1Qex9fk3Lul60DLVc9Mu1JZvXtVZDowdBEE')
        try:
            for entry in dbx.files_list_folder('').entries:
                self.stepchanged.emit(f"Récupération du fichier {entry.name}")
                updater_name = entry.name
                with open(f"C:\\Users\\aboucher\\Desktop\\{entry.name}", "wb") as f:
                    metadata, res = dbx.files_download(path=f"/{entry.name}")
                    f.write(res.content)
                self.countchanged.emit(100)
        except Exception as err:
            logger.error(err)
        try:
            self.flagfin.emit((True,f"C:\\Users\\aboucher\\Desktop\\{updater_name}"))
        except Exception as err:
            logger.error(err)