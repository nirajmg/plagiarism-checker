from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
import psycopg2
from flask_login import LoginManager

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


def create_app():
    global app
    app = Flask(__name__)

    url = 'postgresql://root:root@localhost:5432/mydb'
    app.config['SECRET_KEY'] = 'secret-key-goes-here'

    app.config['SQLALCHEMY_DATABASE_URI'] = url

    db.init_app(app)
    try:
        conn = psycopg2.connect(
            database="mydb", user="root", password="root", host="localhost", port="5432")
    except:
        print("I am unable to connect to the database")

    cur = conn.cursor()
    try:
        cur.execute(
            "CREATE TABLE Users (id serial PRIMARY KEY, name varchar, email varchar, password varchar);")
    except:
        print("I can't drop our test database!")

    conn.commit()  # <--- makes sure the change is shown in the database
    conn.close()
    cur.close()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import Users

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return Users.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
