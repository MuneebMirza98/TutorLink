import os

import click
import sys
from flask import Flask
from flask_cas import CAS


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Setup Flask-CAS
    cas = CAS(app, url_prefix='/auth/cas')

    app.config['CAS_SERVER'] = 'https://cas1.mines-albi.fr'
    app.config['CAS_LOGIN_ROUTE'] = '/login'
    app.config['CAS_VALIDATE_ROUTE'] = '/serviceValidate'
    app.config['CAS_AFTER_LOGIN'] = 'index'
    app.config['CAS_AFTER_LOGOUT'] = 'auth.login'

    # lecture du fichier de configuration
    app.config.from_envvar('TUTORLINK_SETTINGS')
    # for key, value in app.config.items():
    #     click.echo(f"{key}: {value}")

    if app.config['TRACE']:
        click.echo("create_app:" + __name__)
        click.echo("SQLALCHEMY_DATABASE_URI is: " + app.config["SQLALCHEMY_DATABASE_URI"])

    @app.route("/hello")
    def hello():
        return "Hello, World!"

    # register the database commands
    from tutorlink import db

    db.init_app(app)

    # apply the blueprints to the app
    from tutorlink import auth, home, profile, session, data, admin_panel

    app.register_blueprint(auth.bp)
    app.register_blueprint(session.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(data.bp)
    app.register_blueprint(admin_panel.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="index")

    return app
