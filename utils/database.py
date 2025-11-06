from configparser import ConfigParser, NoSectionError
from pathlib import Path
from typing import Optional, Tuple

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.models import Base


def database_connexion(mode: str, config_path: Optional[Path]=None):
    """
        Initialise la connexion à la base de données selon le mode choisi.

        :param mode: "prod" ou "local"
        :param config_path: chemin absolu du fichier INI à utiliser
        :return: (code, error, session_class)
                 - code = 0 si succès
                 - code = -1 si échec
                 - session_class = sessionmaker SQLAlchemy
        """
    if mode == "prod":
        res, error, DATABASE_URL = get_database_config(config_path)
        if res == 0:
            try:
                session = set_database(DATABASE_URL, mode)
                return 0, None, session
            except Exception as err:
                return -1, err, None
        else:
            return -1, error, None
    else:
        DATABASE_URL = 'postgresql+psycopg2://admin:solist2013@localhost:5432/AssoGestionAmse'
        try:
            session = set_database(DATABASE_URL, mode)
            return 0, None, session
        except Exception as err:
            logger.error(err)
            return -1, err, None


def set_database(DATABASE_URL, mode):
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    logger.info(f"Connexion réussie à la base de donnée {mode} AssoGestionAmse")
    return Session


def get_database_config(filename: Optional[Path] = None,
                        section: str = "AssoGestion") -> Tuple[int, Optional[Exception], Optional[str]]:
    """
    Lit les paramètres de connexion PostgreSQL dans le fichier INI.

    :param filename: chemin absolu du fichier .ini à utiliser
    :param section: section à lire (par défaut 'AssoGestion')
    :return: tuple (code, error, DATABASE_URL)
    """
    if filename is None:
        filename = Path("config_assogestion.ini")
    filename = Path(filename)
    if not filename.exists():
        logger.error(f"⚠️ Fichier de configuration introuvable : {filename}")
        return -1, FileNotFoundError(f"{filename} non trouvé"), None
    parser = ConfigParser()
    try:
        with open(filename, encoding='utf-8') as f:
            parser.read_file(f)
            try:
                params = dict(parser.items(section))
            except NoSectionError as err:
                logger.error(f"Section [{section}] introuvable dans {filename}")
                return -1, err, None
        host = params.get("host")
        database = params.get("database")
        user = params.get("user")
        password = params.get("password")
        port = params.get("port")
        if not all([host, database, user, password, port]):
            logger.error(f"Paramètres de connexion incomplets dans {filename}")
            return -1, ValueError("Paramètres manquants"), None

        db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        logger.info(f"Connecting to database {database} at {host}:{port}")
        return 0, None, db_url
    except Exception as err:
        logger.exception(f"Erreur lors de la lecture de {filename}")
        return -1, err, None



def get_version_config(filename: Optional[Path] = None,
                       section: str = "A_PROPOS") -> Tuple[int, Optional[Exception], Optional[str]]:
    """
    Lit la version du programme définie dans le fichier INI.

    :param filename: chemin absolu du fichier .ini
    :param section: section contenant 'version'
    :return: tuple (code, error, version_str)
    """
    if filename is None:
        filename = Path("config_assogestion.ini")

    filename = Path(filename)
    if not filename.exists():
        logger.error(f"⚠️ Fichier de configuration introuvable : {filename}")
        return -1, FileNotFoundError(f"{filename} non trouvé"), None

    parser = ConfigParser()
    try:
        with open(filename, encoding="utf-8") as f:
            parser.read_file(f)
        try:
            params = dict(parser.items(section))
            version = params.get("version")
            logger.info(f"Version lue dans {filename} : {version}")
            return 0, None, version
        except NoSectionError as err:
            logger.error(f"Section [{section}] introuvable dans {filename}")
            return -1, err, None
    except Exception as err:
        logger.exception(f"Erreur lors de la lecture de {filename}")
        return -1, err, None