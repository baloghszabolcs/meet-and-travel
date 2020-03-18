import time
from flask import Flask
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SECRET_KEY'] = 'eaefd390b311802881de38f02ffe59b7'
bcrypt = Bcrypt(app)

from flaskapp import routes