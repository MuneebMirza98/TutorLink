from flask import get_flashed_messages

# Tests de la liste des sessions

def test_01_session_list_no_login(web_client):
    """Test de la liste des sessions sans être connecté"""

    response = web_client.get('/session/list',
                              follow_redirects=True)

    # On vérifie que l'on est bien redirigé vers la page de login
    assert response.status_code == 200
    assert response.request.path == '/auth/login'

def test_02_session_list(web_client):
    """Test de la liste des sessions sans paramètres"""
    
    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.get('/session/list')
    
    assert response.status_code == 200

def test_03_session_list_with_params(web_client):
    """Test de la liste des sessions avec paramètres"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.get('/session/list',
                               query_string=dict(
                                    module=[1,2],
                                    type=['CM','TD'],
                                    date_min='2020-01-01',
                                    date_max='2025-01-31',
                               ))
    
    assert response.status_code == 200

def test_04_session_list_with_bad_module(web_client):
    """Test de la liste des sessions avec un module incorrect"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.get('/session/list',
                               query_string=dict(
                                    module=[1,2,'bad module'],
                                    type=['CM','TD'],
                                    date_min='2020-01-01',
                                    date_max='2025-01-31',
                               ))
    
    assert response.status_code == 200

    messages = get_flashed_messages()
    cond = False
    for message in messages:
        if f'Invalid type for modules. ' in message:
            cond = True
    assert cond

def test_05_session_list_with_bad_date_max(web_client):
    """Test de la liste des sessions avec une date incorrecte"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.get('/session/list',
                               query_string=dict(
                                    module=[1,2],
                                    type=['CM','TD'],
                                    date_min='2020-01-01',
                                    date_max='bad date',
                               ))
    
    assert response.status_code == 200

    messages = get_flashed_messages()
    cond = False
    for message in messages:
        if f'Invalid date format for max date. ' in message:
            cond = True
    assert cond

def test_06_session_list_with_bad_date_min(web_client):
    """Test de la liste des sessions avec une date incorrecte"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.get('/session/list',
                               query_string=dict(
                                    module=[1,2],
                                    type=['CM','TD'],
                                    date_min='bad date',
                                    date_max='2025-01-31',
                               ))
    
    assert response.status_code == 200

    messages = get_flashed_messages()
    cond = False
    for message in messages:
        if f'Invalid date format for min date. ' in message:
            cond = True
    assert cond

def test_07_session_list_with_bad_page(web_client):
    """Test de la liste des sessions avec une page incorrecte"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.get('/session/list',
                               query_string=dict(
                                    page='bad page',
                               ))
    
    assert response.status_code == 200
    assert '<input class="page-link" name="page" value="1" type="submit" disabled/>' in response.data.decode('utf-8')

def test_08_session_list_with_bad_session_type(web_client):
    """Test de la liste des sessions avec un type de session incorrect"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.get('/session/list',
                               query_string=dict(
                                    type=['CM','TD','bad type'],
                               ))
    
    assert response.status_code == 200

def test_09_session_list_with_inexistant_module_id(web_client):
    """Test de la liste des sessions avec un module inexistant"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.get('/session/list',
                               query_string=dict(
                                    module=[1,2,9999],
                               ))
    
    assert response.status_code == 200

def test_10_session_list_with_bad_ue_id(web_client):
    """Test de la liste des sessions avec une UE incorrecte"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.get('/session/list',
                               query_string=dict(
                                    ue=[1,2,'bad ue'],
                               ))
    
    assert response.status_code == 200

    messages = get_flashed_messages()
    cond = False
    for message in messages:
        if f'Invalid type for UEs. ' in message:
            cond = True
    assert cond


# Tests de la fonction pages_list

def test_01_pages_list(web_client, test_app, db_objects):
    """Test de la fonction pages_list"""

    from tutorlink.session import pages_list

    assert pages_list(5, 12) == [1, 2, 3, 4, 5, 6, 7, None, 12]
    assert pages_list(6, 12) == [1, None, 4, 5, 6, 7, 8, None, 12]
    assert pages_list(7, 12) == [1, None, 5, 6, 7, 8, 9, None, 12]
    assert pages_list(8, 12) == [1, None, 6, 7, 8, 9, 10, 11, 12]


# Tests de l'enregistrement à une session

def test_01_session_register_no_login(web_client):
    """Test de l'enregistrement à une session sans être connecté"""

    response = web_client.post('/session/register',
                              follow_redirects=True)

    # On vérifie que l'on est bien redirigé vers la page de login
    assert response.status_code == 200
    assert response.request.path == '/auth/login'

def test_02_session_register(web_client, db_objects):
    """Test de l'enregistrement à une session"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'cleduff'

    response = web_client.post('/session/register',
                               data=dict(
                                    session_id=3,
                               ))
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if f'You have successfully registered for the session.' in message and cat == 'success':
            cond = True
    assert cond

    db_session = db_objects['db_session']
    LecturedBy = db_objects['LecturedBy']

    lectured_by = db_session.query(LecturedBy).filter_by(user_username='cleduff', session_id=3).first()
    assert lectured_by is not None

def test_03_session_register_already_registered(web_client):
    """Test de l'enregistrement à une session"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'cleduff'

    response = web_client.post('/session/register',
                               data=dict(
                                    session_id=3,
                               ))
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if f'cleduff is already registered for this session. ' in message and cat == 'error':
            cond = True
    assert cond

def test_04_session_register_bad_session_id(web_client):
    """Test de l'enregistrement à une session avec un mauvais id de session"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.post('/session/register',
                               data=dict(
                                    session_id='bad session id',
                               ))
    
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if f'Invalid session id.' in message and cat == 'error':
            cond = True
    assert cond

def test_05_session_register_inexistant_session_id(web_client):
    """Test de l'enregistrement à une session avec un id de session inexistant"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.post('/session/register',
                               data=dict(
                                    session_id=1000,
                               ))
    
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if f'The session with id 1000 does not exist.' in message and cat == 'error':
            cond = True
    assert cond

def test_06_session_register_other_user_no_role(web_client):
    """Test de l'enregistrement à une session avec un autre utilisateur sans rôle"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'cleduff'

    response = web_client.post('/session/register',
                               data=dict(
                                    session_id=3,
                                    username='amontarn'
                               ))
    
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if f'You are not allowed to register other users.' in message and cat == 'error':
            cond = True
    assert cond

def test_07_session_register_other_user_as_manager(web_client, db_objects):
    """Test de l'enregistrement à une session avec un autre utilisateur en tant que manager"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'cleduff'

    response = web_client.post('/session/register',
                               data=dict(
                                    session_id=1,
                                    username='amontarn'
                               ))
    
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if 'amontarn has successfully been registered for the session.' in message and cat == 'success':
            cond = True
    assert cond

    db_session = db_objects['db_session']
    LecturedBy = db_objects['LecturedBy']

    assert db_session.query(LecturedBy).filter_by(user_username='amontarn', session_id=1).first() is not None

def test_08_session_register_other_user_as_admin(web_client, db_objects):
    """Test de l'enregistrement à une session avec un autre utilisateur en tant qu'admin"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.post('/session/register',
                               data=dict(
                                    session_id=2,
                                    username='benaben'
                               ))
    
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if 'benaben has successfully been registered for the session.' in message and cat == 'success':
            cond = True
    assert cond

    db_session = db_objects['db_session']
    LecturedBy = db_objects['LecturedBy']

    lectured_by = db_session.query(LecturedBy).filter_by(user_username='benaben', session_id=2).first()
    assert lectured_by is not None

def test_09_session_register_inexistant_user(web_client):
    """Test de l'enregistrement à une session avec un utilisateur inexistant"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.post('/session/register',
                               data=dict(
                                    session_id=3,
                                    username='inexistant'
                               ))
    
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if f'Invalid username.' in message and cat == 'error':
            cond = True
    assert cond

# Tests de la désincription à une session

def test_01_session_unregister_no_login(web_client):
    """Test de l'enregistrement à une session sans être connecté"""

    response = web_client.post('/session/unregister',
                              follow_redirects=True)

    # On vérifie que l'on est bien redirigé vers la page de login
    assert response.status_code == 200
    assert response.request.path == '/auth/login'

def test_02_session_unregister(web_client, db_objects):
    """Test de la désincription à une session"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'cleduff'

    response = web_client.post('/session/unregister',
                               data=dict(
                                    session_id=3,
                               ))
    
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if f'You have successfully unregistered from the session.' in message and cat == 'success':
            cond = True
    assert cond

    db_session = db_objects['db_session']
    LecturedBy = db_objects['LecturedBy']

    lectured_by = db_session.query(LecturedBy).filter_by(user_username='cleduff', session_id=3).first()
    assert lectured_by is None

def test_03_session_unregister_already_unregistered(web_client):
    """Test de la désincription à une session déjà désinscrit"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'cleduff'

    response = web_client.post('/session/unregister',
                               data=dict(
                                    session_id=3,
                               ))
    
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if 'cleduff is not registered for this session.' in message and cat == 'error':
            cond = True
    assert cond

def test_05_session_unregister_bad_session_id(web_client):
    """Test de la désincription à une session avec un mauvais id de session"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.post('/session/unregister',
                               data=dict(
                                    session_id='bad id',
                               ))
    
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if f'Invalid session id.' in message and cat == 'error':
            cond = True
    assert cond

def test_05_session_unregister_inexistant_session_id(web_client):
    """Test de la désincription à une session avec un id de session inexistant"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.post('/session/unregister',
                               data=dict(
                                    session_id=1000,
                               ))
    
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if f'The session with id 1000 does not exist.' in message and cat == 'error':
            cond = True
    assert cond

def test_06_session_unregister_other_user_no_role(web_client):
    """Test de la désincription à une session avec un autre utilisateur sans rôle"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'cleduff'

    response = web_client.post('/session/unregister',
                               data=dict(
                                    session_id=3,
                                    username='benaben'
                               ))
    
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if 'You are not allowed to unregister other users.' in message and cat == 'error':
            cond = True
    assert cond

def test_07_session_unregister_other_user_as_manager(web_client, db_objects):
    """Test de la désincription à une session avec un autre utilisateur en tant que manager"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'cleduff'

    response = web_client.post('/session/unregister',
                               data=dict(
                                    session_id=1,
                                    username='amontarn'
                               ))
    
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if 'amontarn has successfully been unregistered from the session.' in message and cat == 'success':
            cond = True
    assert cond

    db_session = db_objects['db_session']
    LecturedBy = db_objects['LecturedBy']

    lectured_by = db_session.query(LecturedBy).filter_by(user_username='amontarn', session_id=1).first()
    assert lectured_by is None

def test_08_session_unregister_other_user_as_admin(web_client, db_objects):
    """Test de la désincription à une session avec un autre utilisateur en tant qu'admin"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.post('/session/unregister',
                               data=dict(
                                    session_id=2,
                                    username='benaben'
                               ))
    
    messages = get_flashed_messages(with_categories=True)
    cond = False
    for cat, message in messages:
        if 'benaben has successfully been unregistered from the session.' in message and cat == 'success':
            cond = True
    assert cond

    db_session = db_objects['db_session']
    LecturedBy = db_objects['LecturedBy']

    lectured_by = db_session.query(LecturedBy).filter_by(user_username='benaben', session_id=2).first()
    assert lectured_by is None
