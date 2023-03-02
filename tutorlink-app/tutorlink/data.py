import pandas as pd
import re

from flask import Blueprint
from flask import flash
from flask import g
from flask import render_template
from flask import request
from flask import abort

from tutorlink.db import db_session, User, Role, Session, SessionType, Module, Ue, LecturedBy
from sqlalchemy import select
from tutorlink.auth import login_required

bp = Blueprint("data", __name__, url_prefix="/data")


@bp.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """
    Update the database with data from a JSON file.

    The JSON file must have the following structure:
    [{
		"id" : 123,
		"ue" : "UE name",
		"intitule_ue" : "UE label",
		"module" : "Module name",
		"intitule_module" : "Module label",
		"intervenants" : [{"NOM1 Prénom1":"username1"}, {"NOM2 Prénom2":"username2"}],
		"groupes" : "Groupe 1, Groupe 2",
		"type_synapses" : "TYPE1",
		"libelle" : "Nom du type 1",
		"date" : "2022-06-10",
		"salles" : ["Salles 1", "Salle 2"],
		"heuredeb" : "08:00:00",
		"heurefin" : "09:30:00",
	}]

    If the user is not an admin, abort with a 403 error.
    """
    if g.user.admin == False:
        abort(403)
    if request.method == "POST":
        file = request.files.get("file", None)
        if file is not None:
            sessions, session_types, modules, ue, users = read_json(file)
            try:
                result = populate_db(sessions, session_types, modules, ue, users)
            except Exception as e:
                flash(str(e), 'error')
            else:
                msg = f"Data updated: {', '.join(result)}"
                flash(msg, 'success')
        else:
            flash("No file selected", 'warning')
    
    return render_template("data_update.html")

def parse_users(row: pd.Series) -> pd.Series:
    """
    Parse the users from a row of the JSON file.
    If the row is None, return None for all fields.
    If the firstname or surname cannot be parsed,
        return None for the surname and the unparsed name for the surname.

    Parameters:
        row (pd.Series): A row of one user from the JSON file. (e.g. {"NOM1 Prénom1":"username1"})
    
    Returns:
        pd.Series: A Series containing the surname, firstname and username of the user.
    """
    if row is None:
        return pd.Series([None, None, None])
    else:
        name, username = next(iter(row.items()))
        try:
            # Parse firstname and surname
            surname, firstname, _ = re.search(r'(.+) (\b[A-Z]((?![A-Z]).)+\b)', name).groups()
        except AttributeError:
            surname, firstname = name, ''

        return pd.Series([surname, firstname, username])

def read_json(path):
    """
    Read the JSON file and return the data as a tuple of DataFrames and dicts.

    Parameters:
        path (str): The path to the JSON file.
    
    Returns:
        df (pd.DataFrame): The DataFrame containing the sessions from the JSON file.
        session_types (dict): A dict containing the session types and labels from the JSON file.
        modules (dict): A dict containing the modules names and labels from the JSON file.
        ue (dict): A dict containing the UE names and labels from the JSON file.
        users (pd.DataFrame): The DataFrame containing the users surname,
            firstname and username from the JSON file.
    """
    df = pd.read_json(path, convert_dates=False)

    df['date_start'] = pd.to_datetime(df['date'] + ' ' + df['heuredeb'])
    df['date_end'] = pd.to_datetime(df['date'] + ' ' + df['heurefin'])

    session_types = df[['type_synapses', 'libelle']].drop_duplicates()
    session_types = {row['type_synapses']: row['libelle'] for _, row in session_types.iterrows()}

    modules = df[['module', 'intitule_module']].drop_duplicates()
    modules = {row['module']: row['intitule_module'] for _, row in modules.iterrows()}

    ue = df[['ue', 'intitule_ue']].drop_duplicates()
    ue = {row['ue']: row['intitule_ue'] for _, row in ue.iterrows()}

    users = df['intervenants'].explode().drop_duplicates().dropna()
    users = users.apply(parse_users).rename(columns={0: 'surname', 1: 'firstname', 2: 'username'})
    users.reset_index(drop=True, inplace=True)

    df['intervenants'] = df['intervenants'].fillna('').apply(list)
    df['intervenants'] = df['intervenants'].apply(lambda row: [next(iter(user.values())) for user in row])

    df['salles'] = df['salles'].apply(lambda row: ', '.join(row))

    df = df[['id',
             'module',
             'ue',
             'intervenants',
             'groupes',
             'type_synapses',
             'salles',
             'date_start',
             'date_end']]

    return df, session_types, modules, ue, users

def populate_db(sessions: pd.DataFrame, session_types: dict, modules: dict, ue, users: pd.DataFrame):
    """
    Populate database with data from Synapses.

    First, the Role table is populated with the roles declared in the roles dict.
    Then, the SessionType, Module, UE and User tables are populated with the data from the JSON file.
    Finally, the Session table is populated with the data from the JSON file.

    Parameters:
        sessions (pd.DataFrame): The DataFrame containing the sessions from the JSON file.
        session_types (dict): A dict containing the session types and labels from the JSON file.
        modules (dict): A dict containing the modules names and labels from the JSON file.
        ue (dict): A dict containing the UE names and labels from the JSON file.
        users (pd.DataFrame): The DataFrame containing the users surname,
            firstname and username from the JSON file.
    
    Returns:
        result: A list containing messages about the sessions added to the database.
    """
    
    # Populate Role table
    roles = {'Autre': -1,
             'Professeur': 0,
             'Doctorant': 1,
             'Vacataire': 2}
    
    for name, id in roles.items():
        role_in_db = db_session.execute(
            select(Role)
            .where(Role.name == name)
            ).scalars().first()

        if role_in_db is None:
            role = Role(
                name=name,
                id=id
            )
            db_session.add(role)

        else:
            if role_in_db.id != id:
                role_in_db.id = id
                db_session.add(role_in_db)

    # Populate SessionType table
    for type, libele in session_types.items():
        session_type_in_db = db_session.execute(
            select(SessionType)
            .where(SessionType.id == type)
            ).scalars().first()

        if session_type_in_db is None:
            session_type = SessionType(
                id=type,
                name=libele
            )
            db_session.add(session_type)

        else:
            if session_type_in_db.name != libele:
                session_type_in_db.name = libele
                db_session.add(session_type_in_db)

    # Populate Module table
    for module_name, module_label in modules.items():

        module_in_db = db_session.execute(
            select(Module)
            .where(Module.name == module_name)
            ).scalars().first()

        if module_in_db is None:
            module = Module(
                name=module_name,
                label=module_label
            )
            db_session.add(module)

        else:
            if module_in_db.label != module_label:
                module_in_db.label = module_label
                db_session.add(module_in_db)

    # Populate UE table
    for ue_name, ue_label in ue.items():
        ue_in_db = db_session.execute(
            select(Ue)
            .where(Ue.name == ue_name)
            ).scalars().first()

        if ue_in_db is None:
            ue = Ue(
                name=ue_name,
                label=ue_label
            )
            db_session.add(ue)

        else:
            if ue_in_db.label != ue_label:
                ue_in_db.label = ue_label
                db_session.add(ue_in_db)
    
    # Populate User table
    for _, user in users.iterrows():
        user_in_db = db_session.execute(
            select(User)
            .where(User.username == user['username'])
            ).scalars().first()

        if user_in_db is None:
            user = User(
                surname=user['surname'],
                name=user['firstname'],
                username=user['username']
            )
            db_session.add(user)

    # Populate Session table
    
    # Computing session ids to add, update and delete
    sessions_id_in_db = db_session.execute(select(Session.id)).scalars().all()

    db_ids = set(sessions_id_in_db)
    new_ids = set(sessions['id'])

    ids_to_add = new_ids - db_ids
    ids_to_update = new_ids & db_ids
    ids_to_delete = db_ids - new_ids

    # Add new sessions
    new = 0
    for _, row in sessions.loc[sessions['id'].isin(ids_to_add)].iterrows():
        new += 1
        session = Session(
            id=row['id'],
            module=db_session.execute(
                        select(Module)
                        .where(Module.name == row['module'])
                        ).scalars().first(),
            ue=db_session.execute(
                        select(Ue)
                        .where(Ue.name == row['ue'])
                        ).scalars().first(),
            group_name=row['groupes'],
            type=row['type_synapses'],
            salle=row['salles'],
            date_start=row['date_start'],
            date_end=row['date_end']
        )
        db_session.add(session)

        for user in row['intervenants']:
            lecturer = LecturedBy(session_id=row['id'],
                                user_username=user,
                                synapse=True)
            db_session.add(lecturer)
    
    # Update existing sessions
    modified = 0
    not_changed = 0
    for _, row in sessions.loc[sessions['id'].isin(ids_to_update)].iterrows():

        session = db_session.execute(
            select(Session)
            .where(Session.id == row['id'])
            ).scalars().first()
        
        message = ""

        if session.module.name != row['module']:
            message += f"Session {row['id']} has changed module from {session.module.name} to {row['module']}. "
            session.module = db_session.execute(
                select(Module)
                .where(Module.name == row['module'])
                ).scalars().first()

        if session.ue.name != row['ue']:
            message += f"Session {row['id']} has changed UE from {session.ue.name} to {row['ue']}. "
            session.ue = db_session.execute(
                select(Ue)
                .where(Ue.name == row['ue'])
                ).scalars().first()

        if session.group_name != row['groupes']:
            message += f"Session {row['id']} has changed group from {session.group_name} to {row['groupes']}. "
            session.group_name = row['groupes']

        if session.type != row['type_synapses']:
            message += f"Session {row['id']} has changed type from {session.type} to {row['type_synapses']}. "
            session.type = row['type_synapses']

        if session.salle != row['salles']:
            message += f"Session {row['id']} has changed salle from {session.salle} to {row['salles']}. "
            session.salle = row['salles']

        if session.date_start != row['date_start']:
            message += f"Session {row['id']} has changed start date from {session.date_start} to {row['date_start']}. "
            session.date_start = row['date_start']

        if session.date_end != row['date_end']:
            message += f"Session {row['id']} has changed end date from {session.date_end} to {row['date_end']}. "
            session.date_end = row['date_end']
        
        if message != "":
            db_session.add(session)
            
        for user in row['intervenants']:
            lecturer_in_db = db_session.execute(
                                select(LecturedBy)
                                .where(LecturedBy.session_id == row['id'])
                                .where(LecturedBy.user_username == user)
                                ).scalars().first()

            if lecturer_in_db is None:
                lecturer = LecturedBy(session_id=row['id'],
                                    user_username=user,
                                    synapse=True)
                db_session.add(lecturer)
                message += f"Session {row['id']} has new lecturer {user}. "

            else:
                lecturer_in_db.synapse = True
                db_session.add(lecturer_in_db)
        
        if message != "":
            modified += 1
        else:
            not_changed += 1

    # Delete sessions
    deleted = 0
    for session_id in ids_to_delete:
        session = db_session.execute(
            select(Session)
            .where(Session.id == session_id)
            ).scalars().first()

        db_session.delete(session)
        deleted += 1

    db_session.commit()
    result = [f'{new} new sessions', 
              f'{modified} modified sessions', 
              f'{not_changed} not changed sessions',
              f'{deleted} deleted sessions']
    return result
