from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from PyQt5.QtCore import QThread, pyqtSignal
from loguru import logger

from utils.mail_sender import mail_sender


class TraiterEmail(QThread):
    def __init__(self, liste_dest, liste_pj, sujet, msg, parent=None):
        try:
            QThread.__init__(self, parent)
            self.liste_dest = liste_dest
            self.liste_pj = liste_pj
            self.sujet = sujet
            self.message = msg
        except Exception as err:
            logger.error(err)

    line_count_changed = pyqtSignal(int)
    line_count_max = pyqtSignal(int)
    flag_fin = pyqtSignal(bool)

    def run(self):
        try:
            logger.info("Lancement traitement")
            self.line_count_max.emit(len(self.liste_dest))
            for i, d in enumerate(self.liste_dest):
                if len(self.liste_pj) > 0:
                    self.send_message_with_attachment(d, self.sujet, self.message, self.liste_pj)
                else:
                    self.send_message_no_attachment(d, self.sujet, self.message)
                self.line_count_changed.emit(i + 1)
        except Exception as err:
            logger.error(err)
        finally:
            logger.debug("test")
            self.flag_fin.emit(True)

    def send_message_with_attachment(self, dest, sujet, message, liste_pj):
        try:
            msg = MIMEMultipart()
            msg['From'] = 'secretariatamse27@gmail.com'
            msg['Subject'] = sujet
            msg['To'] = dest
            toadress = dest
            logger.info(toadress)
            message = message
            msg.attach(MIMEText(message))
            for i, pj in enumerate(liste_pj):
                nom_pj = pj[0]
                pj_send = pj[1]
                logger.info(pj_send)
                with open(pj_send, "rb") as piece:  # Ouverture du fichier
                    logger.info("Ouverture du fichier")
                    logger.info("Encodage de la pièce jointe en Base64")
                    part = MIMEBase('application', 'octet-stream')  # Encodage de la pièce jointe en Base64
                    part.set_payload(piece.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', "piece; filename= %s" % nom_pj)
                    msg.attach(part)  # Attache de la pièce jointe à l'objet "message"
                    logger.info("Attache de la pièce jointe à l'objet message")
            mail_sender(toadress, msg)
            return 0
        except Exception as err:
            logger.error(err)
            return 1

    def send_message_no_attachment(self, dest, sujet, message):
        try:
            msg = MIMEMultipart()
            msg['From'] = 'secretariatamse27@gmail.com'
            msg['Subject'] = sujet
            message = message
            msg.attach(MIMEText(message))
            logger.info(f"Envoi du mail à {dest}")
            toadress = dest
            mail_sender(toadress, msg)
            return 0
        except Exception as err:
            logger.error(err)
            return 1