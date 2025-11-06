from configparser import ConfigParser, NoSectionError

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.models import Base


def database_connexion(mode):
    # TODO enlever les élements de connexion à la BDD en dur dans le code
    if mode == "prod":
        res, error, DATABASE_URL = get_database_config()
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


def get_database_config(filename="config_assogestion.ini", section="AssoGestion"):
    """Connect to the PostgreSQL database server"""
    # read connection parameters
    parser = ConfigParser()
    # read config file
    try:
        with open(filename, 'r') as f:
            parser.read_file(f)
            db = {}
            try:
                params = parser.items(section)
                for param in params:
                    db[param[0]] = param[1]
                host = db.get('host')
                database = db.get('database')
                user = db.get('user')
                password = db.get('password')
                port = db.get('port')
                logger.info(f"Connecting to the database ... {host}:{port}/{database}")
                DATABASE = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
                return 0, None, DATABASE
            except NoSectionError as err:
                return -1, err, None
    except FileNotFoundError as err:
        return -1, err, None


def get_version_config(filename="config_assogestion.ini", section="A_PROPOS"):
    """Connect to the PostgreSQL database server"""
    # read connection parameters
    parser = ConfigParser()
    # read config file
    try:
        with open(filename, 'r') as f:
            parser.read_file(f)
            db = {}
            try:
                params = parser.items(section)
                for param in params:
                    db[param[0]] = param[1]
                version = db.get('version')
                return 0, None, version
            except NoSectionError as err:
                return -1, err, None
    except FileNotFoundError as err:
        return -1, err, None