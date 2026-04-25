from ultralytics import YOLO
import cv2
import os
import numpy as np
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Charger les variables d'environnement
load_dotenv()

# Charger le modèle YOLO avec vérification
MODEL_PATH = os.getenv('MODEL_PATH', 'model/modele_plantes.pt')

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Modèle introuvable : {MODEL_PATH}. Vérifiez la variable MODEL_PATH dans votre fichier .env.")

model = YOLO(MODEL_PATH)


def run_inference(img_path):
    try:
        # Vérifier que l'image existe
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Image introuvable : {img_path}")

        # Effectuer l'inférence avec le modèle
        results = model(img_path)

        # Vérifier qu'il y a bien des résultats
        if not results or len(results) == 0:
            return {
                'predictions': [],
                'annotated_image_path': None,
                'message': 'Aucune détection effectuée'
            }

        # Obtenir les annotations et les coordonnées des boîtes englobantes
        detections = results[0].boxes

        # Initialiser les listes vides si aucune détection
        if detections is None or len(detections) == 0:
            return {
                'predictions': [],
                'annotated_image_path': None,
                'message': 'Aucune maladie détectée sur cette image'
            }

        boxes = detections.xyxy.numpy()  # coordonnées [x1, y1, x2, y2]
        confidences = detections.conf.numpy()  # confiance
        classes = detections.cls.numpy().astype(int)  # classes détectées

        # Lire l'image pour l'annotation
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError(f"Impossible de lire l'image : {img_path}")

        # Annoter l'image avec des boîtes rouges
        for box, conf, cls in zip(boxes, confidences, classes):
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)  # cadre rouge
            cv2.putText(img, f'Class: {cls}, Conf: {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Chemin pour enregistrer l'image annotée
        DETECTION_FOLDER = 'static/detections/'
        if not os.path.exists(DETECTION_FOLDER):
            os.makedirs(DETECTION_FOLDER)

        # Sécuriser le nom de fichier de sortie
        safe_filename = secure_filename(os.path.basename(img_path))
        annotated_img_path = os.path.join(DETECTION_FOLDER, safe_filename)
        cv2.imwrite(annotated_img_path, img)

        # Préparer le JSON des résultats
        results_json = []
        for box, conf, cls in zip(boxes, confidences, classes):
            results_json.append({
                'class': int(cls),
                'confidence': float(conf),
                'box': box.tolist()  # Convertir en liste pour JSON
            })

        return {
            'predictions': results_json,
            'annotated_image_path': annotated_img_path
        }

    except Exception as e:
        # Relancer l'exception pour qu'elle soit gérée dans app.py
        raise RuntimeError(f"Erreur lors de l'inférence : {str(e)}") from e
