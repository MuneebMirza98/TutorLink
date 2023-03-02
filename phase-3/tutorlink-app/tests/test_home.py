from flask import url_for


def test_01_consultation_no_login(web_client):
    """Test d'accès à la page d'accueil sans être connecté"""

    # On accède à la page d'accueil
    response = web_client.get('/')
    assert response.status_code == 302
    
    response = web_client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == url_for('auth.login')

    assert url_for('home.index') == url_for('index') == '/'

def test_02_consultation(web_client, test_app):
    """Test d'accès à la page d'accueil en étant connecté"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    # On accède à la page d'accueil
    response = web_client.get('/')
    assert response.status_code == 200

def test_03_doctorant(web_client):
    """Test d'accès à la page d'accueil en étant connecté en tant que doctorant"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'cleduff'

    # On accède à la page d'accueil
    response = web_client.get('/')
    assert response.status_code == 200

    assert b"circular-progress" in response.data

def test_04_enseignant(web_client):
    """Test d'accès à la page d'accueil en étant connecté en tant qu'enseignant"""

    # On simule la connexion CAS de l'utilisateur
    with web_client.session_transaction() as session:
        session['CAS_USERNAME'] = 'amontarn'

    # On accède à la page d'accueil
    response = web_client.get('/')
    assert response.status_code == 200

    assert bytes("/∞", 'utf-8') in response.data
