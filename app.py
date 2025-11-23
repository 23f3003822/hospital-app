from flask import Flask
import os
from backend.controller import register_routes
from backend.models import db, DATABASE_PATH, Admin, ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_FULL_NAME


def create_flask_app():
    flask_app = Flask(__name__, instance_relative_config=True)
    flask_app.config['SECRET_KEY'] = 'secretkey'
    # Configure SQLAlchemy to use the same database path as the models module
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.abspath(DATABASE_PATH)}"
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(flask_app)

    # Register routes (controller no longer uses Blueprints)
    register_routes(flask_app)

    # Ensure tables exist and admin user is present
    with flask_app.app_context():
        # Ensure instance folder exists so the SQLite file can be created
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        db.create_all()
        # Create admin if it doesn't exist (preserve previous behavior)
        existing = Admin.query.filter_by(email=ADMIN_EMAIL).first()
        if existing is None:
            admin = Admin(email=ADMIN_EMAIL, password=ADMIN_PASSWORD, full_name=ADMIN_FULL_NAME)
            db.session.add(admin)
            db.session.commit()

    return flask_app


if __name__ == "__main__":
    application = create_flask_app()
    application.run(debug=True)
