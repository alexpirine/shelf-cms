from flask_babel import lazy_gettext as _
from shelf import LazyConfigured
from shelf import db
from shelf.plugins.library import PictureModelMixin
from shelf.plugins.workflow import WorkflowModelMixin, WORKFLOW_STATES
from sqlalchemy_defaults import Column

class Picture(LazyConfigured, PictureModelMixin):
    id = Column(db.Integer, primary_key=True)

class Post(LazyConfigured, WorkflowModelMixin):
    id = Column(db.Integer, primary_key=True)
    picture_id = Column(db.Integer, db.ForeignKey('picture.id'), nullable=True)
    picture = db.relationship("Picture")
    title = Column(db.Unicode(150), label=_(u"title"))
    content = Column(db.UnicodeText, label=_(u"content"))
    state = Column(db.Enum(*WORKFLOW_STATES), label=_(u"state"))
