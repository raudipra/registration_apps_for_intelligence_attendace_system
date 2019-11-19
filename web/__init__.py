import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        #SECRET_KEY='dev', TODO make
        #DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        DEFAULT_TRIGGER_MODE='trigger'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import (
        personnel, api_endpoints, user_config
    )
    app.register_blueprint(personnel.bp)
    app.register_blueprint(api_endpoints.bp)
    app.register_blueprint(user_config.bp)

    return app
