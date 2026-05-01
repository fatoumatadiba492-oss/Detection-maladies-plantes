from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import requests as http_requests
import tempfile
from werkzeug.utils import secure_filename
from model_logic import run_inference
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── Configuration uploads ──────────────────────────────────────────────────────
UPLOAD_FOLDER       = 'uploads/'
ALLOWED_EXTENSIONS  = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH  = 16 * 1024 * 1024   # 16 Mo

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Configuration ESP32 ────────────────────────────────────────────────────────
ESP32_DEFAULT_IP      = os.getenv('ESP32_IP', '')
ESP32_CONNECT_TIMEOUT = 3     # secondes pour le ping
ESP32_CAPTURE_TIMEOUT = 8     # secondes pour capturer une frame


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ══════════════════════════════════════════════════════════════════════════════
# ── ROUTE ACCUEIL ─────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/')
def home():
    return jsonify({
        'status':    'ok',
        'message':   'PlantAI Backend opérationnel',
        'endpoints': {
            '/api/predict':      'POST  — Analyser une image (fichier)',
            '/api/esp32/status': 'GET   — Vérifier la connexion ESP32-CAM',
            '/api/esp32/capture':'POST  — Capturer depuis ESP32-CAM et analyser',
            '/api/esp32/stream_url': 'GET — URL du flux MJPEG ESP32',
            '/health':           'GET   — Santé du service',
        },
    })


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200


# ══════════════════════════════════════════════════════════════════════════════
# ── PRÉDICTION SUR IMAGE UPLOADÉE ─────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/predict', methods=['POST'])
def predict():
    img_path = None
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Aucune image fournie'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': 'Format non autorisé. Acceptés : png, jpg, jpeg, gif, webp'}), 400

        filename = secure_filename(file.filename)
        img_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(img_path)

        result = run_inference(img_path)
        return jsonify(result)

    except Exception as e:
        print(f"Erreur prédiction : {e}")
        return jsonify({'error': 'Erreur interne lors du traitement de l\'image'}), 500

    finally:
        if img_path and os.path.exists(img_path):
            try:
                os.remove(img_path)
            except OSError:
                pass


# ══════════════════════════════════════════════════════════════════════════════
# ── ESP32-CAM : STATUT DE CONNEXION ───────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/esp32/status', methods=['GET'])
def esp32_status():
    """
    Vérifie si l'ESP32-CAM est accessible sur le réseau.
    Paramètre : ?ip=192.168.x.x
    """
    ip = request.args.get('ip', ESP32_DEFAULT_IP).strip()

    if not ip:
        return jsonify({
            'connected': False,
            'ip':        None,
            'message':   'Adresse IP ESP32 non configurée',
        })

    capture_url = f'http://{ip}/capture'
    try:
        r = http_requests.get(capture_url, timeout=ESP32_CONNECT_TIMEOUT, stream=True)
        r.close()
        connected = r.status_code == 200
        return jsonify({
            'connected':  connected,
            'ip':         ip,
            'stream_url': f'http://{ip}:81/stream',
            'capture_url': capture_url,
            'message':    'ESP32-CAM connectée et opérationnelle' if connected else f'HTTP {r.status_code}',
        })

    except http_requests.exceptions.ConnectTimeout:
        return jsonify({'connected': False, 'ip': ip, 'message': 'Hôte injoignable (timeout)'})
    except http_requests.exceptions.ConnectionError:
        return jsonify({'connected': False, 'ip': ip, 'message': 'Connexion refusée — vérifiez l\'IP et le WiFi'})
    except Exception as e:
        return jsonify({'connected': False, 'ip': ip, 'message': str(e)})


# ══════════════════════════════════════════════════════════════════════════════
# ── ESP32-CAM : CAPTURER ET ANALYSER ──────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/esp32/capture', methods=['POST'])
def esp32_capture():
    """
    Capture une frame depuis l'ESP32-CAM et lance l'inférence.
    Body JSON : {"ip": "192.168.x.x"}
    """
    data = request.get_json(silent=True) or {}
    ip   = data.get('ip', ESP32_DEFAULT_IP).strip()

    if not ip:
        return jsonify({'error': 'Adresse IP ESP32 non fournie'}), 400

    capture_url = f'http://{ip}/capture'
    tmp_path    = None

    try:
        # 1. Récupérer la frame JPEG depuis l'ESP32
        r = http_requests.get(capture_url, timeout=ESP32_CAPTURE_TIMEOUT)
        r.raise_for_status()

        if 'image' not in r.headers.get('Content-Type', ''):
            return jsonify({'error': "L'ESP32 n'a pas renvoyé une image valide"}), 502

        # 2. Sauvegarder temporairement
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False, dir=UPLOAD_FOLDER) as f:
            f.write(r.content)
            tmp_path = f.name

        # 3. Lancer l'inférence
        result = run_inference(tmp_path)
        result['source'] = 'esp32'
        result['esp32_ip'] = ip
        return jsonify(result)

    except http_requests.exceptions.ConnectTimeout:
        return jsonify({'error': f'ESP32 injoignable à {ip} (timeout)'}), 504
    except http_requests.exceptions.ConnectionError:
        return jsonify({'error': f'Impossible de se connecter à {ip} — vérifiez l\'IP'}), 503
    except http_requests.exceptions.HTTPError as e:
        return jsonify({'error': f'ESP32 erreur HTTP : {e}'}), 502
    except Exception as e:
        print(f"Erreur ESP32 capture : {e}")
        return jsonify({'error': f'Erreur interne : {str(e)}'}), 500

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


# ══════════════════════════════════════════════════════════════════════════════
# ── ESP32-CAM : PROXY DU FLUX MJPEG ───────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/esp32/stream')
def esp32_stream_proxy():
    """
    Proxy du flux MJPEG de l'ESP32 pour éviter les problèmes CORS.
    Paramètre : ?ip=192.168.x.x
    """
    ip = request.args.get('ip', ESP32_DEFAULT_IP).strip()
    if not ip:
        return jsonify({'error': 'IP manquante'}), 400

    stream_url = f'http://{ip}:81/stream'
    try:
        esp32_response = http_requests.get(stream_url, stream=True, timeout=10)

        def generate():
            try:
                for chunk in esp32_response.iter_content(chunk_size=4096):
                    yield chunk
            except Exception:
                pass

        return Response(
            generate(),
            content_type=esp32_response.headers.get('Content-Type', 'multipart/x-mixed-replace'),
            status=200,
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 503


# ══════════════════════════════════════════════════════════════════════════════
# ── GESTIONNAIRES D'ERREURS ────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.errorhandler(404)
def not_found(_):
    return jsonify({'error': 'Route introuvable', 'endpoints': ['/', '/health', '/api/predict', '/api/esp32/status', '/api/esp32/capture']}), 404

@app.errorhandler(413)
def too_large(_):
    return jsonify({'error': 'Fichier trop volumineux. Maximum : 16 Mo'}), 413

@app.errorhandler(500)
def internal_error(_):
    return jsonify({'error': 'Erreur interne du serveur'}), 500


# ══════════════════════════════════════════════════════════════════════════════
# ── DÉMARRAGE ─────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    port  = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    print(f"\n🌿  PlantAI Backend démarré sur : http://localhost:{port}")
    print(f"📡  ESP32 par défaut          : {ESP32_DEFAULT_IP or 'non configuré'}")
    print(f"🧠  Modèle                    : HuggingFace ViT / EfficientNet-B4\n")
    app.run(host='0.0.0.0', port=port, debug=debug)
