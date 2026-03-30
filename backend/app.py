import os
from flask import Flask
from flask_cors import CORS
from calculator.routes import api_bp

app = Flask(__name__)
CORS(app)

# Upload folder for Excel files
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.register_blueprint(api_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
