from flask import Flask
from backend.controller import main_blueprint

def create_flask_app():
    flask_app = Flask(__name__, instance_relative_config=True)
    flask_app.config['SECRET_KEY'] = 'secretsample'
    flask_app.register_blueprint(main_blueprint)
    return flask_app

if __name__ == "__main__":
    application = create_flask_app()
    application.run(debug=True)
