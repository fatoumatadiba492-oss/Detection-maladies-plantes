from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from model_logic import run_inference
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Créer une instance de Flask
app = Flask(__name__)

# CORS restreint aux origines nécessaires
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Changé pour /api/*

# Configuration sécurisée
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Mo max

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Définir le répertoire pour les uploads d'images
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return jsonify({
        'status': 'ok',
        'message': 'Le backend de détection est opérationnel !',
        'endpoints': {
            '/api/predict': 'POST - Pour faire une prédiction',
            '/health': 'GET - Pour vérifier l\'état du service'
        }
    })


@app.route('/health')
def health():
    """Endpoint de santé pour les orchestrators (Kubernetes, etc.)"""
    return jsonify({'status': 'healthy'}), 200


# Route pour la prédiction avec préfixe /api
@app.route('/api/predict', methods=['POST'])  # Changé pour /api/predict
def predict():
    img_path = None
    try:
        # Vérifier si une image a été fournie
        if 'image' not in request.files:
            return jsonify({'error': 'Aucune image fournie'}), 400

        file = request.files['image']

        # Vérifier si le fichier est une image
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier d\'image vide'}), 400

        # Vérifier l'extension du fichier
        if not allowed_file(file.filename):
            return jsonify({'error': 'Type de fichier non autorisé. Formats acceptés : png, jpg, jpeg, gif, webp'}), 400

        # Sécuriser le nom de fichier
        filename = secure_filename(file.filename)
        img_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(img_path)

        # Appeler la fonction de détection
        results = run_inference(img_path)

        # Retourner les résultats
        return jsonify(results)

    except Exception as e:
        print(f"Erreur lors de la prédiction : {str(e)}")
        return jsonify({'error': 'Une erreur interne est survenue lors du traitement de l\'image'}), 500

    finally:
        # Nettoyer le fichier uploadé
        if img_path and os.path.exists(img_path):
            try:
                os.remove(img_path)
            except OSError:
                pass


# Gestionnaire d'erreur 404 personnalisé
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Route non trouvée',
        'message': 'Vérifiez l\'URL. Endpoints disponibles : /, /health, /api/predict (POST)'
    }), 404


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'Fichier trop volumineux. Taille maximale : 16 Mo'}), 413


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Erreur interne du serveur'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)