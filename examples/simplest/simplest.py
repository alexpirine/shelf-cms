from flask import Flask

from shelf import Shelf
from shelf.base import db
from shelf.security.models import User, Role
from shelf.admin.view import SQLAModelView

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///simplest.db'
app.config['SECRET_KEY'] = 'notasecret'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150))
    content = db.Column(db.Text)


shlf = Shelf(app)
shlf.init_db(db)
shlf.init_admin()
shlf.init_security(User, Role)
shlf.admin.add_view(SQLAModelView(Post, db.session))

app.run('0.0.0.0')
