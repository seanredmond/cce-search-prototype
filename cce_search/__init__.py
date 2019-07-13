import os
from flask import Flask, send_from_directory


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        #DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        API='http://sfr-bardo-copyright-development.us-east-1.elasticbeanstalk.com',
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

    from . import api

    from . import search
    app.register_blueprint(search.bp)
    app.add_url_rule('/', endpoint='index')
    
    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return api.search()

    @app.route('/fonts/<path:path>')
    def send_fonts(path):
        return send_from_directory('fonts', path)
    
    return app


