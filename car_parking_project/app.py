from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
from routes.slot_routes import slot_bp
from config.config import Config

app = Flask(__name__)

CORS(app)

app.config.from_object(Config)

mysql = MySQL(app)

app.register_blueprint(slot_bp)

# run the app
if __name__ == "__main__":
    app.run(debug=True)
