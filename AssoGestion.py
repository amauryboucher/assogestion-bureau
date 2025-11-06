import configparser
import os
import sys
from configparser import ConfigParser
from pathlib import Path

from PyQt5.QtCore import QStandardPaths, QSharedMemory, QCoreApplication, Qt
from PyQt5.QtWidgets import QApplication
from loguru import logger

from utils.ConnexionAPP import ConnexionApp

APP_NAME = "AssoGestion"
ORG_NAME = "ABOTECH"
INI_NAME = "config_assogestion.ini"
LOG_NAME = "assogestion.log"

def is_frozen() -> bool:
    """Retourne True si l'application est packagée via PyInstaller"""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def resource_dir() -> Path:
    """Répertoire des ressources (icônes, .ui, etc.)"""
    if is_frozen():
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent


def get_installation_dir() -> str:
    """Chemin du répertoire d'installation réel"""
    if is_frozen():
        return str(Path(sys.executable).resolve().parent)
    return str(Path(__file__).resolve().parent)

def app_data_dir() -> Path:
    base = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    if not base:
        base = str(Path.home() / ".config" / APP_NAME)
    p = Path(base)
    p.mkdir(parents=True, exist_ok=True)
    return p

def write_local_ini(filename=INI_NAME, section="PARAM") -> Path:
    """Utilise le fichier INI existant s'il est présent, sinon le crée."""
    cfg_path = Path(filename)

    # 1️⃣ Si le fichier existe déjà : on le conserve tel quel
    if cfg_path.exists():
        logger.info(f"Fichier de configuration existant trouvé : {cfg_path}")
        config = configparser.ConfigParser()
        config.read(cfg_path, encoding="utf-8")

        # On vérifie juste la section PARAM pour mise à jour éventuelle
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, "installation_dir", get_installation_dir())

        with cfg_path.open("w", encoding="utf-8") as f:
            config.write(f)
        return cfg_path

    # 2️⃣ Sinon, on le crée depuis zéro (cas première installation)
    logger.warning(f"Aucun fichier de configuration trouvé. Création de {cfg_path}")
    config = configparser.ConfigParser()
    config.add_section(section)
    config.set(section, "installation_dir", get_installation_dir())
    with cfg_path.open("w", encoding="utf-8") as f:
        config.write(f)
    return cfg_path

def already_running(key="AssoGestion_SingleInstance") -> bool:
    """Empêche le double lancement"""
    mem = QSharedMemory(key)
    if not mem.create(1):
        logger.warning("Une instance d’AssoGestion est déjà en cours d’exécution.")
        return True
    return False


# ========= MAIN ========= #

def setup_logger():
    """Configure loguru (console + fichier rotatif)"""
    base_dir = app_data_dir()
    log_file = base_dir / LOG_NAME

    # Supprime les handlers précédents
    logger.remove()

    # Console (colorée)
    logger.add(sys.stderr, level="DEBUG", colorize=True,
               format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

    # Fichier rotatif
    logger.add(log_file, level="DEBUG", rotation="500 KB", retention=3,
               encoding="utf-8", enqueue=True, backtrace=True, diagnose=True)

    logger.info(f"Logs enregistrés dans {log_file}")
    return logger


def excepthook(exc_type, exc_value, traceback):
    """Capture globale des exceptions non gérées"""
    logger.opt(exception=(exc_type, exc_value, traceback)).error("Exception non gérée")
    sys.exit(1)

def set_local_dir(filename="config_assogestion.ini", section="PARAM"):
    config = ConfigParser()
    config.read(filename)
    try:
        config.add_section(section)
    except configparser.DuplicateSectionError as err:
        pass
    finally:
        config.set(section, "installation_dir", os.getcwd())
        with open(filename, "w") as config_file:
            config.write(config_file)
            print("Mise à jour du fichier ini")
    return os.getcwd()

if __name__ == "__main__":
    # Configuration Qt
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setOrganizationName(ORG_NAME)
    QCoreApplication.setApplicationName(APP_NAME)

    # Logger
    setup_logger()
    sys.excepthook = excepthook

    if already_running():
        sys.exit(0)
    # App Qt
    app = QApplication(sys.argv)
    app.setApplicationDisplayName(APP_NAME)
    try:
        write_local_ini()
    except Exception as e:
        logger.exception(f"Erreur lors de l’écriture du fichier INI: {e}")
    logger.info("Lancement de l’application...")
    accueil = ConnexionApp()
    sys.exit(app.exec_())
