from flask import Blueprint, render_template, g
from sqlalchemy import select

import datetime

from tutorlink.auth import login_required
from tutorlink.db import db_session, Session, LecturedBy


bp = Blueprint("home", __name__)


@bp.route("/")
@login_required
def index():
    """
    Show the main page of the application
    
    This page shows the list of urgent sessions (sessions without lecturers)
    and the total number of hours the user has lectured.

    If the user is a "doctorant", the page will show the total number of hours/64 with a progress bar.
    Else, the page will show the total number of hours.
    """

    # Fetch the list of urgent sessions i.e. sessions without lecturers
    urgent_sessions = db_session.execute(
        select(Session)
        .join(LecturedBy, Session.id == LecturedBy.session_id, isouter=True)
        .where(LecturedBy.user_username == None)
        .where(Session.date_start >= datetime.datetime.now())
        .order_by(Session.date_start)
        .limit(12)
        ).scalars().all()

    all_user_sessions = db_session.execute(
        select(Session)
        .join(LecturedBy, Session.id == LecturedBy.session_id)
        .where(LecturedBy.user_username == g.user.username)
        ).scalars()

    user_next_sessions = db_session.execute(
        select(Session)
        .join(LecturedBy, Session.id == LecturedBy.session_id)
        .where(LecturedBy.user_username == g.user.username)
        .where(Session.date_start >= datetime.datetime.now())
        .order_by(Session.date_start)
        .limit(12)
        ).scalars().all()

    total_duration = sum([session.duration for session in all_user_sessions], datetime.timedelta())
    
    return render_template("home/index.html",
                            urgent_sessions=urgent_sessions,
                            user_next_sessions=user_next_sessions,
                            total_duration=round(total_duration.total_seconds()/3600, 2))
