from flask import Flask
from flask_bcrypt import Bcrypt
from datetime import timedelta


app = Flask(__name__)
app.config['SECRET_KEY'] = 'eaefd390b311802881de38f02ffe59b7'
app.permanent_session_lifetime = timedelta(days=4)
bcrypt = Bcrypt(app)

from flaskapp import routes