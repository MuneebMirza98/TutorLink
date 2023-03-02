from flask import g, get_flashed_messages
from sqlalchemy import select

from .test_db import create_user_in_db, delete_user_in_db

def register_new_user(web_client):
    """Fonction qui permet d'enregistrer un utilisateur avec la route /auth/register"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'ttest'

    # On créer un nouvel utilisateur
    response = web_client.post('/auth/register', 
                                data={
                                    'email': 'test.test@mail.com',
                                    'name': 'test',
                                    'surname': 'test',
                                    'role': -1,
                                },
                                follow_redirects=True)

    return response

# Test de la route /auth/register

def test_01_register_new_user(web_client, test_app, db_objects):
    """Test de la route /auth/register avec des données valides"""

    with test_app.app_context():
        response = register_new_user(web_client)
        assert response.status_code == 200

        messages = get_flashed_messages()
        assert 'Registration ok' in messages
        
        # On vérifie que l'utilisateur a bien été créé dans la base
        db_session = db_objects['db_session']
        User = db_objects['User']
        db_user = db_session.execute(
                        select(User)
                        .where(User.username == 'ttest')
                    ).scalars().first()

        assert db_user is not None
        # assert db_user is g.user

        # On vérifie que l'utilisateur est bien connecté
        assert g.user is not None
        assert g.user.username == 'ttest'
    
    delete_user_in_db(db_objects)
        

def test_02_register_without_data(web_client, db_objects):
    """Test de la route /auth/register sans données"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'ttest'
    # on tente de créer un nouvel utilisateur (sans envoyer de données)
    response = web_client.post('/auth/register')
    assert response.status_code == 200

    messages = get_flashed_messages()
    cond = False
    for message in messages:
        if 'Email is required' in message:
            cond = True
    assert cond

    delete_user_in_db(db_objects)
        

def test_03_register_without_name(web_client, db_objects):
    """Test de la route /auth/register sans le nom"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'ttest'
    # on tente de créer un nouvel utilisateur (sans toutes les données)
    response = web_client.post('/auth/register',
                               data={
                                    'email': 'test.test@mail.com'
                                    })

    assert response.status_code == 200

    messages = get_flashed_messages()
    cond = False
    for message in messages:
        if 'Name is required' in message:
            cond = True
    assert cond

    delete_user_in_db(db_objects)


def test_04_register_with_inexistant_role(web_client, db_objects):
    """Test de la route /auth/register avec un rôle inexistant"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'ttest'

    # on tente de créer un nouvel utilisateur (avec mot de passe vide)
    role = 'impossible role'
    response = web_client.post('/auth/register', data={
                                    'email': 'test.test@mail.com',
                                    'name': 'test',
                                    'surname': 'test',
                                    'role': role,
                                })
    assert response.status_code == 200

    messages = get_flashed_messages()
    cond = False
    for message in messages:
        if f'Invalid role. ' in message:
            cond = True
    assert cond

    delete_user_in_db(db_objects)

def test_05_register_with_existing_username(web_client, db_objects):
    """Test de la route /auth/register avec un nom d'utilisateur existant"""

    # On créer un nouvel utilisateur
    user = create_user_in_db(db_objects, username='ttest_05_register', no_data=True)

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'ttest_05_register'

    # On tente de créer un nouvel utilisateur avec le même nom d'utilisateur
    response = web_client.post('/auth/register',
                                data={
                                    'email': 'test.test@mail.com',
                                    'name': 'test',
                                    'surname': 'test',
                                    'role': 1
                                },
                                follow_redirects=True)
    
    assert response.status_code == 200

    messages = get_flashed_messages()
    cond = False
    for message in messages:
        if 'Registration ok' in message:
            cond = True
    assert cond

    # On vérifie que l'utilisateur a bien été mis à jour dans la base
    db_session = db_objects['db_session']
    User = db_objects['User']
    db_user = db_session.execute(
                    select(User)
                    .where(User.username == 'ttest_05_register')
                ).scalars().first()

    assert db_user is not None
    assert db_user.email == 'test.test@mail.com'
    assert db_user.name == 'test'
    assert db_user.surname == 'test'
    assert db_user.role_id == 1

    delete_user_in_db(db_objects, username='ttest_05_register')

def test_06_register_redirect_user_missing_data(web_client, test_app, db_objects):
    """Test de la redirection vers la route /auth/register avec un utilisateur existant mais sans données"""

    with test_app.app_context():
        # On créer un nouvel utilisateur
        user = create_user_in_db(db_objects, username='ttest_06_register', no_data=True)
    
        # On simule la connexion CAS de l'utilisateur
        with web_client.session_transaction() as session:
            session['CAS_USERNAME'] = 'ttest_06_register'
        # On tente de créer un nouvel utilisateur avec le même nom d'utilisateur
        response = web_client.get('/', follow_redirects=True)

        assert response.status_code == 200
        assert response.request.path == '/auth/register'

        delete_user_in_db(db_objects, username='ttest_06_register')

# Test de connexion

def test_01_login(web_client, test_app, db_objects):
    """Test de connexion d'un utilisateur existant"""

    # on créer un nouvel utilisateur
    user = create_user_in_db(db_objects, username='ttest2')

    with test_app.app_context():
        # On simule la connexion CAS de l'utilisateur
        with web_client.session_transaction() as session:
            session['CAS_USERNAME'] = 'ttest2'

        response = web_client.get('/hello')

        db_session = db_objects['db_session']
        User = db_objects['User']
        db_user = db_session.execute(
                        select(User)
                        .where(User.username == 'ttest2')
                    ).scalars().first()

        # On vérifie que l'utilisateur est bien connecté
        assert response.status_code == 200
        assert g.user is not None
        assert g.user.username == 'ttest2'

    delete_user_in_db(db_objects, user=user)
