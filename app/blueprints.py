import os

from flask import Blueprint

views = dict()


def get_view_names():
    files = filter(lambda name: '__' not in name,
                   next(os.walk('app/views'))[2])
    return set(map(lambda view: view.split('.py')[0], files))


def get_blueprints():
    blueprints = list(map(lambda view: Blueprint(
        view,
        f'app.views.{view}',
        url_prefix=f'/{view}'), get_view_names()))
    for bp in blueprints:
        views[bp.name] = bp
    return blueprints
