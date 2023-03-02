import pandas as pd
from werkzeug.datastructures import FileStorage
import io
import json
from flask import get_flashed_messages, url_for
from sqlalchemy import select
import datetime

def test_01_data_update_route(web_client):
    """Test de l'affichage de la page de mise à jour des données"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.get('/data/update')

    assert response.status_code == 200

def test_02_data_update_route_with_bad_role(web_client):
    """Test de l'affichage de la page de mise à jour des données avec un rôle incorrect"""

    # On simule la connexion CAS de l'utilisateur non admin
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'benaben'

    response = web_client.get('/data/update')

    assert response.status_code == 403

def test_03_data_update_route_no_login(web_client):
    """Test de l'affichage de la page de mise à jour des données sans être connecté"""

    response = web_client.get('/data/update')
    assert response.status_code == 302

    response = web_client.get('/data/update', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == url_for('auth.login')


def test_04_parse_users():

    from tutorlink.data import parse_users

    assert parse_users(None).equals(pd.Series([None, None, None]))

    assert (pd.Series([{"FERTIER Audrey":"afertier"}]).apply(parse_users).values == pd.Series(['FERTIER', 'Audrey', 'afertier']).values).all()
    assert (pd.Series([{"FERTIER TEST Audrey":"afertier"}]).apply(parse_users).values == pd.Series(['FERTIER TEST', 'Audrey', 'afertier']).values).all()

    assert (pd.Series([{"FERTIER AUDREY":"afertier"}]).apply(parse_users).values == pd.Series(['FERTIER AUDREY', '', 'afertier']).values).all()

def test_05_read_json():
    """Test de la lecture du fichier JSON"""

    from tutorlink.data import read_json

    path = 'tests/populate.json'
    sessions, session_types, modules, ue, users = read_json(path)

    assert len(sessions) == 3
    assert ['id', 'module', 'ue', 'intervenants', 'groupes', 'type_synapses', 'salles', 'date_start', 'date_end'] == list(sessions.columns)
    assert [1,
            'MOD-IFIE3-G-S-ProjAgil-C1',
            'UE-IFIE3-GIPSI-S-OMng',
            list(['afertier', 'cleduff']),
            'IFIE3-GIPSI-GI2, IFIE3-GIPSI-GSI2',
            'TD',
            '0F05-zoom, 51-140 pers - 0F05',
            pd.Timestamp('2022-09-27 9:45:00'),
            pd.Timestamp('2022-09-27 11:15:00')] in sessions.values.tolist()
    assert [2,
            'MOD-IFIE3-G-S-ProjAgil-C1',
            'UE-IFIE3-GIPSI-S-OMng',
            list(['afertier', 'cleduff']),
            'IFIE3-GIPSI-GI2, IFIE3-GIPSI-GSI2',
            'TD',
            '0F05-zoom, 51-140 pers - 0F05',
            pd.Timestamp('2022-09-27 11:30:00'),
            pd.Timestamp('2022-09-27 13:00:00')] in sessions.values.tolist()
    assert [3,
            'MOD-IFIE3-G-GSI-ASCII-C1',
            'UE-IFIE3-GIPSI-GSI-ASD',
            list(['benaben']),
            'IFIE3-GIPSI-GSI',
            'CM',
            '1A23-zoom, 30-50 pers - 1A23',
            pd.Timestamp('2022-09-14 08:00:00'),
            pd.Timestamp('2022-09-14 09:30:00')] in sessions.values.tolist()
    

    # Check that the session types are correct
    assert len(session_types) == 2, session_types
    assert ("CM", "Cours Magistraux") in session_types.items()
    assert ("TD", "Travaux Dirigés") in session_types.items()

    # Check that the modules are correct
    assert len(modules) == 2
    assert ('MOD-IFIE3-G-S-ProjAgil-C1', 'Management agile de projets') in modules.items()
    assert ('MOD-IFIE3-G-GSI-ASCII-C1', 'Application Specifications (ASCII)') in modules.items()

    # Check that the UE are correct
    assert len(ue) == 2
    assert ('UE-IFIE3-GIPSI-S-OMng', 'Socle GIPSI : outils pour le management des organisations') in ue.items()
    assert ('UE-IFIE3-GIPSI-GSI-ASD', 'GSI : Application Spécification et développement (ASIDE)') in ue.items()

    # Check that the users are correct
    assert len(users) == 3
    assert ["LE DUFF", "Clara", "cleduff"] in users.values
    assert ["FERTIER", "Audrey", "afertier",] in users.values
    assert ["BENABEN", "Frederick", "benaben"] in users.values

def test_06_data_update_no_file(web_client):
    """Test de la mise à jour des données sans fichier"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.post('/data/update',
                               data=dict())

    assert response.status_code == 200

    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if cat == 'warning' and 'No file selected' in message:
            cond = True
    assert cond


def test_07_data_update(web_client, populate_file):
    """Test de la mise à jour des données"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.post('/data/update',
                               data=dict(file=populate_file))

    assert response.status_code == 200

    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if ('0 new sessions' in message
            and '0 modified sessions' in message
            and '3 not changed sessions' in message
            and '0 deleted sessions' in message):
            cond = True
    assert cond

def test_08_data_update_add_lecturer(web_client, populate_dict):
    """Test de la mise à jour des données avec ajout d'un intervenant"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    # On simule l'envoi d'un fichier JSON
    populate_dict[0]['intervenants'].append({'LAGARDE Julien':'jlagarde'})
    input_json = json.dumps(populate_dict, indent=4).encode("utf-8")

    json_file = FileStorage(
        stream=io.BytesIO(input_json),
        filename="Input.json",
        content_type="application/json",
    )
    
    response = web_client.post('/data/update',
                               data=dict(file=json_file))

    assert response.status_code == 200

    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if ('0 new sessions' in message
            and '1 modified sessions' in message
            and '2 not changed sessions' in message
            and '0 deleted sessions' in message):
            cond = True
    assert cond

def test_09_data_update_confirm_lecturer(web_client, populate_dict, db_objects):
    """Test de la mise à jour des données avec la confirmation d'un intervenant"""

    # On ajoute un intervenant à la session 1
    db_session = db_objects['db_session']
    LecturedBy = db_objects['LecturedBy']
    db_session.add(LecturedBy(session_id=1, user_username='benaben', synapse=False))
    db_session.commit()

    assert db_session.execute(
                select(LecturedBy)
                .filter_by(session_id=1, user_username='benaben')
            ).scalars().first() is not None

    assert db_session.execute(
                select(LecturedBy.synapse)
                .filter_by(session_id=1, user_username='benaben')
            ).scalars().first() == False

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'
    
    # On simule l'envoi d'un fichier JSON
    populate_dict[0]['intervenants'].append({"BENABEN Frederick":"benaben"})
    input_json = json.dumps(populate_dict, indent=4).encode("utf-8")

    json_file = FileStorage(
        stream=io.BytesIO(input_json),
        filename="Input.json",
        content_type="application/json",
    )

    response = web_client.post('/data/update',
                                 data=dict(file=json_file))
    
    assert response.status_code == 200

    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if ('0 new sessions' in message
            and '0 modified sessions' in message
            and '3 not changed sessions' in message
            and '0 deleted sessions' in message):
            cond = True
    assert cond


    assert db_session.execute(
                select(LecturedBy)
                .filter_by(session_id=1, user_username='benaben')
            ).scalars().first() is not None

    assert db_session.execute(
                select(LecturedBy.synapse)
                .filter_by(session_id=1, user_username='benaben')
            ).scalars().first() == True

def test_10_data_update_new_session(web_client, populate_dict, db_objects):
    """Test d'ajout de nouvelle session"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'
    
    # On simule l'envoi d'un fichier JSON
    populate_dict.append({
		"id" : 4,
		"ue" : "new_ue",
		"intitule_ue" : "New UE",
		"module" : "new_module",
		"intitule_module" : "New Module",
		"intervenants" : [{"TEST DATA UPDATE Test":"ttest_data_update"}],
		"groupes" : "Groupe 1, Groupe 2",
		"categorie_pers" : "DOC, PERS",
		"type_synapses" : "N",
		"libelle" : "Nouveau type de session",
		"date" : "2022-09-27",
		"salles" : ["Salle 1","Salle 2"],
		"heuredeb" : "14:15:00",
		"heurefin" : "15:45:00",
		"duree" : 1.5
	},)
    input_json = json.dumps(populate_dict, indent=4).encode("utf-8")

    json_file = FileStorage(
        stream=io.BytesIO(input_json),
        filename="Input.json",
        content_type="application/json",
    )

    response = web_client.post('/data/update',
                               data=dict(file=json_file))
    
    assert response.status_code == 200

    db_session = db_objects['db_session']
    Session = db_objects['Session']
    LecturedBy = db_objects['LecturedBy']
    User = db_objects['User']
    SessionType = db_objects['SessionType']
    Module = db_objects['Module']
    Ue = db_objects['Ue']

    # Session was added
    session = db_session.execute(
                    select(Session)
                    .filter_by(id=4)
                ).scalars().first()

    assert session is not None
    assert session.group_name == 'Groupe 1, Groupe 2'
    assert session.type == 'N'
    assert session.date_start == datetime.datetime(2022, 9, 27, 14, 15)
    assert session.date_end == datetime.datetime(2022, 9, 27, 15, 45)
    assert session.salle == 'Salle 1, Salle 2'

    # Lecturer was added
    assert db_session.execute(
                select(LecturedBy)
                .filter_by(session_id=4, user_username='ttest_data_update')
            ).scalars().first() is not None

    # New User was added
    user = db_session.execute(
                select(User)
                .filter_by(username='ttest_data_update')
            ).scalars().first()

    assert user is not None
    assert user.name == 'Test'
    assert user.surname == 'TEST DATA UPDATE'

    # New SessionType was added
    session_type = db_session.execute(
                        select(SessionType)
                        .filter_by(id='N')
                    ).scalars().first()

    assert session_type is not None
    assert session_type.name == 'Nouveau type de session'

    # New Module was added
    module = db_session.execute(
                select(Module)
                .filter_by(name='new_module')
            ).scalars().first()

    assert module is not None
    assert module.label == 'New Module'

    # New Ue was added
    ue = db_session.execute(
                select(Ue)
                .filter_by(name='new_ue')
            ).scalars().first()

    assert ue is not None
    assert ue.label == 'New UE'

def test_11_data_update_modify_session(web_client, populate_dict, db_objects):
    """Test de modification d'une session"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'
    
    # On simule l'envoi d'un fichier JSON
    populate_dict.append({
		"id" : 4,
		"ue" : "new_ue",
		"intitule_ue" : "New UE modified",
		"module" : "new_module",
		"intitule_module" : "New Module modified",
		"intervenants" : [{"TEST DATA UPDATE Test":"ttest_data_update"}],
		"groupes" : "Groupe modifié",
		"categorie_pers" : "DOC, PERS",
		"type_synapses" : "N",
		"libelle" : "Nouveau type de session modifié",
		"date" : "2022-09-28",
		"salles" : ["Salle modifiée"],
		"heuredeb" : "14:15:00",
		"heurefin" : "15:45:00",
		"duree" : 1.5
	},)
    input_json = json.dumps(populate_dict, indent=4).encode("utf-8")

    json_file = FileStorage(
        stream=io.BytesIO(input_json),
        filename="Input.json",
        content_type="application/json",
    )

    response = web_client.post('/data/update',
                               data=dict(file=json_file))
    
    assert response.status_code == 200

    db_session = db_objects['db_session']
    Session = db_objects['Session']
    SessionType = db_objects['SessionType']
    Module = db_objects['Module']
    Ue = db_objects['Ue']

    # Session was modified
    session = db_session.execute(
                    select(Session)
                    .filter_by(id=4)
                ).scalars().first()

    assert session is not None
    assert session.group_name == 'Groupe modifié'
    assert session.type == 'N'
    assert session.date_start == datetime.datetime(2022, 9, 28, 14, 15)
    assert session.date_end == datetime.datetime(2022, 9, 28, 15, 45)
    assert session.salle == 'Salle modifiée'

    # SessionType was modified
    session_type = db_session.execute(
                        select(SessionType)
                        .filter_by(id='N')
                    ).scalars().first()

    assert session_type is not None
    assert session_type.name == 'Nouveau type de session modifié'

    # Module was modified
    module = db_session.execute(
                    select(Module)
                    .filter_by(name='new_module')
                ).scalars().first()

    assert module is not None
    assert module.label == 'New Module modified'

    # Ue was modified
    ue = db_session.execute(
                select(Ue)
                .filter_by(name='new_ue')
            ).scalars().first()

    assert ue is not None
    assert ue.label == 'New UE modified'

def test_12_data_update_delete_session(web_client, populate_file):
    """Test de suppression d'une session"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.post('/data/update',
                               data=dict(file=populate_file))

    assert response.status_code == 200

    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if ('0 new sessions' in message
            and '0 modified sessions' in message
            and '3 not changed sessions' in message
            and '1 deleted sessions' in message):
            cond = True
    assert cond
