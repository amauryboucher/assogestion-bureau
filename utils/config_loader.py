import sys
from pathlib import Path
from loguru import logger

def app_data_dir() -> Path:
    """Renvoie le dossier AppData/AssoGestion s’il existe."""
    from PyQt5.QtCore import QStandardPaths
    base = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    if not base:
        base = str(Path.home() / ".config" / "AssoGestion")
    p = Path(base)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_config_path() -> Path:
    """Retourne le chemin du fichier INI (local ou AppData)."""
    local = Path(__file__).resolve().parent.parent / "config_assogestion.ini"
    if local.exists():
        return local
    alt = app_data_dir() / "config_assogestion.ini"
    if alt.exists():
        return alt
    logger.warning("⚠️ Aucun fichier config_assogestion.ini trouvé, utilisation du chemin local par défaut.")
    return local

def resource_dir() -> Path:
    """Retourne le dossier des ressources compatible PyInstaller."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent