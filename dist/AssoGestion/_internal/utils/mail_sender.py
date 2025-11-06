import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger


def mail_sender(toadress, msg):
    try:

        if toadress not in ("", None):
            mailserver = smtplib.SMTP(host='smtp.gmail.com', port=587)
            mailserver.ehlo()
            mailserver.starttls()
            mailserver.ehlo()
            mailserver.login('secretariatamse27@gmail.com', 'zpjndvigjubnyrde')
            mailserver.sendmail('secretariatamse27@gmail.com', toadress, msg.as_string())
            mailserver.close()
        else:
            return -2, "Pas d'email destinataire"
        return 0, ""
    except Exception as err:
        logger.error(err)
        return -1, str(err)

def reset_password(to):
    try:
        send_info_to_user(to)
        send_password_lost_report(to)
        return 0
    except Exception as err:
        logger.error(err)
        return -1


def send_info_to_user(to):
    msg = MIMEMultipart()
    msg['From'] = 'secretariatamse27@gmail.com'
    msg['Subject'] = f"Envoi d'identifiant pour Asso'Gestion"
    msg['To'] = to
    toadress = to
    message = f"""Bonjour,
        Vous avez récemment effectué une réinitalisation de mot de passe pour votre compte Asso'Gestion.

        Votre administrateur va prendre contact avec vous afin de vous donner un nouveau mot de passe

        Cordialement,

        AssoGestion
        """
    msg.attach(MIMEText(message))
    mail_sender(toadress, msg)


def send_password_lost_report(user):
    msg = MIMEMultipart()
    msg['From'] = 'secretariatamse27@gmail.com'
    msg['Subject'] = f"Mot de passe oublié pour l'application Asso'Gestion"
    msg['To'] = "amaury.robert.boucher@gmail.com"
    toadress = "amaury.robert.boucher@gmail.com"
    message = f"""Bonjour,
        L'utilisateur {user} a envoyé une demande de réinitialisation de mot de passe
        
        Cordialement,

        L'administrateur AssoGestion
        """
    msg.attach(MIMEText(message))
    mail_sender(toadress, msg)


def send_error_report(user, error_code, error_msg):
    msg = MIMEMultipart()
    msg['From'] = 'secretariatamse27@gmail.com'
    msg['Subject'] = f"Erreur de lancement de l'application Asso'Gestion"
    msg['To'] = "amaury.robert.boucher@gmail.com"
    toadress = "amaury.robert.boucher@gmail.com"
    message = f"""Bonjour,
L'utilisateur {user} a rencontré une erreur lors du lancement de l'application:
code: {error_code}
message: {error_msg}
    """
    msg.attach(MIMEText(message))
    mail_sender(toadress, msg)

def send_import_report_adh(user, liste_error):
    msg = MIMEMultipart()
    msg['From'] = 'secretariatamse27@gmail.com'
    msg['Subject'] = f"Asso'Gestion - rapport d'intégration des adhérents"
    msg['To'] = "amaury.robert.boucher@gmail.com"
    toadress = "amaury.robert.boucher@gmail.com"
    message = f"""Bonjour,
    
    Voici le rapport d'intégration du fichier adhérents pour l'utilisateur {user}:
    
    """
    for l in liste_error:
        message += l
    msg.attach(MIMEText(message))
    mail_sender(toadress, msg)


def send_recu_fiscal(adh, nom_pdf, pj, annee):
    msg = MIMEMultipart()
    msg['From'] = 'secretariatamse27@gmail.com'
    msg['Subject'] = f"Reçu fiscal pour l'année {annee}"
    msg['To'] = adh.email_adherent
    msg['Cci'] = "amaury.robert.boucher@gmail.com"
    toadress = adh.email_adherent
    message = f"""Bonjour {adh.titre_adherent} {adh.prenom_adherent} {adh.nom_adherent},
Veuillez trouver ci-joint votre reçu des versements effectués en {annee} pour l'AMSE au titre de cotisation et dons.
Cordialement,
Le secrétariat de l'AMSE
    """
    msg.attach(MIMEText(message))
    with open(pj, "rb") as piece:  # Ouverture du fichier
        part = MIMEBase('application', 'octet-stream')  # Encodage de la pièce jointe en Base64
        part.set_payload(piece.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "piece; filename= %s" % nom_pdf)
        msg.attach(part)  # Attache de la pièce jointe à l'objet "message"
    res, err = mail_sender(toadress, msg)
    if res == -1:
        return -1, err
    elif res == -2:
        return -2, err
    else:
        return 0, err
