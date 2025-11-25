from flask import Flask
import os
from backend.controller import register_routes
from backend.models import db, DATABASE_PATH, Admin, ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_FULL_NAME


def create_flask_app():
    flask_app = Flask(__name__, instance_relative_config=True)
    flask_app.config['SECRET_KEY'] = 'secretkey'
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.abspath(DATABASE_PATH)}"
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(flask_app)

    register_routes(flask_app)

    with flask_app.app_context():
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        db.create_all()
        existing = Admin.query.filter_by(email=ADMIN_EMAIL).first()
        if existing is None:
            admin = Admin(email=ADMIN_EMAIL, password=ADMIN_PASSWORD, full_name=ADMIN_FULL_NAME)
            db.session.add(admin)
            db.session.commit()

    return flask_app


if __name__ == "__main__":
    application = create_flask_app()
    application.run(debug=True)
