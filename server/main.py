import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from classes import *

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@hostname/database'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)


@app.cli.command('initdb')
def initdb():
    db.create_all()


class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    inPlay = db.Column(db.PickleType)
    discard = db.Column(db.PickleType)
    deck = db.Column(db.PickleType)
    turn = db.Column(db.SmallInteger)
    players = db.Column(db.PickleType)
    hands = db.Column(db.PickleType)
    misfires = db.Column(db.SmallInteger)
    hints = db.Column(db.SmallInteger)
    rainbowIsColour = db.Column(db.Boolean)
    perfectOrBust = db.Column(db.Boolean)

    def __repr__(self):
        return '<Game %r>' % self.id


# Routes

# @app.route('/game/<int:gameId>')
# def game(gameId):
#     return '<h1>Hello World!</h1>'

if __name__ == '__main__':
    app.run(debug=True)