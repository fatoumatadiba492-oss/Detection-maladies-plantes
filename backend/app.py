from flask import Flask, request, jsonify, Response, g
from flask_cors import CORS
import os
import sys
import requests as http_requests

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
import tempfile
from werkzeug.utils import secure_filename
from model_logic import run_inference
from dotenv import load_dotenv
from datetime import datetime, timezone

from auth import (
    login_required, role_required,
    hash_password, verify_password, generate_token,
)

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
ESP32_CONNECT_TIMEOUT = 8
ESP32_CAPTURE_TIMEOUT = 8

# ══════════════════════════════════════════════════════════════════════════════
# ── MONGODB ───────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
_mongo_col = None

def get_history_col():
    """Retourne la collection MongoDB (lazy init, graceful fallback)."""
    global _mongo_col
    if _mongo_col is not None:
        return _mongo_col
    try:
        from pymongo import MongoClient, DESCENDING
        uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/plantai')
        client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        client.server_info()          # lève une exception si MongoDB est absent
        db  = client['plantai']
        col = db['predictions']
        col.create_index([('date', DESCENDING)])
        _mongo_col = col
        print("✅  MongoDB connecté →", uri)
    except Exception as e:
        print(f"⚠️   MongoDB non disponible : {e} — l'historique restera en mémoire côté client")
        _mongo_col = None
    return _mongo_col


def _save_prediction(entry: dict):
    """Insère un enregistrement dans MongoDB. Silencieux si DB indisponible."""
    col = get_history_col()
    if col is None:
        return None
    try:
        result = col.insert_one(entry)
        return str(result.inserted_id)
    except Exception as e:
        print(f"⚠️  Erreur sauvegarde MongoDB : {e}")
        return None


def _serialize(doc: dict) -> dict:
    """Convertit ObjectId → str et datetime → ISO string pour jsonify."""
    from bson import ObjectId
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        elif isinstance(v, list):
            out[k] = [_serialize(i) if isinstance(i, dict) else i for i in v]
        elif isinstance(v, dict):
            out[k] = _serialize(v)
        else:
            out[k] = v
    return out


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ══════════════════════════════════════════════════════════════════════════════
# ── MONGODB : COLLECTIONS UTILISATEURS & CAPTEURS ─────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
_users_col   = None
_sensors_col = None


def get_users_col():
    """Retourne la collection MongoDB 'users' (lazy init, index unique sur email)."""
    global _users_col
    if _users_col is not None:
        return _users_col
    col = get_history_col()  # déclenche l'init de _mongo_col / vérifie la connexion
    if col is None:
        return None
    db = col.database
    _users_col = db['users']
    _users_col.create_index('email', unique=True)
    return _users_col


def get_sensors_col():
    """Retourne la collection MongoDB 'sensors_data' (lazy init)."""
    global _sensors_col
    if _sensors_col is not None:
        return _sensors_col
    col = get_history_col()
    if col is None:
        return None
    db = col.database
    _sensors_col = db['sensors_data']
    _sensors_col.create_index([('dateMesure', -1)])
    return _sensors_col


def _user_to_dict(doc: dict) -> dict:
    """Sérialise un document utilisateur pour l'API — ne renvoie jamais motDePasse."""
    out = {
        'idUtilisateur': str(doc['_id']),
        'nom':           doc.get('nom'),
        'prenom':        doc.get('prenom'),
        'email':         doc.get('email'),
        'role':          doc.get('role'),
    }
    if doc.get('role') == 'maraicher':
        out['exploitation'] = doc.get('exploitation')
    return out


# ══════════════════════════════════════════════════════════════════════════════
# ── ROUTE ACCUEIL ─────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/')
def home():
    return jsonify({
        'status':    'ok',
        'message':   'PlantAI Backend opérationnel',
        'endpoints': {
            '/auth/login':          'POST  — Connexion (email + motDePasse) → token + rôle',
            '/auth/logout':         'POST  — Déconnexion (authentifié)',
            '/api/predict':         'POST  — Analyser une image (fichier)',
            '/api/predict/cnn':     'POST  — Analyser une image via le CNN Keras (ia/model.py)',
            '/api/esp32/status':    'GET   — Vérifier la connexion ESP32-CAM',
            '/api/esp32/capture':   'POST  — Capturer depuis ESP32-CAM et analyser',
            '/api/esp32/stream_url':'GET   — URL du flux MJPEG ESP32',
            '/api/history':         'GET/POST/DELETE — Historique des analyses (legacy, non authentifié)',
            '/history':             'GET   — Historique de l\'utilisateur connecté (authentifié)',
            '/users':               'GET/POST — Gestion des utilisateurs (administrateur)',
            '/users/<id>':          'PUT/DELETE — Modifier/supprimer un utilisateur (administrateur)',
            '/sensors/data':        'GET/POST — Données capteurs (température/humidité)',
            '/sensors/data/simulate':'POST — Simule l\'envoi de données capteur (test)',
            '/health':              'GET   — Santé du service',
        },
    })


@app.route('/health')
def health():
    db_ok = get_history_col() is not None
    return jsonify({'status': 'healthy', 'mongodb': 'connected' if db_ok else 'unavailable'}), 200


# ══════════════════════════════════════════════════════════════════════════════
# ── AUTHENTIFICATION (diagramme de séquence "Connexion") ─────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email        = (data.get('email') or '').strip().lower()
    mot_de_passe = data.get('motDePasse') or data.get('password') or ''

    if not email or not mot_de_passe:
        return jsonify({'error': 'Email et mot de passe requis'}), 400

    col = get_users_col()
    if col is None:
        return jsonify({'error': 'Base de données indisponible'}), 503

    user = col.find_one({'email': email})
    if user is None or not verify_password(mot_de_passe, user['motDePasse']):
        return jsonify({'error': 'Identifiants invalides'}), 401

    user_out = _user_to_dict(user)
    token = generate_token({
        'idUtilisateur': user_out['idUtilisateur'],
        'email':         user_out['email'],
        'role':          user_out['role'],
    })

    return jsonify({'token': token, **user_out})


@app.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    # JWT stateless : la déconnexion est gérée côté client (suppression du token).
    return jsonify({'ok': True, 'message': 'Déconnecté'})


# ══════════════════════════════════════════════════════════════════════════════
# ── PRÉDICTION SUR IMAGE UPLOADÉE ─────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/predict', methods=['POST'])
@role_required('maraicher')
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

        # ── Auto-sauvegarde MongoDB ──────────────────────────────────────────
        entry = {
            **result,
            'image':   filename,
            'source':  'api',
            'date':    datetime.now(timezone.utc),
            'userId':  g.current_user['idUtilisateur'],
        }
        db_id = _save_prediction(entry)
        if db_id:
            result['dbId'] = db_id

        return jsonify(result)

    except Exception as e:
        print(f"Erreur prédiction : {e}")
        return jsonify({'error': "Erreur interne lors du traitement de l'image"}), 500

    finally:
        if img_path and os.path.exists(img_path):
            try:
                os.remove(img_path)
            except OSError:
                pass


# ══════════════════════════════════════════════════════════════════════════════
# ── PRÉDICTION VIA LE CNN KERAS (ia/model.py) ─────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
def _predict_cnn(img_path):
    """Import paresseux du modèle Keras : ne bloque pas le démarrage de Flask
    si TensorFlow n'est pas installé dans l'environnement backend."""
    ia_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ia')
    if ia_dir not in sys.path:
        sys.path.insert(0, ia_dir)
    from model import predict_image
    return predict_image(img_path)


@app.route('/api/predict/cnn', methods=['POST'])
@role_required('maraicher')
def predict_cnn():
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

        result = _predict_cnn(img_path)

        # ── Auto-sauvegarde MongoDB ──────────────────────────────────────────
        entry = {
            **result,
            'image':   filename,
            'source':  'cnn_keras',
            'date':    datetime.now(timezone.utc),
            'userId':  g.current_user['idUtilisateur'],
        }
        db_id = _save_prediction(entry)
        if db_id:
            result['dbId'] = db_id

        return jsonify(result)

    except ModuleNotFoundError:
        return jsonify({'error': "Modèle CNN indisponible — installez ia/requirements.txt (tensorflow)"}), 503
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        print(f"Erreur prédiction CNN : {e}")
        return jsonify({'error': "Erreur interne lors du traitement de l'image"}), 500

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
            'connected':   connected,
            'ip':          ip,
            'stream_url':  f'http://{ip}:81/stream',
            'capture_url': capture_url,
            'message':     'ESP32-CAM connectée et opérationnelle' if connected else f'HTTP {r.status_code}',
        })

    except http_requests.exceptions.ConnectTimeout:
        return jsonify({'connected': False, 'ip': ip, 'message': 'Hôte injoignable (timeout)'})
    except http_requests.exceptions.ConnectionError:
        return jsonify({'connected': False, 'ip': ip, 'message': "Connexion refusée — vérifiez l'IP et le WiFi"})
    except Exception as e:
        return jsonify({'connected': False, 'ip': ip, 'message': str(e)})


# ══════════════════════════════════════════════════════════════════════════════
# ── ESP32 : DONNÉES CAPTEURS IoT (DHT22 temp/humidité) ────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/esp32/sensors', methods=['GET'])
def esp32_sensors():
    ip = request.args.get('ip', ESP32_DEFAULT_IP).strip()
    if not ip:
        return jsonify({'ok': False, 'error': 'Adresse IP ESP32 non fournie'}), 400
    try:
        r = http_requests.get(f'http://{ip}/sensors', timeout=5)
        r.raise_for_status()
        data = r.json()
        return jsonify(data)
    except http_requests.exceptions.ConnectTimeout:
        return jsonify({'ok': False, 'error': 'Timeout — ESP32 injoignable'}), 504
    except http_requests.exceptions.ConnectionError:
        return jsonify({'ok': False, 'error': 'Connexion refusée'}), 503
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# ── ESP32-CAM : CAPTURER ET ANALYSER ──────────────────────────────────════════
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/esp32/capture', methods=['POST'])
@role_required('maraicher')
def esp32_capture():
    data = request.get_json(silent=True) or {}
    ip   = data.get('ip', ESP32_DEFAULT_IP).strip()

    if not ip:
        return jsonify({'error': 'Adresse IP ESP32 non fournie'}), 400

    capture_url = f'http://{ip}/capture'
    tmp_path    = None

    try:
        r = http_requests.get(capture_url, timeout=ESP32_CAPTURE_TIMEOUT)
        r.raise_for_status()

        if 'image' not in r.headers.get('Content-Type', ''):
            return jsonify({'error': "L'ESP32 n'a pas renvoyé une image valide"}), 502

        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False, dir=UPLOAD_FOLDER) as f:
            f.write(r.content)
            tmp_path = f.name

        result = run_inference(tmp_path)
        result['source']   = 'esp32'
        result['esp32_ip'] = ip

        # ── Auto-sauvegarde MongoDB ──────────────────────────────────────────
        entry = {
            **result,
            'image':   f'ESP32-CAM ({ip})',
            'date':    datetime.now(timezone.utc),
            'userId':  g.current_user['idUtilisateur'],
        }
        db_id = _save_prediction(entry)
        if db_id:
            result['dbId'] = db_id

        return jsonify(result)

    except http_requests.exceptions.ConnectTimeout:
        return jsonify({'error': f'ESP32 injoignable à {ip} (timeout)'}), 504
    except http_requests.exceptions.ConnectionError:
        return jsonify({'error': f"Impossible de se connecter à {ip} — vérifiez l'IP"}), 503
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
# ── HISTORIQUE DES ANALYSES (MongoDB) ─────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/api/history', methods=['GET'])
def get_history():
    """Retourne les 200 dernières analyses triées du plus récent au plus ancien."""
    col = get_history_col()
    if col is None:
        return jsonify([])
    try:
        from pymongo import DESCENDING
        records = list(col.find({}).sort('date', DESCENDING).limit(200))
        return jsonify([_serialize(r) for r in records])
    except Exception as e:
        print(f"Erreur lecture historique : {e}")
        return jsonify([])


@app.route('/api/history', methods=['POST'])
def post_history():
    """Sauvegarde une entrée (utilisé par le frontend pour les analyses mock)."""
    col = get_history_col()
    if col is None:
        return jsonify({'ok': False, 'error': 'MongoDB non disponible'}), 503
    try:
        record = request.get_json(silent=True)
        if not record:
            return jsonify({'error': 'Données manquantes'}), 400
        # Normalise le champ date en datetime Python
        raw_date = record.get('date')
        if isinstance(raw_date, str):
            try:
                record['date'] = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
            except ValueError:
                record['date'] = datetime.now(timezone.utc)
        else:
            record['date'] = datetime.now(timezone.utc)

        result = col.insert_one(record)
        return jsonify({'ok': True, 'dbId': str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/history/<db_id>', methods=['DELETE'])
def delete_one_history(db_id):
    """Supprime un enregistrement par son _id MongoDB."""
    col = get_history_col()
    if col is None:
        return jsonify({'ok': False}), 503
    try:
        from bson import ObjectId
        col.delete_one({'_id': ObjectId(db_id)})
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """Vide tout l'historique."""
    col = get_history_col()
    if col is None:
        return jsonify({'ok': False}), 503
    try:
        col.delete_many({})
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# ── HISTORIQUE DE L'UTILISATEUR CONNECTÉ (diagramme "Consultation historique") ─
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/history', methods=['GET'])
@role_required('maraicher', 'administrateur')
def get_user_history():
    """Maraîcher : ses propres analyses (consulterHistorique()).
    Administrateur : toutes les analyses (consulterAnalyses()).
    Même format que /api/history (label, confidence, disease_info, image, source, date)
    pour rester compatible avec transformBackendResponse() côté frontend."""
    col = get_history_col()
    if col is None:
        return jsonify([])

    query = {}
    if g.current_user.get('role') != 'administrateur':
        query['userId'] = g.current_user['idUtilisateur']

    try:
        from pymongo import DESCENDING
        records = list(col.find(query).sort('date', DESCENDING).limit(200))
        return jsonify([_serialize(r) for r in records])
    except Exception as e:
        print(f"Erreur lecture /history : {e}")
        return jsonify([])


# ══════════════════════════════════════════════════════════════════════════════
# ── GESTION DES UTILISATEURS (réservée à l'Administrateur) ───────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/users', methods=['GET'])
@role_required('administrateur')
def list_users():
    col = get_users_col()
    if col is None:
        return jsonify({'error': 'Base de données indisponible'}), 503
    return jsonify([_user_to_dict(u) for u in col.find({})])


@app.route('/users', methods=['POST'])
@role_required('administrateur')
def create_user():
    """Administrateur.ajouterUtilisateur()"""
    data = request.get_json(silent=True) or {}
    nom          = (data.get('nom') or '').strip()
    prenom       = (data.get('prenom') or '').strip()
    email        = (data.get('email') or '').strip().lower()
    mot_de_passe = data.get('motDePasse') or ''
    role         = data.get('role') or 'maraicher'
    exploitation = data.get('exploitation')

    if not nom or not email or not mot_de_passe:
        return jsonify({'error': 'nom, email et motDePasse sont requis'}), 400
    if role not in ('administrateur', 'maraicher'):
        return jsonify({'error': "role doit être 'administrateur' ou 'maraicher'"}), 400

    col = get_users_col()
    if col is None:
        return jsonify({'error': 'Base de données indisponible'}), 503

    doc = {
        'nom': nom, 'prenom': prenom, 'email': email,
        'motDePasse': hash_password(mot_de_passe), 'role': role,
    }
    if role == 'maraicher':
        doc['exploitation'] = exploitation

    try:
        result = col.insert_one(doc)
        doc['_id'] = result.inserted_id
        return jsonify(_user_to_dict(doc)), 201
    except Exception as e:
        if 'duplicate key' in str(e).lower():
            return jsonify({'error': 'Cet email est déjà utilisé'}), 409
        return jsonify({'error': str(e)}), 500


@app.route('/users/<user_id>', methods=['PUT'])
@role_required('administrateur')
def update_user(user_id):
    """Administrateur.modifierUtilisateur()"""
    from bson import ObjectId
    data = request.get_json(silent=True) or {}

    updates = {}
    for field in ('nom', 'prenom', 'email', 'role', 'exploitation'):
        if field in data:
            updates[field] = data[field]
    if 'motDePasse' in data and data['motDePasse']:
        updates['motDePasse'] = hash_password(data['motDePasse'])

    if not updates:
        return jsonify({'error': 'Aucun champ à mettre à jour'}), 400

    col = get_users_col()
    if col is None:
        return jsonify({'error': 'Base de données indisponible'}), 503

    try:
        result = col.find_one_and_update(
            {'_id': ObjectId(user_id)}, {'$set': updates},
            return_document=True,
        )
        if result is None:
            return jsonify({'error': 'Utilisateur introuvable'}), 404
        return jsonify(_user_to_dict(result))
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/users/<user_id>', methods=['DELETE'])
@role_required('administrateur')
def delete_user(user_id):
    """Administrateur.supprimerUtilisateur()"""
    from bson import ObjectId
    col = get_users_col()
    if col is None:
        return jsonify({'error': 'Base de données indisponible'}), 503
    try:
        result = col.delete_one({'_id': ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Utilisateur introuvable'}), 404
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ══════════════════════════════════════════════════════════════════════════════
# ── DONNÉES CAPTEURS (DonneesCapteur : temp/humidité air, humidité sol) ───────
# ══════════════════════════════════════════════════════════════════════════════
EXEMPLE_DONNEES_CAPTEUR = {
    'temperatureAir': 24.5,
    'humiditeAir':    62.0,
    'humiditeSol':    38.0,
}


def _insert_sensor_reading(data: dict):
    col = get_sensors_col()
    if col is None:
        return None, jsonify({'error': 'Base de données indisponible'}), 503

    for field in ('temperatureAir', 'humiditeAir', 'humiditeSol'):
        if field not in data:
            return None, jsonify({'error': f'Champ manquant : {field}'}), 400

    raw_date = data.get('dateMesure')
    if isinstance(raw_date, str):
        try:
            date_mesure = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
        except ValueError:
            date_mesure = datetime.now(timezone.utc)
    else:
        date_mesure = datetime.now(timezone.utc)

    doc = {
        'temperatureAir': float(data['temperatureAir']),
        'humiditeAir':    float(data['humiditeAir']),
        'humiditeSol':    float(data['humiditeSol']),
        'dateMesure':     date_mesure,
    }
    if data.get('analyseId'):
        doc['analyseId'] = data['analyseId']  # référence optionnelle vers Analyse.idAnalyse

    result = col.insert_one(doc)
    return str(result.inserted_id), None, None


@app.route('/sensors/data', methods=['POST'])
def post_sensor_data():
    """DonneesCapteur.recevoirDonnees() — appelé par le capteur physique (pas d'auth requise)."""
    data = request.get_json(silent=True) or {}
    inserted_id, error_response, status = _insert_sensor_reading(data)
    if error_response:
        return error_response, status
    return jsonify({'ok': True, 'id': inserted_id}), 201


@app.route('/sensors/data/simulate', methods=['POST'])
def simulate_sensor_data():
    """Route de test : simule l'envoi de données par un capteur, sans matériel réel."""
    inserted_id, error_response, status = _insert_sensor_reading(dict(EXEMPLE_DONNEES_CAPTEUR))
    if error_response:
        return error_response, status
    return jsonify({'ok': True, 'id': inserted_id, 'donnees_simulees': EXEMPLE_DONNEES_CAPTEUR}), 201


@app.route('/sensors/data', methods=['GET'])
@role_required('maraicher')
def get_sensor_data():
    """Maraicher.consulterDonnees()"""
    col = get_sensors_col()
    if col is None:
        return jsonify([])
    try:
        records = list(col.find({}).sort('dateMesure', -1).limit(200))
        return jsonify([_serialize(r) for r in records])
    except Exception as e:
        print(f"Erreur lecture /sensors/data : {e}")
        return jsonify([])


# ══════════════════════════════════════════════════════════════════════════════
# ── GESTIONNAIRES D'ERREURS ────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
@app.errorhandler(404)
def not_found(_):
    return jsonify({'error': 'Route introuvable', 'endpoints': [
        '/', '/health', '/auth/login', '/api/predict', '/api/predict/cnn',
        '/api/esp32/status', '/api/esp32/capture', '/api/history', '/history',
        '/users', '/sensors/data',
    ]}), 404

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
    get_history_col()   # initialise la connexion au démarrage
    print(f"\n🌿  PlantAI Backend démarré sur : http://localhost:{port}")
    print(f"📡  ESP32 par défaut          : {ESP32_DEFAULT_IP or 'non configuré'}")
    print(f"🧠  Modèle                    : HuggingFace ViT / EfficientNet-B4\n")
    app.run(host='0.0.0.0', port=port, debug=debug)
