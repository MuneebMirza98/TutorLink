# initialisation des tests effectués par 'pytest' dans ce répertoire (et
# ses sous-répertoires)

import os
import pytest
import warnings
import subprocess
from werkzeug.datastructures import FileStorage
import json

from sys import platform

SQLALCHEMY_DATABASE_URI_TEST = "postgresql+psycopg2://tutorlinkadmin:tutorlinkadminpass@localhost:5432/tutorlinktest"


def execute_sql_file_with_psql(url, filename):
    """Exécute un script SQL via psql en utilisant l'URL fourni pour se connecter"""
    psql_url = url.replace("+psycopg2", "")
    # warnings.warn(psql_url)
    # warnings.warn(filename)
    if platform == "win32":
        psql_path = 'psql'
    else:
        psql_path = '/usr/bin/psql'
    res = subprocess.run(
        [psql_path, '-f', filename, psql_url],
        capture_output=True,
        encoding="utf-8",
        timeout=3,
    )
    if res.stdout != '':
        warnings.warn(f"\nSTDOUT: {res.stdout}")
    if res.stderr != '':
        warnings.warn(f"\nSTDERR: {res.stderr}")
    assert res.returncode == 0


@pytest.fixture(autouse=True, scope="session")
def init_test_db():
    """(ré)Initialisation de la structure et des données de la base de test"""
    execute_sql_file_with_psql(SQLALCHEMY_DATABASE_URI_TEST, "sql/schema.sql")
    execute_sql_file_with_psql(SQLALCHEMY_DATABASE_URI_TEST, "sql/populate.sql")
    return True


@pytest.fixture
def test_app():
    """L'application Flask de test de tutorlink"""
    os.environ["TUTORLINK_CONFIG"] = "testing"
    from tutorlink import create_app
    test_app = create_app({
        'TESTING': True,
        # "SQLALCHEMY_DATABASE_URI": SQLALCHEMY_DATABASE_URI_TEST,
        # "TRACE": True,
        # "TRACE_MAPPING": True,
    })
    yield test_app


@pytest.fixture
def web_client(test_app):
    """Un client Web pour simuler des requêtes provenant d'un navigateur"""
    with test_app.test_client() as web_client:
        yield web_client


@pytest.fixture
def db_objects(test_app):
    """Tous les objets pour l'accès à la base de données"""

    from tutorlink.db import db_session, User, Session, Module, Ue, Role, Favorite, ManagedBy, LecturedBy, SessionType
    
    db_objects = {'db_session': db_session,
                  'User': User,
                  'Session': Session,
                  'Module': Module,
                  'Ue': Ue,
                  'Role': Role,
                  'Favorite': Favorite,
                  'ManagedBy': ManagedBy,
                  'LecturedBy': LecturedBy,
                  'SessionType': SessionType}
    return db_objects


@pytest.fixture
def populate_file():
    """Fichier JSON de population de la base de test"""
    # On simule l'envoi d'un fichier JSON
    json_file = FileStorage(
        stream=open("tests/populate.json", "rb"),
        filename="populate.json",
        content_type="application/json",
    )
    return json_file


@pytest.fixture
def populate_dict():
    """Dictionnaire Python de population de la base de test"""
    with open('tests/populate.json', 'rb') as f:
        data = json.load(f)
    return data
