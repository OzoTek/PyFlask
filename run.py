from importlib import import_module
from flask import Flask, jsonify, Response
from werkzeug.exceptions import HTTPException

from app.blueprints import get_blueprints


def create_app():
    app = Flask(__name__)
    blueprints = get_blueprints()
    for bp in blueprints:
        import_module(bp.import_name)
        app.register_blueprint(bp)
    return app


app = create_app()


@app.route('/')
def default():
    return jsonify('Ok'), 200


@app.errorhandler(HTTPException)
def http_handler(exc):
    try:
        response = {'code': exc.name, 'description': exc.description}
        return jsonify(response), exc.code
    except Exception as e:
        return default_handler(e)


@app.errorhandler(Exception)
def default_handler(exc):
    print('------ Internal Server Error -----', exc)
    return jsonify({'code': 'InternalServer', 'description': str(exc)}), 500


if __name__ == '__main__':
    app.run()
