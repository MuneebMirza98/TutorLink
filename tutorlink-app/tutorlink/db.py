import click
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.automap import name_for_collection_relationship
from sqlalchemy.ext.automap import name_for_scalar_relationship
from flask.cli import with_appcontext
from flask_sqlalchemy_session import flask_scoped_session

# from sqlalchemy.orm import scoped_session

# Les éléments suivants seront définis lorsque l'automap aura fait son
# travail...
db_session = None

User = None
Session = None
Module = None
Ue = None
Role = None
Favorite = None
ManagedBy = None
LecturedBy = None
SessionType = None


def connect_db(app):
    '''Connextion à la base de données via l'automap'''
    # click.echo("db.connect_db")
    if app.config['TRACE_MAPPING']:
        click.echo("DB mapping...")


    # ORM: correpondances nom de table => nom de classe
    model_map = {
        'user': 'User',
        'session': 'Session',
        'module': 'Module',
        'ue': 'Ue',
        'role': 'Role',
        'favorite': 'Favorite',
        'managed_by': 'ManagedBy',
        'lectured_by': 'LecturedBy',
        'session_type': 'SessionType',
    }


    relation_map = {
        'User=>Role(user_role_id_fkey)': 'role',
        'Role=>User(user_role_id_fkey)': 'all_users',

        'Session=>Module(session_module_id_fkey)': 'module',
        'Module=>Session(session_module_id_fkey)': 'all_sessions',

        'Session=>Ue(session_ue_id_fkey)': 'ue',
        'Ue=>Session(session_ue_id_fkey)': 'all_sessions',

        'Session=>SessionType(session_type_fkey)': 'session_type',
        'SessionType=>Session(session_type_fkey)': 'all_sessions',

        'Favorite=>Module(favorite_module_id_fkey)': 'module',
        'Module=>Favorite(favorite_module_id_fkey)': 'favorite_collection',

        'ManagedBy=>Module(managed_by_module_id_fkey)': 'module',
        'Module=>ManagedBy(managed_by_module_id_fkey)': 'managedby_collection',
        'ManagedBy=>User(managed_by_user_username_fkey)': 'user',
        'User=>ManagedBy(managed_by_user_username_fkey)': 'managedby_collection',

        'LecturedBy=>Session(lectured_by_session_id_fkey)': 'session',
        'Session=>LecturedBy(lectured_by_session_id_fkey)': 'lecturedby_collection',
        'LecturedBy=>User(lectured_by_user_username_fkey)': 'user',
        'User=>LecturedBy(lectured_by_user_username_fkey)': 'lecturedby_collection',

        'Module=>User(favorite_module_id_fkey)': 'favorited_by_users',
        'User=>Module(favorite_user_username_fkey)': 'favorite_modules',

        'Module=>User(managed_by_module_id_fkey)': 'managed_by_users',
        'User=>Module(managed_by_user_username_fkey)': 'managed_modules',

        'Session=>User(lectured_by_session_id_fkey)': 'lectured_by_users',
        'User=>Session(lectured_by_user_username_fkey)': 'lectured_sessions',
    }

    url_de_connexion = app.config['SQLALCHEMY_DATABASE_URI']
    sqlalchemy_engine_echo = app.config['SQLALCHEMY_ENGINE_ECHO']

    if app.config['TRACE_MAPPING']:
        click.echo("URL de connexion:" + url_de_connexion)

    engine = create_engine(
        url_de_connexion,
        # si True, pratique pour déboguer (mais très verbeux)
        echo=sqlalchemy_engine_echo,
        # pour disposer des fonctionnalités de la version 2.0
        future=True,
    )
    our_metadata = MetaData()
    our_metadata.reflect(engine, only=model_map.keys())
    # print("our_metadata: ok")
    Base = automap_base(metadata=our_metadata)


    class User(Base):
        __tablename__ = 'user'

        lectured_sessions = relationship('Session', secondary='lectured_by', back_populates='lectured_by_users', viewonly=True)

        def __str__(self):
            return f"User({self.username})"


    class Session(Base):
        __tablename__ = 'session'

        lectured_by_users = relationship("User", secondary='lectured_by', back_populates='lectured_sessions', viewonly=True)

        @property
        def duration(self):
            return self.date_end - self.date_start

        def __str__(self):
            return f"Session({self.id}, {self.date_start.strftime('%Y-%m-%d %H:%M')}, {self.module_id}, {self.salle})"


    class Favorite(Base):
        __tablename__ = 'favorite'

        def __str__(self):
            return f"Favorite({self.email}, {self.module_id})"


    class ManagedBy(Base):
        __tablename__ = 'managed_by'

        def __str__(self):
            return f"ManagedBy({self.email}, {self.module_id})"


    class Module(Base):
        __tablename__ = 'module'

        def __str__(self):
            return f"Module({self.id}, {self.name})"
    
    class Ue(Base):
        __tablename__ = 'ue'

        def __str__(self):
            return f"Ue({self.id}, {self.name})"


    class LecturedBy(Base):
        __tablename__ = 'lectured_by'

        def __str__(self):
            return f"LecturedBy({self.email}, {self.module_id})"


    class SessionType(Base):
        __tablename__ = 'session_type'

        def __str__(self):
            return f"SessionType({self.id}, {self.name})"


    class Role(Base):
        __tablename__ = 'role'

        def __str__(self):
            return f"Role({self.id}, {self.name})"


    def map_names(type, orig_func):
        """fonction d'aide à la mise en correspondance"""

        def _map_names(base, local_cls, referred_cls, constraint):
            auto_name = orig_func(base, local_cls, referred_cls, constraint)
            # la clé de l'association
            key = f"{local_cls.__name__}=>{referred_cls.__name__}({constraint.name})"
            # quelle correpondance ?
            if key in relation_map:
                # Yes, return it
                name = relation_map[key]
            else:
                name = auto_name
            if app.config['TRACE_MAPPING']:
                # affiche la relation créée (pour comprendre ce qui se passe)
                click.echo(f" {type:>10s}: {key} {auto_name} => {name}")
            return name

        return _map_names

    Base.prepare(
        name_for_scalar_relationship=map_names('scalar',
                                               name_for_scalar_relationship),
        name_for_collection_relationship=map_names('collection',
                                                   name_for_collection_relationship),
    )

    # On rend les tables du modèle globales à ce module
    for cls in [User, Session, Module, Ue, Role, Favorite, ManagedBy, LecturedBy, SessionType]:
        cls.__table__.info = dict(bind_key='main')
        globals()[cls.__name__] = cls

    Session = sessionmaker(
        bind=engine,
        future=True,
        class_=sqlalchemy.orm.Session
    )
    globals()['db_session'] = flask_scoped_session(Session, app)

    if app.config['TRACE_MAPPING']:
        click.echo("DB mapping done.")

@click.command("check-db")
@with_appcontext
def check_db_command():
    """Vérifie que le mapping vers la base de données fonctionne bien."""
    assert db_session is not None

    print(type(db_session))

    # on fait quelques requêtes SQL
    ordre = select(User)
    all_users = db_session.execute(ordre).scalars().all()
    for user in all_users:
        assert isinstance(user, User)


def init_app(app):
    """Initialisation du lien avec la base de données"""

    if app.config['TRACE']:
        click.echo(
            f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}"
        )

    connect_db(app)

    app.cli.add_command(check_db_command)
