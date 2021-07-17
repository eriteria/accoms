from flask import Flask, Blueprint

from accoms.views import site
from accoms.extensions import db, migrate, login_manager
from accoms.commands import create_tables


def create_app(config_file="settings.py"):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)

    with app.app_context():
        db.init_app(app)
        migrate.init_app(app, db, render_as_batch=True)
        login_manager.init_app(app)

    app.register_blueprint(site)

    app.cli.add_command(create_tables)

    return app