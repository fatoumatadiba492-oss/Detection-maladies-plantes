"""
Test des priorités 1 à 4 (auth, historique, utilisateurs, capteurs) via
Flask test_client() + mongomock (MongoDB en mémoire, aucun serveur requis).

Usage :
  cd backend
  pip install mongomock   # dépendance de test uniquement, pas en prod
  python test_priorities.py
"""

import sys
import os
import mongomock
from datetime import datetime, timezone
from bson import ObjectId

import app as app_module
from auth import hash_password

# ── Injection d'une base MongoDB en mémoire (bypass la vraie connexion) ───────
mock_db = mongomock.MongoClient()['plantai']
app_module._mongo_col = mock_db['predictions']
app_module._mongo_col.create_index([('date', -1)])

client = app_module.app.test_client()

passed = failed = 0


def check(label, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {label}")
    else:
        failed += 1
        print(f"  ❌ {label}")


# ══════════════════════════════════════════════════════════════════════════════
print("\n=== PRIORITÉ 1 — Authentification ===")

mock_db['users'].insert_one({
    'nom': 'Diallo', 'prenom': 'Fatou', 'email': 'admin@plantai.test',
    'motDePasse': hash_password('admin123'), 'role': 'administrateur',
})
mock_db['users'].insert_one({
    'nom': 'Ba', 'prenom': 'Moussa', 'email': 'marai@plantai.test',
    'motDePasse': hash_password('champs123'), 'role': 'maraicher', 'exploitation': 'Ferme du Nord',
})

r = client.post('/auth/login', json={'email': 'admin@plantai.test', 'motDePasse': 'mauvais'})
check("login refusé si mauvais mot de passe (401)", r.status_code == 401)

r = client.post('/auth/login', json={'email': 'admin@plantai.test', 'motDePasse': 'admin123'})
check("login admin réussi (200)", r.status_code == 200)
admin_token = r.get_json().get('token')
check("token présent", bool(admin_token))
check("role renvoyé = administrateur", r.get_json().get('role') == 'administrateur')

r = client.post('/auth/login', json={'email': 'marai@plantai.test', 'motDePasse': 'champs123'})
check("login maraîcher réussi (200)", r.status_code == 200)
marai_data = r.get_json()
marai_token = marai_data['token']
marai_id    = marai_data['idUtilisateur']

r = client.get('/users')
check("route protégée sans token → 401", r.status_code == 401)

r = client.get('/users', headers={'Authorization': f'Bearer {marai_token}'})
check("route admin refusée pour un maraîcher → 403", r.status_code == 403)

# ══════════════════════════════════════════════════════════════════════════════
print("\n=== PRIORITÉ 2 — Historique des analyses ===")

mock_db['predictions'].insert_one({
    'label': 'Tomato___Late_blight', 'confidence': 0.91,
    'disease_info': {'maladie': 'Mildiou'}, 'image': 'feuille1.jpg',
    'source': 'api', 'date': datetime.now(timezone.utc), 'userId': marai_id,
})
mock_db['predictions'].insert_one({
    'label': 'Apple___healthy', 'confidence': 0.97,
    'disease_info': {'maladie': None}, 'image': 'feuille2.jpg',
    'source': 'api', 'date': datetime.now(timezone.utc), 'userId': 'un-autre-user',
})

r = client.get('/history')
check("historique sans token → 401", r.status_code == 401)

r = client.get('/history', headers={'Authorization': f'Bearer {marai_token}'})
data = r.get_json()
check("maraîcher voit uniquement ses analyses (1)", r.status_code == 200 and len(data) == 1)
check("champ maladie correct", data and data[0]['disease_info']['maladie'] == 'Mildiou')

r = client.get('/history', headers={'Authorization': f'Bearer {admin_token}'})
data = r.get_json()
check("admin voit toutes les analyses (2)", r.status_code == 200 and len(data) == 2)

# ══════════════════════════════════════════════════════════════════════════════
print("\n=== PRIORITÉ 3 — Gestion des utilisateurs (admin) ===")

r = client.post('/users', headers={'Authorization': f'Bearer {marai_token}'},
                 json={'nom': 'X', 'email': 'x@x.test', 'motDePasse': 'x', 'role': 'maraicher'})
check("création utilisateur refusée pour un maraîcher → 403", r.status_code == 403)

r = client.post('/users', headers={'Authorization': f'Bearer {admin_token}'}, json={
    'nom': 'Sow', 'prenom': 'Awa', 'email': 'awa@plantai.test',
    'motDePasse': 'motdepasse1', 'role': 'maraicher', 'exploitation': 'Verger Sud',
})
check("admin crée un utilisateur (201)", r.status_code == 201)
new_user_id = r.get_json()['idUtilisateur']
check("motDePasse absent de la réponse", 'motDePasse' not in r.get_json())

r = client.get('/users', headers={'Authorization': f'Bearer {admin_token}'})
check("liste des utilisateurs = 3", len(r.get_json()) == 3)

r = client.put(f'/users/{new_user_id}', headers={'Authorization': f'Bearer {admin_token}'},
                json={'exploitation': 'Verger Sud-Est'})
check("admin modifie un utilisateur (200)", r.status_code == 200 and r.get_json()['exploitation'] == 'Verger Sud-Est')

r = client.delete(f'/users/{new_user_id}', headers={'Authorization': f'Bearer {admin_token}'})
check("admin supprime un utilisateur (200)", r.status_code == 200)

r = client.get('/users', headers={'Authorization': f'Bearer {admin_token}'})
check("liste des utilisateurs revenue à 2", len(r.get_json()) == 2)

# ══════════════════════════════════════════════════════════════════════════════
print("\n=== PRIORITÉ 4 — Données capteurs ===")

r = client.post('/sensors/data/simulate')
check("simulation capteur (201, sans auth)", r.status_code == 201)

r = client.post('/sensors/data', json={
    'temperatureAir': 21.3, 'humiditeAir': 55.2, 'humiditeSol': 40.1,
})
check("envoi manuel de données capteur (201)", r.status_code == 201)

r = client.post('/sensors/data', json={'temperatureAir': 20})
check("champ manquant → 400", r.status_code == 400)

r = client.get('/sensors/data')
check("lecture capteurs sans token → 401", r.status_code == 401)

r = client.get('/sensors/data', headers={'Authorization': f'Bearer {marai_token}'})
check("lecture capteurs avec token → 200, 2 entrées", r.status_code == 200 and len(r.get_json()) == 2)

r = client.get('/sensors/data', headers={'Authorization': f'Bearer {admin_token}'})
check("lecture capteurs refusée pour un admin → 403 (route Maraîcher)", r.status_code == 403)

# ══════════════════════════════════════════════════════════════════════════════
print("\n=== SÉCURITÉ — rôle strict sur les routes Maraîcher ===")
# Le décorateur @role_required rejette avant même de lire request.files,
# donc ces routes peuvent être testées sans image ni modèle IA chargé.

for route in ('/api/predict', '/api/predict/cnn', '/api/esp32/capture'):
    r = client.post(route)
    check(f"{route} sans token → 401", r.status_code == 401)

    r = client.post(route, headers={'Authorization': f'Bearer {admin_token}'})
    check(f"{route} avec un admin (mauvais rôle) → 403", r.status_code == 403)

    r = client.post(route, headers={'Authorization': f'Bearer {marai_token}'})
    check(f"{route} avec un maraîcher → passe le contrôle de rôle (pas de 401/403)", r.status_code not in (401, 403))

# ══════════════════════════════════════════════════════════════════════════════
print("\n=== ÉTAPE 2 — Catalogue Maladies & Recommandations ===")

reco_id = mock_db['recommandations'].insert_one(
    {'texte': 'Traiter rapidement', 'produitsConseilles': ['Cuivre', 'Soufre']}
).inserted_id
maladie_id = mock_db['maladies'].insert_one(
    {'codeLabel': 'Test___Rouille', 'nom': 'Rouille test', 'traitement': 'Fongicide', 'recommandationId': reco_id}
).inserted_id

entry = {}
app_module._link_maladie(entry, {'label': 'Test___Rouille'})
check("_link_maladie rattache maladieId depuis result['label']", entry.get('maladieId') == str(maladie_id))
check("_link_maladie rattache recommandationId", entry.get('recommandationId') == str(reco_id))

entry2 = {}
app_module._link_maladie(entry2, {'label': 'Inconnu___XYZ'})
check("_link_maladie ignore silencieusement un code non référencé", 'maladieId' not in entry2)

r = client.get('/maladies')
check("GET /maladies liste le catalogue", r.status_code == 200 and len(r.get_json()) == 1)

r = client.get(f'/maladies/{maladie_id}')
data = r.get_json()
check("GET /maladies/<id> renvoie la recommandation imbriquée",
      r.status_code == 200 and data['recommandation']['texte'] == 'Traiter rapidement')

r = client.get('/maladies/000000000000000000000000')
check("GET /maladies/<id inexistant> → 404", r.status_code == 404)

# ══════════════════════════════════════════════════════════════════════════════
print("\n=== ÉTAPE 3 — Persistance des images ===")

os.makedirs(app_module.UPLOAD_FOLDER, exist_ok=True)
fake_upload = os.path.join(app_module.UPLOAD_FOLDER, 'test_upload.jpg')
with open(fake_upload, 'wb') as f:
    f.write(b'\xff\xd8\xff\xe0FAKEJPEGDATA')

image_id, permanent_path = app_module._persist_image(fake_upload, 'feuille_test.jpg')
check("_persist_image renvoie un idImage", bool(image_id))
check("_persist_image renomme vers un chemin permanent unique", permanent_path != fake_upload and os.path.exists(permanent_path))
check("l'ancien chemin temporaire n'existe plus (renommé, pas copié)", not os.path.exists(fake_upload))

img_doc = mock_db['images'].find_one({'_id': ObjectId(image_id)})
check("le document 'images' contient nomImage/cheminImage/dateCapture",
      img_doc is not None and img_doc['nomImage'] == 'feuille_test.jpg' and 'dateCapture' in img_doc)

r = client.get(f'/images/{image_id}')
check("GET /images/<id> sert le fichier (200)", r.status_code == 200)

r = client.get('/images/000000000000000000000000')
check("GET /images/<id inexistant> → 404", r.status_code == 404)

os.remove(permanent_path)  # nettoyage du fichier de test

# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{'='*50}\nRésultat : {passed} réussis / {failed} échoués\n{'='*50}")
sys.exit(1 if failed else 0)
