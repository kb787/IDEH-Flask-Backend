import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_sqlalchemy import SQLAlchemy
from flask_dance.consumer import oauth_error

from modules.web_application.api.prompt_routes import prompt_bp
from modules.web_application.api.user_routes import user_bp
from modules.web_application.api.scrapping_routes import scrape_bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["secret_key"] = os.getenv("secret_key")
app.config["pg_connection_string"] = os.getenv(
    "pg_connection_string", "sqlite:///test.db"
)
db = SQLAlchemy(app)
google_blueprint_obj = make_google_blueprint(
    client_id=os.getenv("google_auth_client_id"),
    client_secret=os.getenv("google_auth_secret_key"),
    redirect_to="google_login",
)

facebook_blueprint_obj = make_facebook_blueprint(
    client_id=os.getenv("facebook_auth_client_id"),
    client_secret=os.getenv("facebook_auth_secret_key"),
    redirect_to="facebook_login",
)

app.register_blueprint(google_blueprint_obj, url_prefix="/google_login")
app.register_blueprint(facebook_blueprint_obj, url_prefix="/facebook_login")
app.register_blueprint(user_bp)
app.register_blueprint(prompt_bp)
app.register_blueprint(scrape_bp)


@oauth_error.connect_via(google_blueprint_obj)
@oauth_error.connect_via(facebook_blueprint_obj)
def oauth_error_handler(blueprint, message, response):
    print(f"OAuth error with {blueprint.name}: {message}")


@app.route("/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/plus/v1/people/me")
    assert resp.ok, resp.text
    user_info = resp.json()
    return f"You are {user_info['displayName']} on Google"


@app.route("/facebook")
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))
    resp = facebook.get("/me?fields=id,name,email")
    assert resp.ok, resp.text
    user_info = resp.json()
    return f"You are {user_info['name']} on Facebook"


def create_app():
    app = Flask(__name__)
    app.config.from_object("Config")
    app.config.from_object("AlchemyConfig")
    db.init_app(app)

    @app.errorhandler(404)
    def not_found_error(error):
        return {"message": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {"message": "Internal server error"}, 500

    return app


if __name__ == "__main__":
    app.run(debug=True)
