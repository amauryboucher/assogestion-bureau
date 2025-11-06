import re

from loguru import logger


def user_password_control(passwd):
    SpecialSym = ['$', '@', '#', '%', "!"]
    ret = []
    val = True
    if len(passwd) < 6:
        logger.error('Le mot de passe doit avoir au moins 6 caractères')
        val = "CTRL_USER_003"
        ret.append(val)

    # Check if password contains at least one digit, uppercase letter, lowercase letter, and special symbol
    has_digit = False
    has_upper = False
    has_lower = False
    has_sym = False
    for char in passwd:
        if 48 <= ord(char) <= 57:
            has_digit = True
        elif 65 <= ord(char) <= 90:
            has_upper = True
        elif 97 <= ord(char) <= 122:
            has_lower = True
        elif char in SpecialSym:
            has_sym = True

    if not has_digit:
        logger.error('Le mot de passe doit contenir au moins un nombre')
        val = "CTRL_USER_005"
        ret.append(val)
    if not has_upper:
        logger.error('Le mot de passe doit contenir au moins une majuscule')
        val = "CTRL_USER_006"
        ret.append(val)
    if not has_lower:
        logger.error('Le mot de passe doit contenir au moins une minuscule')
        val = "CTRL_USER_007"
        ret.append(val)
    if not has_sym:
        logger.error('Le mot de passe doit avoir au moins un caractère spécial parmis les suivants: $@#!')
        val = "CTRL_USER_008"
        ret.append(val)

    return ret

def user_email_control(email):
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.match(pat, email):
        return ""
    else:
        return "CTRL_USER_001"

def user_username_control(username):
    if username:
        return ""
    else:
        return "CTRL_USER_002"

def user_actif_control(actif):
    if actif:
        return ""
    else:
        return "CTRL_USER_004"

def user_database_control(user, password):
    if user:
        for u in user:
            if u.actif:
                if u.password == password:
                    logger.info("Redirection vers la page d'accueil")
                else:
                    return "CTRL_USER_004"
            else:
                return "CTRL_USER_003"
    else:
        return "CTRL_USER_002"


