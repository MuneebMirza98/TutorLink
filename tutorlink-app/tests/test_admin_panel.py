from sqlalchemy import select
from flask import get_flashed_messages

# Test de la route admin_panel

def test_01_admin_panel_route_as_admin(web_client):
    """Test de la route admin_panel"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    response = web_client.get('admin/panel', follow_redirects=True)
    assert response.status_code == 200

def test_02_admin_panel_route_as_user(web_client):
    """Test de la route admin_panel"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'benaben'

    response = web_client.get('admin/panel', follow_redirects=True)
    assert response.status_code == 403

def test_03_admin_panel_route_as_guest(web_client):
    """Test de la route admin_panel"""

    response = web_client.get('admin/panel', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/auth/login'

# Test de la route grant_admin

def test_01_grant_admin_role_as_admin(web_client, db_objects):
    """Test de la route grant_admin_role en tant qu'admin"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'
    
    username = 'benaben'

    response = web_client.post(f'admin/grant_admin/{username}', follow_redirects=True)
    assert response.status_code == 200

    # On vérifie que l'utilisateur a bien le rôle admin
    db_session = db_objects['db_session']
    User = db_objects['User']
    user = db_session.execute(
                select(User)
                .where(User.username == username)
            ).scalars().first()

    assert user is not None
    assert user.admin

def test_02_grant_admin_role_as_user(web_client):
    """Test de la route grant_admin_role en tant qu'utilisateur"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'cleduff'
    
    username = 'benaben'

    response = web_client.post(f'admin/grant_admin/{username}', follow_redirects=True)
    assert response.status_code == 403

def test_03_grant_admin_role_already_admin(web_client, db_objects):
    """Test de la route grant_admin_role pour un utilisateur déjà admin"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'
    
    username = 'benaben'

    response = web_client.post(f'admin/grant_admin/{username}', follow_redirects=True)
    assert response.status_code == 200

    message = get_flashed_messages()
    cond = False
    for m in message:
        if f"User {username} already has admin privileges." in m:
            cond = True
    assert cond

    # On vérifie que l'utilisateur a toujours le rôle admin
    db_session = db_objects['db_session']
    User = db_objects['User']
    user = db_session.execute(
                select(User)
                .where(User.username == username)
            ).scalars().first()

    assert user is not None
    assert user.admin

def test_04_grant_admin_role_inexistant_user(web_client):
    """Test de la route grant_admin_role pour un utilisateur inexistant"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'
    
    username = 'inexistant_user'

    response = web_client.post(f'admin/grant_admin/{username}', follow_redirects=True)
    assert response.status_code == 200

    message = get_flashed_messages()
    cond = False
    for m in message:
        if f"User {username} does not exist" in m:
            cond = True
    assert cond

# Test de la route revoke_admin

def test_01_revoke_admin_role_as_admin(web_client, db_objects):
    """Test de la route revoke_admin_role en tant qu'admin"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'
    
    username = 'benaben'

    response = web_client.post(f'admin/revoke_admin/{username}', follow_redirects=True)
    assert response.status_code == 200

    # On vérifie que l'utilisateur n'a plus le rôle admin
    db_session = db_objects['db_session']
    User = db_objects['User']
    user = db_session.execute(
                select(User)
                .where(User.username == username)
            ).scalars().first()

    assert user is not None
    assert not user.admin

def test_02_revoke_admin_role_as_user(web_client):
    """Test de la route revoke_admin_role en tant qu'utilisateur"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'cleduff'
    
    username = 'benaben'
    
    response = web_client.post(f'admin/revoke_admin/{username}', follow_redirects=True)
    assert response.status_code == 403

def test_03_revoke_admin_role_already_user(web_client, db_objects):
    """Test de la route revoke_admin_role pour un utilisateur déjà plus admin"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'
    
    username = 'benaben'

    response = web_client.post(f'admin/revoke_admin/{username}', follow_redirects=True)
    assert response.status_code == 200

    message = get_flashed_messages()
    cond = False
    for m in message:
        if f"User {username} does not have admin privileges" in m:
            cond = True
    assert cond

    # On vérifie que l'utilisateur n'a toujours pas le rôle admin
    db_session = db_objects['db_session']
    User = db_objects['User']
    user = db_session.execute(
                select(User)
                .where(User.username == username)
            ).scalars().first()

    assert user is not None
    assert not user.admin

def test_04_revoke_admin_role_inexistant_user(web_client):
    """Test de la route revoke_admin_role pour un utilisateur inexistant"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    username = 'inexistant_user'

    response = web_client.post(f'admin/revoke_admin/{username}', follow_redirects=True)
    assert response.status_code == 200

    message = get_flashed_messages()
    cond = False
    for m in message:
        if f"User {username} does not exist" in m:
            cond = True
    assert cond
