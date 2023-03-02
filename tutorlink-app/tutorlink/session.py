import math
from flask import Blueprint, render_template, request, flash, redirect, g, url_for

from tutorlink.db import db_session, User, Session, Module, SessionType, LecturedBy, Ue
from tutorlink.auth import login_required
from sqlalchemy import select

from datetime import datetime

bp = Blueprint("session", __name__, url_prefix="/session")

@bp.route("/list", methods=["GET"])
@login_required
def session_list():
    """
    This view allows the user to list all the sessions.
    The user can filter the sessions by type, module, UE, dates.
    TODO: add groupes and rooms filters

    The page is paginated with 12 sessions per page.
    TODO: add a filter to change the number of sessions per page

    User needs to be logged in to access this view.
    """

    error = ""

    # Get all parameters from the request
    selected_page = request.args.get('page', 1, type=int)

    type_ids = db_session.execute(select(SessionType.id)).scalars().all()
    selected_types = [type_id for type_id in request.args.getlist('type') if type_id in type_ids]

    try:
        selected_modules = [int(module_id) for module_id in request.args.getlist('module')]
    except ValueError:
        error += "Invalid type for modules. "
        selected_modules = []
    try:
        selected_ues = [int(ue_id) for ue_id in request.args.getlist('ue')]
    except ValueError:
        error += "Invalid type for UEs. "
        selected_ues = []
    selected_date_min = request.args.get('date_min', datetime.now().strftime('%Y-%m-%d'))
    selected_date_max = request.args.get('date_max', '')

    # Build the query
    order = (select(Session)
            .select_from(Session)
            .join(Module, Module.id == Session.module_id)
            .join(Ue, Ue.id == Session.ue_id)
            .join(SessionType, SessionType.id == Session.type)
            )
    if selected_date_max != '':
        try:
            selected_date_max = datetime.strptime(selected_date_max, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            error += "Invalid date format for max date. "
            selected_date_max = None
        else:
            order = order.where(Session.date_end <= selected_date_max)
    
    if selected_date_min != '':
        try:
            selected_date_min = datetime.strptime(selected_date_min, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            error += "Invalid date format for min date. "
            selected_date_min = None
        else:
            order = order.where(Session.date_start >= selected_date_min)

    if len(selected_types) > 0:
        order = order.where(SessionType.id.in_(selected_types))

    if len(selected_modules) > 0:
        order = order.where(Module.id.in_(selected_modules))
    
    if len(selected_ues) > 0:
        order = order.where(Ue.id.in_(selected_ues))

    sessions = db_session.execute(order.order_by(Session.date_start)).scalars().all()
    nb_sessions = len(sessions)
    nb_pages = math.ceil(nb_sessions / 12)
    sessions = sessions[(selected_page - 1) * 12 : selected_page * 12]
    selected_page = max(min(selected_page, nb_pages), 1)

    # Get all modules and session types for the filter
    modules = db_session.execute(select(Module)).scalars()
    ues = db_session.execute(select(Ue)).scalars()
    session_types = db_session.execute(select(SessionType)).scalars()

    if error != "":
        flash(error, "error")

    return render_template("/session/session_list.html",
                           sessions=sessions,
                           modules=modules,
                           ues=ues,
                           session_types=session_types,
                           selected_types=selected_types,
                           selected_modules=selected_modules,
                           selected_ues=selected_ues,
                           selected_date_min=selected_date_min,
                           selected_date_max=selected_date_max,
                           pages=pages_list(selected_page, nb_pages),
                           current_page=selected_page)

def pages_list(page, nb_pages):
    """Return a list of pages to display in the pagination bar.
    Take the current page and the total number of pages as arguments.

    Return a list of pages to display, with None as a placeholder for ellipsis.
    
    Example: pages_list(6, 12) -> [1, None, 4, 5, 6, 7, 8, None, 12]"""

    if page > 5:
        beg = list(range(1, 2)) + [None] + list(range(page-2, page))
    else:
        beg = list(range(1, page))
    if page < nb_pages - 4:
        end = list(range(page+1, page+3)) + [None] + list(range(nb_pages, nb_pages+1))
    else:
        end = list(range(page+1, nb_pages+1))
    pages = beg + [page] + end
    return pages

@bp.route("/register", methods=["POST"])
@login_required
def session_register():
    """
    This route allows the user to register to a session.
    The user can register to a session if he is not already registered to it.
    The user can register other users to a session if he is an admin or if he manages the module of the session.

    User needs to be logged in to access this route.
    """
    if request.method == "POST":

        session_id = request.form.get("session_id", "")
        username = request.form.get("username", g.user.username)

        error = ""

        try:
            session_id = int(session_id)
        except ValueError:
            error += "Invalid session id. "
        else:
            session = db_session.execute(
                select(Session)
                .where(Session.id == session_id)
                ).scalars().first()

            if session is None:
                error += f"The session with id {session_id} does not exist. "
        
        user = db_session.execute(
            select(User)
            .where(User.username == username)
            ).scalars().first()

        if user is None:
            error += "Invalid username. "

        if (error == ""
            and user.username != g.user.username
            and g.user.admin == False
            and session.module not in g.user.managed_modules):

            error += "You are not allowed to register other users. "

        if (error == ""
            and db_session.execute(
                select(LecturedBy)
                .where(LecturedBy.session_id == session_id)
                .where(LecturedBy.user_username == username)
                ).scalars().first() is not None):

            error += f"{username} is already registered for this session. "

        if error == "":
            session_lecturer = LecturedBy(session_id=session_id,
                                        user_username=username,
                                        synapse=False)
            db_session.add(session_lecturer)
            db_session.commit()
            if user.username == g.user.username:
                flash("You have successfully registered for the session.", 'success')
            else:
                flash(f"{username} has successfully been registered for the session.", 'success')
        else:
            flash(error, 'error')
    
    if request.referrer is None:
        return redirect(url_for('index'))

    return redirect(request.referrer)


@bp.route("/unregister", methods=["POST"])
@login_required
def session_unregister():
    """
    This route allows the user to unregister from a session.
    The user can unregister from a session if he is registered to it.
    The user can unregister other users from a session if he is an
        admin or if he manages the module of the session.

    User needs to be logged in to access this route.
    """
    if request.method == "POST":

        session_id = request.form.get("session_id", "")
        username = request.form.get("username", g.user.username)

        error = ""

        try:
            session_id = int(session_id)
        except ValueError:
            error += "Invalid session id. "
        else:
            session = db_session.execute(
                select(Session)
                .where(Session.id == session_id)
                ).scalars().first()
            
            if session is None:
                error += f"The session with id {session_id} does not exist. "
        
        user = db_session.execute(
            select(User)
            .where(User.username == username)
            ).scalars().first()
        
        if user is None:
            error += "Invalid username. "

        if (user.username != g.user.username
            and g.user.admin == False
            and session.module not in g.user.managed_modules):

            error += "You are not allowed to unregister other users. "

        if (error == "" 
            and db_session.execute(
                select(LecturedBy)
                .where(LecturedBy.session_id == session_id)
                .where(LecturedBy.user_username == username)
                ).scalars().first() is None):

                error += f"{username} is not registered for this session. "

        if error == "":
            session_lecturer = db_session.execute(
                select(LecturedBy)
                .where(LecturedBy.session_id == session_id)
                .where(LecturedBy.user_username == username)
                ).scalars().first()
            
            db_session.delete(session_lecturer)
            db_session.commit()
            if user.username == g.user.username:
                flash("You have successfully unregistered from the session.", 'success')
            else:
                flash(f"{username} has successfully been unregistered from the session.", 'success')
        else:
            flash(error, 'error')
    
    if request.referrer is None:
        return redirect(url_for('index'))

    return redirect(request.referrer)
