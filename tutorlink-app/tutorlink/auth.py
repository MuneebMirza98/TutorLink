import functools
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import abort

from tutorlink.db import db_session, User, Role
from sqlalchemy import select


bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(function):
    @functools.wraps(function)
    def wrap(*args, **kwargs):
        if 'CAS_USERNAME' not in session:
            session['CAS_AFTER_LOGIN_SESSION_URL'] = (
                request.script_root +
                request.full_path
            )
            return redirect(url_for('auth.login', _external=True))
        else:
            return function(*args, **kwargs)
    return wrap

def admin_required(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if not g.user.admin:
            abort(403)
        return function(*args, **kwargs)
    return wrapper

@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    username = session.get("CAS_USERNAME")

    # Not logged in
    if username is None:
        g.user = None
    
    # Logged in with CAS
    else:
        g.user = db_session.execute(
            select(User)
            .where(User.username == username)
        ).scalars().first()

        # User is not registered or some information is missing
        # Redirect every requests to the registration page except for 
        # the request to the registration page itself, the logout page and the static files
        authorized_routes = ["auth.register", "cas.logout", "static"]

        if (g.user is None
            or not (g.user.email
                    and g.user.name
                    and g.user.surname
                    and g.user.role_id is not None)):
            
            if request.endpoint not in authorized_routes:
                return redirect(url_for("auth.register"))


@bp.route("/register", methods=("GET", "POST"))
@login_required
def register():
    """
    Register a new user.

    Check if the user is already registered. If not, prompt for email, name, surname and role.

    If the user is already registered but some information is missing, prompt for the missing information.

    If the user is already registered and all information is present, redirect to the index page.
    """
    if (g.user is not None
        and g.user.email
        and g.user.name
        and g.user.surname
        and g.user.role_id is not None):
        return redirect(url_for("index"))
    
    roles = db_session.execute(
        select(Role)
    ).scalars().all()

    username = session.get("CAS_USERNAME")

    if request.method == "POST":
        error = ""

        email = request.form.get("email", '').strip()
        name = request.form.get("name", '').strip()
        surname = request.form.get("surname", '').strip()
        try:
            role_id = int(request.form.get("role", -1))
        except ValueError:
            error += "Invalid role. "
            role_id = -1

        role = db_session.execute(
                select(Role)
                .where(Role.id == role_id)
            ).scalars().first()

        if email == '':
            error += "Email is required. "

        if name == '':
            error += "Name is required. "
        
        if surname == '':
            error += "Surname is required. "

        if role is None:
            error += f"Role {role_id} does not exist. "

        if error == '':
            preexistant_user = db_session.execute(
                select(User).
                where(User.username == username)
            ).scalars().first()

            if preexistant_user is not None:
                preexistant_user.email = email
                preexistant_user.name = name
                preexistant_user.surname = surname
                preexistant_user.role = role            
            else:
                new_user = User(
                    username=username,
                    email=email,
                    name=name,
                    surname=surname,
                    role=role,
                    admin=False
                )
                db_session.add(new_user)
            db_session.commit()
            flash("Registration ok", "success")
            return redirect(url_for("index"))

        flash(error, "error")

    return render_template("auth/register.html",
                            username=session.get("CAS_USERNAME"),
                            roles=roles)

@bp.route("/login")
def login():
    """
    Login page.

    If the user is already logged in, redirect to the index page.
    """
    if g.user:
        return redirect(url_for("index"))
    
    return render_template("auth/login.html")

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
