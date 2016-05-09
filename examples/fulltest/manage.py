#!/usr/bin/env python
# coding: utf-8

import datetime
import random

from flask import current_app
from flask.ext.script import Manager
from flask_security.utils import encrypt_password

from jinja2.utils import generate_lorem_ipsum

from shelf import manager as shelf_manager
from shelf.base import db
from shelf.security.models import User, Role

from app import create_app
from models import LocalizedString, LocalizedText, Post, Tag

manager = Manager(create_app)
manager.add_command('shelf', shelf_manager)


@manager.command
def test():
    print("Hello world!")


@manager.command
def create_tags():
    names = [u"news", u"article", u"interview", u"test", u"review", u"témoignage"]
    for name in names:
        tag = Tag()
        name = LocalizedString(value=name, lang=u"fr")
        tag.name = name
        db.session.add(tag)
        db.session.commit()


@manager.command
def create_posts():
    names = [u"news", u"article", u"interview", u"test", u"review", u"témoignage"]
    titles = [
        u"voici un super post", u"un article trop cool", u"une bonne idée",
        u"nouvel article", u"un petit article", u"regardez ca !", u"petit retour"]

    for index in range(12):
        post = Post(mode="text")
        title = random.choice(titles)
        title = LocalizedString(value=title, lang=u"fr")
        post.title = title
        post.state = "published"

        post.publication_date = datetime.datetime.now()

        text = generate_lorem_ipsum()
        text = LocalizedText(value=text, lang=u"fr")
        post.text = text

        abstract = generate_lorem_ipsum(n=1, max=60)
        abstract = LocalizedText(value=abstract, lang=u"fr")
        post.abstract = abstract

        db.session.add(post)
        db.session.commit()

        tags_count = Tag.query.count()
        print "tags_count : ", tags_count
        tag_id = random.randint(1,tags_count)
        print "tag_id : ", tag_id
        tag = Tag.query.get(tag_id)

        tag.posts.append(post)
        db.session.commit()

        print post
        print tag


@manager.command
def create_admin():
    user_datastore = current_app.extensions['security'].datastore

    admin = User.query.join(User.roles).filter(Role.name == u'superadmin').first()
    if not admin:
        admin_email = u'admin@localhost'
        admin_pwd = u'admin31!'
        admin = User(
            email=admin_email,
            active=True,
        )
        for role_name in [u'superadmin', u'reviewer', u'publisher']:
            role = user_datastore.find_role(role_name)
            user_datastore.add_role_to_user(admin, role)
        admin.password = encrypt_password(admin_pwd)
        db.session.add(admin)
        db.session.commit()

        print("Admin user %(email)s (password: %(pwd)s) created successfully." % {
            'email': admin.email,
            'pwd': admin_pwd,
        })
    else:
        print("Admin user %(email)s already exists!" % {
            'email': admin.email,
        })

if __name__ == '__main__':
    manager.run()
