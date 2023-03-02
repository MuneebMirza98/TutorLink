from flask import g, get_flashed_messages
from sqlalchemy import select

from .test_db import create_user_in_db, delete_user_in_db

# Test de la route /profile/

def test_01_profile_edit(web_client, test_app, db_objects):
    """Test de la route /profile/ avec des données valides"""

    # on créer un nouvel utilisateur
    db_session = db_objects['db_session']
    User = db_objects['User']

    username = "ttest"
    user = create_user_in_db(db_objects, username=username)

    assert db_session.execute(
                select(User)
                .where(User.username == username)
            ).scalars().first() is not None

    with test_app.app_context():
        # On simule la connexion CAS de l'utilisateur
        with web_client.session_transaction() as session:
            session['CAS_USERNAME'] = username

        response = web_client.post('/profile/',
                                    data=dict(
                                        email="test.test2@mail.com",
                                        name="test",
                                        surname="test2",
                                        role=2,
                                        admin=False),
                                    follow_redirects=True)

        assert response.status_code == 200

        messages = get_flashed_messages()
        assert "Profile updated." in messages

        assert g.user is not None
        assert g.user.username == 'ttest'
        assert g.user.email == 'test.test2@mail.com'
        assert g.user.name == 'test'
        assert g.user.surname == 'test2'
        assert g.user.role_id == 2
        assert g.user.admin == False
    
    delete_user_in_db(db_objects, user=user)

def test_02_profile_edit_without_data(web_client, test_app, db_objects):
    """Test de la route /profile/ sans données"""

    # on créer un nouvel utilisateur
    db_session = db_objects['db_session']
    User = db_objects['User']

    username = "ttest"
    user = create_user_in_db(db_objects, username=username)

    assert db_session.execute(
                select(User)
                .where(User.username == username)
            ).scalars().first() is not None

    with test_app.app_context():
        # On simule la connexion CAS de l'utilisateur
        with web_client.session_transaction() as session:
            session['CAS_USERNAME'] = username

        response = web_client.post('/profile/',
                                    data=dict(
                                        email="",
                                        surname="",
                                        role=2,
                                        admin=False),
                                    follow_redirects=True)

        assert response.status_code == 200
        messages = get_flashed_messages()
        cond = False
        for message in messages:
            if f'Email is required. ' in message:
                cond = True
        assert cond
    
    delete_user_in_db(db_objects, user=user)
