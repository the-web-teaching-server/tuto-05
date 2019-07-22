from flask import Flask, render_template, request, session, g, redirect, url_for
import flask_login
import sqlite3

from models.user import User, UserForLogin

DATABASE = '.data/db.sqlite'
app = Flask(__name__)
app.secret_key = 'mysecret!'

##############################################################################
#                BOILERPLATE CODE (you can essentially ignore this)          #
##############################################################################

def get_db():
    """Boilerplate code to open a database
    connection with SQLite3 and Flask.
    Note that `g` is imported from the
    `flask` module."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
    return db

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

@app.teardown_appcontext
def close_connection(exception):
    """Boilerplate code: function called each time 
    the request is over."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
##############################################################################
#                APPLICATION CODE (read from this point!)                    #
##############################################################################
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_get'

@login_manager.user_loader
def load_user(email):
    db = get_db()
    cur = db.cursor()
    return UserForLogin.getByEmail(cur, email)

  
@app.route("/")
@flask_login.login_required
def home():
  return render_template('index.html')

@app.route('/login', methods=['GET'])
def login_get():
    return render_template('login.html')

@app.route("/login", methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = request.form.get('remember_me')

    db = get_db()
    cur = db.cursor()
    
    user = UserForLogin.getByEmail(cur, email)
    if user is None or not user.check_password(password):
        return render_template(
          'login.html',
          error_msg="Authentication failed",
        )

    flask_login.login_user(user, remember=remember)
    return redirect(url_for('home'))


    
if __name__ == '__main__':
    app.run(debug=True)
