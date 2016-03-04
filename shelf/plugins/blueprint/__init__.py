from flask import Blueprint as FlaskBlueprint
from flask.ext.sqlalchemy import before_models_committed
from flask_security.core import current_user
from sqlalchemy.ext.declarative import declared_attr

from shelf.base import db

class BlueprintModelMixin(object):
    """
    Provides a mixin for SQLAlchemy models.
    Adds three fields:
    - date_created: creation date of the object
    - date_updated: last modification date of the object
    - modified_by: user who modified the object for the last time
    """
    date_created = db.Column(db.DateTime, default=db.func.now())
    date_updated = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    @declared_attr
    def modified_by_id(cls):
        return db.Column(db.Integer, db.ForeignKey('user.id'))

    @declared_attr
    def modified_by(cls):
        return db.relationship('User', backref='blueprints')

    def set_current_user(self):
        self.modified_by_id = current_user.id

def on_models_committed(app, changes):
    for obj, op in changes:
        if op in ['insert', 'update'] and isinstance(obj, BlueprintModelMixin):
            obj.set_current_user()

before_models_committed.connect(on_models_committed)

config = {
    "name": "Blueprint",
    "description": "Blueprint fonctionnality",
}

class Blueprint(object):
    def __init__(self):
        self.config = config

    def init_app(self, app):
        self.bp = FlaskBlueprint('blueprint', __name__)
        app.register_blueprint(self.bp)
