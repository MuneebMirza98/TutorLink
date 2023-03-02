from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from tutorlink.db import db_session, Role
from sqlalchemy import select
from tutorlink.auth import login_required

bp = Blueprint("profile", __name__, url_prefix="/profile")

@bp.route("/", methods=(["GET", "POST"]))
@login_required
def profile():
    """
    This view allows the user to update their profile.

    User needs to be logged in to access this view.
    """
    # Update profile
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
            g.user.email = email
            g.user.name = name
            g.user.surname = surname
            g.user.role = role

            db_session.add(g.user)
            db_session.commit()

            flash("Profile updated.", "success")
            return redirect(url_for("profile.profile"))
        else:
            flash(error, "error")
    
    roles = db_session.execute(select(Role)).scalars()
    
    return render_template("profile/user.html",
                            roles=roles)
