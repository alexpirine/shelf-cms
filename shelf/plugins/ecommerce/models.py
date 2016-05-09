# coding: utf-8

from flask.ext.babel import lazy_gettext as _
from flask.ext.security import UserMixin, RoleMixin
from sqlalchemy_defaults import Column

from shelf import LazyConfigured
from shelf.base import db

class Client(LazyConfigured):
    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship("User", backref='client')

    created_on = Column(db.DateTime, auto_now=True, label=_(u"registration date"))
    first_name = Column(db.Unicode(255), label=_(u"first name"))
    last_name = Column(db.Unicode(255), label=_(u"last name"))
    birth_date = Column(db.Date, nullable=True, label=_(u"birth date"))
    tel = Column(db.Unicode(20), nullable=True, label=_(u"telephone number"))

class Address(LazyConfigured):
    """
    Norme AFNOR XPZ 10-011 :
    on utilise 4 lignes en champ libre, suivis d'une ligne pour le code postal,
    le CEDEX et la ville, et une dernière ligne pour le pays de destination.
    Une ligne ne peut dépasser 38 caractères. Les abbréviations ne sont
    autorisées que lorsque la ligne dépasse 32 caractères. La police utilisée
    doit être Lucida Console. Les signes de pontuation ne doivent pas être
    utilisés dans la description de la localité. Les deux dernières lignes
    doivent être écrites en majuscules, sans accents ni ponctuation.
    Le pays sera toujours la dernière ligne de l'adresse, mais le
    positionnement des autres éléments dépendera du pays de destination. Par
    exemple, le code postal sera imprimé après le nom de la localité pour les
    envois au Canada.
    """

    id = Column(db.Integer, primary_key=True)
    client = db.relationship(Client, backref='addresses')
    client_id = Column(db.Integer, db.ForeignKey('client.id'))

    line1 = Column(db.Unicode(38), label=_(u"line 1"))
    line2 = Column(db.Unicode(38), nullable=True, label=_(u"line 2"))
    line3 = Column(db.Unicode(38), nullable=True, label=_(u"line 3"))
    line4 = Column(db.Unicode(38), nullable=True, label=_(u"line 4"))
    city = Column(db.Unicode(38), label=_(u"city"))
    zip_code = Column(db.Unicode(20), label=_(u"zip code"))
    country = Column(db.Unicode(38), label=_(u"country"))

    def set_lines(self, lines):
        lines = [l.strip() for l in lines.strip().split('\n')]
        self.line1 = lines[0] if len(lines) > 0 else ''
        self.line2 = lines[1] if len(lines) > 1 else ''
        self.line3 = lines[2] if len(lines) > 2 else ''
        self.line4 = lines[3] if len(lines) > 3 else ''

    def __unicode__(self):
        # ligne 5 : localité et code postal
        line5 = []
        if self.zip_code:
            line5.append(self.zip_code)
        if self.city:
            line5.append(self.city)
        line5 = u' '.join(line5)

        # ligne 6 : pays destinataire
        line6 = self.country

        # adresse complète
        address = []
        if self.line1:
            address.append(self.line1)
        if self.line2:
            address.append(self.line2)
        if self.line3:
            address.append(self.line3)
        if self.line4:
            address.append(self.line4)
        if line5:
            address.append(line5)
        if line6:
            address.append(line6)

        address1 = u'\n'.join(address[:-3])
        address2 = u'\n'.join(address[-3:]).upper()

        return u'\n'.join(filter(None, [address1, address2]))
