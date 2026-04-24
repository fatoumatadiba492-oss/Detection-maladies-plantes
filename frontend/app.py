"""
Frontend Flask — Détection des Maladies des Plantes
Sert l'interface React (index.html) et fait le lien avec le backend.
Lancer : python app.py
"""

from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder=".")

# ── Route principale : affiche index.html ──────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# ── Route pour les fichiers statiques éventuels (images, css, js) ──────────
@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)

if __name__ == "__main__":
    port = int(os.environ.get("FRONTEND_PORT", 3000))
    print(f"\n🌿  Interface disponible sur : http://localhost:{port}")
    print(f"🔗  Assurez-vous que le backend tourne sur : http://localhost:5000\n")
    app.run(debug=True, port=port)
