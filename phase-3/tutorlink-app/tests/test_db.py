from sqlalchemy import select

# Test d'utilisation de la base de données
def create_user_in_db(db_objects, username="ttest", no_data=False):
    """Création d'un utilisateur dans la base de données"""

    db_session = db_objects['db_session']
    User = db_objects['User']

    if no_data:
        user = User(username=username)
    
    else:
        email = "test.test@mail.com"
        name = "test"
        surname = "test"
        role_id = 1
        admin = False

        user = User(username=username, email=email, name=name, surname=surname, role_id=role_id, admin=admin)

    assert isinstance(user, User)
    # on le prépare à être créé dans le base
    db_session.add(user)
    # on le créer réellement (on peut récuper son id automatique)
    db_session.commit()

    return user

def delete_user_in_db(db_objects, username="ttest", user=None):
    """Création d'un utilisateur dans la base de données"""

    db_session = db_objects['db_session']
    User = db_objects['User']

    user = user or db_session.execute(select(User).where(User.username == username)).scalars().first()

    if user is not None:
        # on efface l'utilisateur
        db_session.delete(user)
        db_session.commit()

def test_01_consultation(db_objects):
    """Test d'accès à la base de données"""

    db_session = db_objects['db_session']
    User = db_objects['User']
    Module = db_objects['Module']

    ordre = select(User)
    all_users = db_session.execute(ordre).scalars().all()
    for user in all_users:
        assert isinstance(user, User)
        for module in user.favorite_modules:
            assert isinstance(module, Module)
        for module in user.managed_modules:
            assert isinstance(module, Module)


def test_02_create_and_delete_user(db_objects):
    """Création et destruction d'un utilisateur dans la base de données"""
    db_session = db_objects['db_session']
    User = db_objects['User']

    username = "ttest"
    user = create_user_in_db(db_objects, username=username)
    
    # on le cherche dans la base
    db_user = db_session.execute(select(User).where(User.username == username)).scalars().first()
    assert db_user is not None
    assert isinstance(db_user, User)

    # on vérifie que l'ORM a bien fait son boulot (les deux objets sont les mêmes)
    assert user is db_user
    
    delete_user_in_db(db_objects, user=user)

    # on vérifie qu'il n'existe plus dans la base
    db_user = db_session.execute(select(User).where(User.username == username)).scalars().first()
    assert db_user is None
