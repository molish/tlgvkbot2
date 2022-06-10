import threading
import traceback

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# init SQLAlchemy so we can use it later in our models

db = SQLAlchemy()
tg_thread = threading.Thread()
vk_thread = threading.Thread()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from users import users as users_blueprint
    app.register_blueprint(users_blueprint)

    from groups import groups as groups_blueprint
    app.register_blueprint(groups_blueprint)

    from messages import messages as messages_blueprint
    app.register_blueprint(messages_blueprint)

    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from telegbot import listen_tg_bot
    from app import tg_thread

    try:
        if not tg_thread.is_alive():
            tg_thread = threading.Thread(target=listen_tg_bot, daemon=True)
            tg_thread.start()
    except BaseException as e:
        print('exception:', traceback.format_exc())
        tg_thread.stop()

    print('tg daemon started')

    from vkontaktebot import start_vkbot
    from app import vk_thread

    try:
        if not vk_thread.is_alive():
            vk_thread = threading.Thread(target=start_vkbot, daemon=True)
            vk_thread.start()
            print('vk daemon started')
    except BaseException as e:
        print('exception:', traceback.format_exc())
        vk_thread.stop()

    return app


def init_db():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    return app


