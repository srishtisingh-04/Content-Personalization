from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///learnsmart.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

# Import models first to get db instance
from models import db
db.init_app(app)

jwt = JWTManager(app)
CORS(app)

# Import routes after db initialization
from routes import register_routes

# Register all routes
register_routes(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
