import os

TRACE = False
TRACE_MAPPING = True
SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
SQLALCHEMY_ENGINE_ECHO = False
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://tutorlinkadmin:tutorlinkadminpass@localhost:5432/tutorlink"
