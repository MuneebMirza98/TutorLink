from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for
from flask import flash

from tutorlink.db import db_session, User
from tutorlink.auth import login_required, admin_required

from sqlalchemy import select


bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/panel")
@login_required
@admin_required
def admin_panel():
    """Show the admin panel of the application"""
    users = db_session.execute(select(User)).scalars().all()

    return render_template('admin/panel.html', users=users)

@bp.route('/grant_admin/<username>', methods=['POST'])
@login_required
@admin_required
def grant_admin(username):
    """
    Grant admin privileges to a user
    Only accessible by admin users
    
    Parameters:
        username (str): The username of the user to grant admin privileges to
    
    Returns:
        redirect: Redirects to the admin panel
    """
    user = db_session.query(User).filter(User.username == username).first()
    if user is None:
        flash(f"User {username} does not exist.", "error")
    elif user.admin:
        flash(f"User {username} already has admin privileges.", "warning")
    else:
        user.admin = True
        db_session.commit()
        flash(f"User {username} has been granted admin privileges.", "success")
    return redirect(url_for('admin.admin_panel'))

@bp.route('/revoke_admin/<username>', methods=['POST'])
@login_required
@admin_required
def revoke_admin(username):
    """
    Revoke admin privileges from a user
    Only accessible by admin users

    Parameters:
        username (str): The username of the user to revoke admin privileges from
    
    Returns:
        redirect: Redirects to the admin panel
    """
    user = db_session.query(User).filter(User.username == username).first()

    if user is None:
        flash(f"User {username} does not exist.", "error")
    
    elif not user.admin:
        flash(f"User {username} does not have admin privileges.", "warning")
    
    else:
        user.admin = False
        db_session.commit()
        flash(f"User {username} has been revoked admin privileges.", "error")
    return redirect(url_for('admin.admin_panel'))
