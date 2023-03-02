# Tests basiques de l'application

def test_01_config_testing(test_app):
    """Vérification de l'utilisation de la base de tests"""

    assert test_app.testing is True


def test_02_hello_route(web_client):
    """Test de la route hello"""

    response = web_client.get('/hello')
    assert b"Hello, World!" == response.data
