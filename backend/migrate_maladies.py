"""
Migration — crée les collections normalisées "maladies" et "recommandations"
à partir des données jusqu'ici fusionnées dans CLASS_INFO / UNIVERSAL_DISEASE_INFO
(model_logic.py).

Modèle cible :
  maladies       : { codeLabel, nom, traitement, recommandationId }
  recommandations: { texte, produitsConseilles: [...] }

Idempotent : peut être relancé sans dupliquer (upsert sur codeLabel).
Les entrées "healthy" (pas de maladie) sont ignorées — une Analyse d'une
plante saine n'a simplement pas de maladieId.

Usage :
  cd backend
  python migrate_maladies.py
"""

import os
import re
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from pymongo import MongoClient

from model_logic import CLASS_INFO, UNIVERSAL_DISEASE_INFO

load_dotenv()


def _extract_produits(traitement: str) -> list:
    """Découpe le texte de traitement existant en une liste de produits candidats
    (aucune donnée inventée — simple segmentation du texte déjà présent)."""
    if not traitement:
        return []
    parts = re.split(r'\s+ou\s+|\s*\+\s*|,\s*|;\s*', traitement)
    return [p.strip().rstrip('.') for p in parts if len(p.strip()) > 2][:5]


def main():
    uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/plantai')
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.server_info()
    db = client['plantai']
    maladies_col = db['maladies']
    recos_col    = db['recommandations']
    maladies_col.create_index('codeLabel', unique=True)

    sources = list(CLASS_INFO.items()) + list(UNIVERSAL_DISEASE_INFO.items())
    created = updated = skipped = 0

    for code_label, info in sources:
        if not info.get('maladie'):
            skipped += 1  # entrée "saine", pas une maladie
            continue

        nom        = info['maladie']
        traitement = info.get('traitement') or ''
        texte      = info.get('conseil') or ''
        produits   = _extract_produits(traitement)

        reco_result = recos_col.find_one_and_update(
            {'codeLabelSource': code_label},
            {'$set': {'texte': texte, 'produitsConseilles': produits, 'codeLabelSource': code_label}},
            upsert=True, return_document=True,
        )

        existing = maladies_col.find_one({'codeLabel': code_label})
        maladies_col.update_one(
            {'codeLabel': code_label},
            {'$set': {
                'nom': nom, 'traitement': traitement,
                'recommandationId': reco_result['_id'],
            }},
            upsert=True,
        )
        if existing:
            updated += 1
        else:
            created += 1

    print(f"Maladies créées : {created} | mises à jour : {updated} | ignorées (saines) : {skipped}")
    print(f"Total en base — maladies : {maladies_col.count_documents({})} | recommandations : {recos_col.count_documents({})}")


if __name__ == '__main__':
    main()
