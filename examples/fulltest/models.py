# coding: utf-8

from flask.ext.babel import lazy_gettext as _
from shelf import LazyConfigured
from shelf import ModelForm
from shelf.base import db
from shelf.plugins.i18n import LocalizedModelMixin
from shelf.plugins.library import PictureModelMixin, RemoteFileModelMixin
from shelf.plugins.page import PageModelMixin
from shelf.plugins.preview import PreviewableModelMixin
from shelf.plugins.workflow import WorkflowModelMixin, WORKFLOW_STATES
from sqlalchemy_defaults import Column

class LocalizedString(LazyConfigured, LocalizedModelMixin):
    __tablename__ = "localized_string"
    id = Column(db.Integer, primary_key=True)
    value = Column(db.Unicode(255), label=_(u"value"))
    lang = Column(db.String(2), label=_(u"language code"))
    translations = db.relationship('LocalizedString', lazy="joined", backref=db.backref("parent", remote_side=[id]))
    parent_id = Column(db.Integer, db.ForeignKey('localized_string.id'))

    def __unicode__(self):
        return self.value


class LocalizedText(LazyConfigured, LocalizedModelMixin):
    __tablename__ = "localized_text"
    id = Column(db.Integer, primary_key=True)
    value = Column(db.UnicodeText, label=_(u"value"))
    lang = Column(db.String(2), label=_(u"language code"))
    translations = db.relationship('LocalizedText', lazy="joined", backref=db.backref("parent", remote_side=[id]))
    parent_id = Column(db.Integer, db.ForeignKey('localized_text.id'))


class Picture(LazyConfigured, PictureModelMixin):
    id = Column(db.Integer, primary_key=True)


class RemoteFile(LazyConfigured, RemoteFileModelMixin):
    __tablename__ = "remote_file"
    id = Column(db.Integer, primary_key=True)
    path = Column(db.Unicode(255), label=_(u"path"))

    def __unicode__(self):
        return self.path


#classes de l'application

post_tags = db.Table('post_tags',
    Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    Column('post_id', db.Integer, db.ForeignKey('post.id'))
)


class Tag(LazyConfigured):
    id = Column(db.Integer(), primary_key=True)

    name_id = Column(db.Integer, db.ForeignKey('localized_string.id'))
    name = db.relationship('LocalizedString', foreign_keys=(name_id,))

    posts = db.relationship(
        "Post", secondary=post_tags,
        backref=db.backref('tags', lazy='joined'))

    def __unicode__(self):
        return unicode(self.name)


class Post(LazyConfigured, WorkflowModelMixin, PreviewableModelMixin):
    id = Column(db.Integer, primary_key=True)
    created_on = Column(db.DateTime, default=db.func.now(), label=_(u"created on"))

    mode = Column(db.Enum("text", "video"), default="text")

    publication_date = Column(db.Date, label=_(u"desired date of publication"))
    state = Column(db.Enum(*WORKFLOW_STATES))

    title_id = Column(db.Integer, db.ForeignKey('localized_string.id'))
    title = db.relationship('LocalizedString', foreign_keys=(title_id,))

    abstract_id = Column(db.Integer, db.ForeignKey('localized_text.id'))
    abstract = db.relationship('LocalizedText', foreign_keys=(abstract_id,))

    text_id = Column(db.Integer, db.ForeignKey('localized_text.id'))
    text = db.relationship('LocalizedText', foreign_keys=(text_id,))

    picture_id = Column(db.Integer, db.ForeignKey('picture.id'))
    picture = db.relationship("Picture")

    attachment_id = Column(db.Integer, db.ForeignKey('remote_file.id'))
    attachment = db.relationship("RemoteFile")

    video_link = Column(db.Unicode(50), nullable=True, label=_(u"video link"))


class Page(LazyConfigured, PreviewableModelMixin, PageModelMixin):
    id = Column(db.Integer, primary_key=True)
    name = Column(db.Unicode(50), label=_(u"name"))
    l_title_id = Column(db.Integer, db.ForeignKey('localized_string.id'))
    l_title = db.relationship('LocalizedString', foreign_keys=(l_title_id,))

    l_description_id = Column(db.Integer, db.ForeignKey('localized_string.id'))
    l_description = db.relationship('LocalizedString', foreign_keys=(l_description_id,))

    __mapper_args__ = {
        'polymorphic_on': name,
        'polymorphic_identity': 'page'
    }


class IndexPage(Page):
    intro_id = Column(db.Integer, db.ForeignKey('localized_string.id'))
    intro = db.relationship('LocalizedString', foreign_keys=(intro_id,))
    __mapper_args__ = {
        'polymorphic_identity': u'index'
    }


class ContactPage(Page):
    text_id = Column(db.Integer, db.ForeignKey('localized_text.id'))
    text = db.relationship('LocalizedText', foreign_keys=(text_id,))

    __mapper_args__ = {
        'polymorphic_identity': u'contact'
    }
