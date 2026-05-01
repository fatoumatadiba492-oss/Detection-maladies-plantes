"""
Moteur d'inférence — Détection des maladies des plantes
Modèle primaire  : dima806/plant_disease_image_detection (HuggingFace ViT, 38 classes)
Modèle secondaire: EfficientNet-B4 local si entraîné (model/plant_disease_efficientnet.pt)
Fallback         : YOLOv8 si modèle local disponible
"""

import os
import io
import json
import warnings
warnings.filterwarnings('ignore')

from PIL import Image

# ── Métadonnées des 38 classes PlantVillage (noms FR + traitements) ────────────
CLASS_INFO = {
    "Apple___Apple_scab": {
        "fr": "Pomme — Tavelure",
        "plante": "Pomme 🍎",
        "maladie": "Tavelure",
        "niveau": "sick",
        "description": "Champignon Venturia inaequalis. Taches olivâtres puis brun-noir sur feuilles et fruits.",
        "traitement": "Fongicide cuivre ou captane dès le débourrement. Répéter après chaque pluie.",
        "conseil": "Ramasser et brûler les feuilles tombées. Tailler pour aérer la frondaison.",
    },
    "Apple___Black_rot": {
        "fr": "Pomme — Pourriture noire",
        "plante": "Pomme 🍎",
        "maladie": "Pourriture noire",
        "niveau": "critical",
        "description": "Champignon Botryosphaeria obtusa. Anneaux concentriques brun-noirs sur fruits, chancres sur rameaux.",
        "traitement": "Excision chirurgicale des parties atteintes. Fongicide systémique (thiophanate-méthyl).",
        "conseil": "Désinfection des outils de taille. Destruction des momies de fruits. Taille hivernale stricte.",
    },
    "Apple___Cedar_apple_rust": {
        "fr": "Pomme — Rouille du cèdre",
        "plante": "Pomme 🍎",
        "maladie": "Rouille cédrière",
        "niveau": "sick",
        "description": "Champignon Gymnosporangium juniperi-virginianae. Taches orange vif sur la face supérieure des feuilles.",
        "traitement": "Myclobutanil ou trifloxystrobine au stade bouton rose. 2-3 traitements espacés de 10 jours.",
        "conseil": "Supprimer les genévriers/cèdres à moins de 300 m. Variétés résistantes recommandées.",
    },
    "Apple___healthy": {
        "fr": "Pomme — Saine ✅",
        "plante": "Pomme 🍎",
        "maladie": None,
        "niveau": "healthy",
        "description": "Feuille de pommier en parfaite santé, sans aucun signe de pathologie.",
        "traitement": "Aucun traitement requis.",
        "conseil": "Maintenir l'irrigation régulière et la fertilisation équilibrée NPK.",
    },
    "Blueberry___healthy": {
        "fr": "Myrtille — Saine ✅",
        "plante": "Myrtille 🫐",
        "maladie": None,
        "niveau": "healthy",
        "description": "Plant de myrtillier en bonne santé.",
        "traitement": "Aucun traitement requis.",
        "conseil": "Maintenir un pH acide (4.5–5.5). Paillis de copeaux de bois conseillé.",
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "fr": "Cerise — Oïdium",
        "plante": "Cerise 🍒",
        "maladie": "Oïdium",
        "niveau": "sick",
        "description": "Podosphaera clandestina. Feutrage blanc poudreux sur jeunes feuilles et pousses.",
        "traitement": "Soufre mouillable ou bicarbonate de sodium. Fongicide systémique si sévère.",
        "conseil": "Taille sévère pour aérer. Éviter l'excès d'azote. Arroser à la base.",
    },
    "Cherry_(including_sour)___healthy": {
        "fr": "Cerise — Saine ✅",
        "plante": "Cerise 🍒",
        "maladie": None,
        "niveau": "healthy",
        "description": "Cerisier en bonne santé.",
        "traitement": "Aucun traitement requis.",
        "conseil": "Taille après récolte. Protection filet contre les oiseaux.",
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "fr": "Maïs — Cercosporiose (Tache grise)",
        "plante": "Maïs 🌽",
        "maladie": "Cercosporiose",
        "niveau": "sick",
        "description": "Cercospora zeae-maydis. Lésions rectangulaires gris-brun entre nervures, limitées par elles.",
        "traitement": "Triazole + strobilurine à partir de la feuille ligule (stade 9-11 feuilles).",
        "conseil": "Rotation maïs/soja. Hybrides résistants. Enfouissement des résidus.",
    },
    "Corn_(maize)___Common_rust_": {
        "fr": "Maïs — Rouille commune",
        "plante": "Maïs 🌽",
        "maladie": "Rouille commune",
        "niveau": "sick",
        "description": "Puccinia sorghi. Pustules brun-rouille ovales sur les deux faces foliaires.",
        "traitement": "Fongicide triazole si pression forte avant floraison. Hybrides résistants préférables.",
        "conseil": "Infections tardives généralement sans impact économique. Surveiller dès début saison.",
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "fr": "Maïs — Helminthosporiose du Nord",
        "plante": "Maïs 🌽",
        "maladie": "Helminthosporiose",
        "niveau": "sick",
        "description": "Exserohilum turcicum. Grandes taches en forme de cigare, gris-vert puis brun-tan.",
        "traitement": "Propiconazole ou azoxystrobine + propiconazole au stade panicule.",
        "conseil": "Rotation obligatoire. Enfouissement profond des résidus.",
    },
    "Corn_(maize)___healthy": {
        "fr": "Maïs — Sain ✅",
        "plante": "Maïs 🌽",
        "maladie": None,
        "niveau": "healthy",
        "description": "Plant de maïs en bonne santé.",
        "traitement": "Aucun traitement requis.",
        "conseil": "Fertilisation azotée fractionnée. Irrigation en période de floraison.",
    },
    "Grape___Black_rot": {
        "fr": "Vigne — Pourriture noire",
        "plante": "Raisin 🍇",
        "maladie": "Pourriture noire",
        "niveau": "critical",
        "description": "Guignardia bidwellii. Taches circulaires brun-rouge avec pycnides noires, baies momifiées.",
        "traitement": "Mancozèbe ou cuivre en préventif. Traitement obligatoire avant floraison.",
        "conseil": "Éliminer les grappes momifiées. Palissage pour aérer. Taille courte.",
    },
    "Grape___Esca_(Black_Measles)": {
        "fr": "Vigne — Esca (Rougeot parasitaire)",
        "plante": "Raisin 🍇",
        "maladie": "Esca",
        "niveau": "critical",
        "description": "Complexe fongique du bois (Phaeomoniella, Phaeoacremonium). Tigré foliaire, apoplexie foudroyante.",
        "traitement": "Aucun traitement curatif. Protection des plaies de taille avec mastic fongicide.",
        "conseil": "Tailler par temps sec. Désinfecter outils (éthanol). Arracher plants très atteints.",
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "fr": "Vigne — Brûlure des feuilles",
        "plante": "Raisin 🍇",
        "maladie": "Brûlure foliaire",
        "niveau": "sick",
        "description": "Pseudocercospora vitis. Taches angulaires brun-rougeâtre, jaunissement puis chute foliaire.",
        "traitement": "Cuivre + fongicide de contact. Éviter l'humidité stagnante.",
        "conseil": "Ramasser les feuilles tombées. Palissage soigné. Bonne gestion eau.",
    },
    "Grape___healthy": {
        "fr": "Vigne — Saine ✅",
        "plante": "Raisin 🍇",
        "maladie": None,
        "niveau": "healthy",
        "description": "Feuille de vigne en parfaite santé.",
        "traitement": "Aucun traitement requis.",
        "conseil": "Surveillance mildiou/oïdium. Taille hivernale rigoureuse.",
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "fr": "Orange — Huanglongbing (HLB)",
        "plante": "Orange 🍊",
        "maladie": "Verdissement des agrumes (HLB)",
        "niveau": "critical",
        "description": "Bactérie Candidatus Liberibacter asiaticus. Mosaïque asymétrique jaune-vert, fruits difformes et amers. INCURABLE.",
        "traitement": "Aucun traitement curatif. Arrachage et destruction immédiate des plants infectés.",
        "conseil": "QUARANTAINE STRICTE. Contrôle du psylle asiatique (vecteur). Plants certifiés indemnes obligatoires.",
    },
    "Peach___Bacterial_spot": {
        "fr": "Pêche — Tache bactérienne",
        "plante": "Pêche 🍑",
        "maladie": "Tache bactérienne",
        "niveau": "sick",
        "description": "Xanthomonas arboricola pv. pruni. Petites taches aqueuses angulaires sur feuilles et fruits.",
        "traitement": "Oxychlorure de cuivre en préventif. Éviter aspersion sur feuillage.",
        "conseil": "Variétés résistantes disponibles. Éviter les blessures lors des travaux.",
    },
    "Peach___healthy": {
        "fr": "Pêche — Saine ✅",
        "plante": "Pêche 🍑",
        "maladie": None,
        "niveau": "healthy",
        "description": "Pêcher en bonne santé.",
        "traitement": "Aucun traitement requis.",
        "conseil": "Éclaircissage des fruits. Protection contre la cloque du pêcher au débourrement.",
    },
    "Pepper,_bell___Bacterial_spot": {
        "fr": "Poivron — Tache bactérienne",
        "plante": "Poivron 🫑",
        "maladie": "Tache bactérienne",
        "niveau": "sick",
        "description": "Xanthomonas campestris pv. vesicatoria. Lésions aqueuses cernées de halo jaune, puis nécrotiques.",
        "traitement": "Cuivre + mancozèbe en préventif. Bactéricide (kasugamycine) si sévère.",
        "conseil": "Rotation 3 ans. Semences certifiées. Arrosage au sol uniquement.",
    },
    "Pepper,_bell___healthy": {
        "fr": "Poivron — Sain ✅",
        "plante": "Poivron 🫑",
        "maladie": None,
        "niveau": "healthy",
        "description": "Plant de poivron en bonne santé.",
        "traitement": "Aucun traitement requis.",
        "conseil": "Tuteurage recommandé. Température optimale 18–30°C.",
    },
    "Potato___Early_blight": {
        "fr": "Pomme de terre — Alternariose",
        "plante": "Pomme de terre 🥔",
        "maladie": "Alternariose (mildiou précoce)",
        "niveau": "sick",
        "description": "Alternaria solani. Taches brunes concentriques en cible, sur feuilles les plus âgées d'abord.",
        "traitement": "Chlorothalonil ou mancozèbe préventif dès fermeture du couvert végétal.",
        "conseil": "Rotation 3 ans. Plants certifiés. Binage pour aération.",
    },
    "Potato___Late_blight": {
        "fr": "Pomme de terre — Mildiou",
        "plante": "Pomme de terre 🥔",
        "maladie": "Mildiou (Phytophthora infestans)",
        "niveau": "critical",
        "description": "Phytophthora infestans. Taches huileuses brun-violet, duvet blanc en face inférieure. Progression fulgurante.",
        "traitement": "TRAITEMENT D'URGENCE : métalaxyl + mancozèbe. Détruire les fanes. Récolte rapide.",
        "conseil": "Surveiller les alertes mildiou (températures 15-20°C + humidité). Rotation obligatoire 4 ans.",
    },
    "Potato___healthy": {
        "fr": "Pomme de terre — Saine ✅",
        "plante": "Pomme de terre 🥔",
        "maladie": None,
        "niveau": "healthy",
        "description": "Plant de pomme de terre en bonne santé.",
        "traitement": "Aucun traitement requis.",
        "conseil": "Buttage régulier. Irrigation goutte-à-goutte recommandée.",
    },
    "Raspberry___healthy": {
        "fr": "Framboise — Saine ✅",
        "plante": "Framboise 🫐",
        "maladie": None,
        "niveau": "healthy",
        "description": "Framboisier en bonne santé.",
        "traitement": "Aucun traitement requis.",
        "conseil": "Tailler les cannes fruitées après récolte. Paillage du sol recommandé.",
    },
    "Soybean___healthy": {
        "fr": "Soja — Sain ✅",
        "plante": "Soja 🌱",
        "maladie": None,
        "niveau": "healthy",
        "description": "Plant de soja en bonne santé.",
        "traitement": "Aucun traitement requis.",
        "conseil": "Inoculation rhizobium recommandée. Rotation maïs-soja classique.",
    },
    "Squash___Powdery_mildew": {
        "fr": "Courge — Oïdium",
        "plante": "Courge 🎃",
        "maladie": "Oïdium",
        "niveau": "sick",
        "description": "Podosphaera xanthii. Poudre blanche farineuse sur la face supérieure des feuilles.",
        "traitement": "Soufre mouillable ou bicarbonate dilué. Fongicide systémique si généralisé.",
        "conseil": "Aération. Éviter excès d'azote. Variétés tolérantes disponibles.",
    },
    "Strawberry___Leaf_scorch": {
        "fr": "Fraise — Brûlure des feuilles",
        "plante": "Fraise 🍓",
        "maladie": "Brûlure des feuilles",
        "niveau": "sick",
        "description": "Diplocarpon earlianum. Petites taches pourpres à brun sur feuilles, sans tache centrale pâle.",
        "traitement": "Captane ou myclobutanil. Éliminer les feuilles infectées.",
        "conseil": "Éviter humidité persistante. Renouveler les plants tous les 3–4 ans.",
    },
    "Strawberry___healthy": {
        "fr": "Fraise — Saine ✅",
        "plante": "Fraise 🍓",
        "maladie": None,
        "niveau": "healthy",
        "description": "Fraisier en bonne santé.",
        "traitement": "Aucun traitement requis.",
        "conseil": "Paillis pour garder l'humidité et éviter les éclaboussures de terre.",
    },
    "Tomato___Bacterial_spot": {
        "fr": "Tomate — Tache bactérienne",
        "plante": "Tomate 🍅",
        "maladie": "Tache bactérienne",
        "niveau": "sick",
        "description": "Xanthomonas spp. Petites taches aqueuses, puis nécrotiques entourées d'un halo jaune.",
        "traitement": "Cuivre + mancozèbe dès les premiers symptômes. Retirer feuilles infectées.",
        "conseil": "Rotation 2–3 ans. Arrosage au sol uniquement. Désinfection des outils.",
    },
    "Tomato___Early_blight": {
        "fr": "Tomate — Alternariose",
        "plante": "Tomate 🍅",
        "maladie": "Alternariose",
        "niveau": "sick",
        "description": "Alternaria solani. Taches brunes concentriques en cible, anneau jaune autour.",
        "traitement": "Chlorothalonil ou azoxystrobine. Supprimer feuilles basses infectées.",
        "conseil": "Paillis pour éviter éclaboussures. Arrosage matinal.",
    },
    "Tomato___Late_blight": {
        "fr": "Tomate — Mildiou",
        "plante": "Tomate 🍅",
        "maladie": "Mildiou (Phytophthora infestans)",
        "niveau": "critical",
        "description": "Phytophthora infestans. Taches huileuses irrégulières, duvet blanc sous les feuilles. Extrêmement contagieux.",
        "traitement": "URGENCE : fongicide systémique (métalaxyl + cuivre). Arracher plants très atteints.",
        "conseil": "Abri en cas de pluie. Brûler les débris. Ne jamais composter. Rotation stricte.",
    },
    "Tomato___Leaf_Mold": {
        "fr": "Tomate — Moisissure des feuilles",
        "plante": "Tomate 🍅",
        "maladie": "Moisissure des feuilles (Cladosporiose)",
        "niveau": "sick",
        "description": "Passalora fulva. Face supérieure jaune, face inférieure veloutée olive à brun.",
        "traitement": "Mancozèbe ou chlorothalonil. Améliorer drastiquement la ventilation.",
        "conseil": "Humidité relative < 85%. Espacer les plants. Serre bien ventilée.",
    },
    "Tomato___Septoria_leaf_spot": {
        "fr": "Tomate — Septoriose",
        "plante": "Tomate 🍅",
        "maladie": "Septoriose",
        "niveau": "sick",
        "description": "Septoria lycopersici. Petites taches circulaires blanches à centre gris, nombreux points noirs.",
        "traitement": "Cuivre ou chlorothalonil. Supprimer feuilles basses au moindre symptôme.",
        "conseil": "Éviter arrosage foliaire. Rotation des cultures. Tuteurage.",
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "fr": "Tomate — Acariens tétranyques",
        "plante": "Tomate 🍅",
        "maladie": "Infestation d'acariens (Tetranychus urticae)",
        "niveau": "sick",
        "description": "Acarien Tetranychus urticae. Décoloration en mosaïque bronze, toiles fines sous les feuilles.",
        "traitement": "Acaricide (abamectine). Savon insecticide bio. Prédateurs biologiques (Phytoseiulus).",
        "conseil": "Hygrométrie élevée défavorable. Surveiller régulièrement la face inférieure.",
    },
    "Tomato___Target_Spot": {
        "fr": "Tomate — Tache en cible",
        "plante": "Tomate 🍅",
        "maladie": "Tache en cible (Corynespora)",
        "niveau": "sick",
        "description": "Corynespora cassiicola. Taches concentriques brun-tan sur feuilles et fruits.",
        "traitement": "Azoxystrobine ou difénoconazole.",
        "conseil": "Bonne ventilation. Éliminer débris végétaux. Rotation des cultures.",
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "fr": "Tomate — Virus de l'enroulement jaune (TYLCV)",
        "plante": "Tomate 🍅",
        "maladie": "Virus TYLCV",
        "niveau": "critical",
        "description": "Geminiviridae transmis par Bemisia tabaci. Feuilles en cuillère, chlorose marginale. INCURABLE.",
        "traitement": "Aucun traitement curatif. Insecticide contre les aleurodes (vecteur). Filet insectproof.",
        "conseil": "Variétés résistantes TYLCV disponibles. Éliminer plants atteints sans tarder. Quarantaine.",
    },
    "Tomato___Tomato_mosaic_virus": {
        "fr": "Tomate — Virus de la mosaïque (ToMV)",
        "plante": "Tomate 🍅",
        "maladie": "Virus mosaïque (ToMV)",
        "niveau": "critical",
        "description": "Tobamovirus. Mosaïque vert clair/foncé, déformation foliaire et des fruits. Très contagieux par contact.",
        "traitement": "Aucun traitement curatif. Arracher et brûler immédiatement les plants infectés.",
        "conseil": "Hygiène stricte : laver les mains, désinfecter outils. Plants certifiés indemnes.",
    },
    "Tomato___healthy": {
        "fr": "Tomate — Saine ✅",
        "plante": "Tomate 🍅",
        "maladie": None,
        "niveau": "healthy",
        "description": "Plant de tomate en parfaite santé.",
        "traitement": "Aucun traitement requis.",
        "conseil": "Tuteurage et taille des gourmands. Fertilisation régulière calcium/magnésium.",
    },
}

# Seuil de confiance minimum pour considérer un résultat fiable
CONFIDENCE_THRESHOLD = 0.35

# ── Variables globales pour les modèles ───────────────────────────────────────
_hf_classifier = None
_local_model    = None
_yolo_model     = None
_use_local      = False

HF_MODEL_ID  = "dima806/plant_disease_image_detection"
LOCAL_PT_PATH = os.getenv('MODEL_PATH', 'model/plant_disease_efficientnet.pt')
YOLO_PATH     = os.getenv('YOLO_MODEL_PATH', 'model/modele_plantes.pt')


# ── Chargement du modèle HuggingFace ─────────────────────────────────────────
def _get_hf_classifier():
    global _hf_classifier
    if _hf_classifier is not None:
        return _hf_classifier
    try:
        import torch
        from transformers import pipeline
        device = 0 if torch.cuda.is_available() else -1
        print(f"📥 Chargement HuggingFace : {HF_MODEL_ID} (GPU={'oui' if device==0 else 'non'})…")
        _hf_classifier = pipeline(
            "image-classification",
            model=HF_MODEL_ID,
            device=device,
            top_k=5,
        )
        print("✅ Modèle HuggingFace chargé avec succès")
        return _hf_classifier
    except Exception as e:
        print(f"⚠️  Impossible de charger HuggingFace ({e})")
        return None


# ── Chargement du modèle local (EfficientNet entraîné) ────────────────────────
def _get_local_model():
    global _local_model, _use_local
    if _local_model is not None:
        return _local_model
    if not os.path.exists(LOCAL_PT_PATH):
        return None
    try:
        import torch
        from torchvision.models import efficientnet_b4, EfficientNet_B4_Weights
        import torch.nn as nn

        ckpt = torch.load(LOCAL_PT_PATH, map_location='cpu')
        class_names = ckpt.get('class_names', list(CLASS_INFO.keys()))
        num_classes = ckpt.get('num_classes', len(class_names))

        model = efficientnet_b4(weights=None)
        in_feat = model.classifier[1].in_features
        model.classifier = nn.Sequential(nn.Dropout(0.4), nn.Linear(in_feat, num_classes))
        model.load_state_dict(ckpt['model_state_dict'])
        model.eval()
        _local_model = (model, class_names)
        _use_local = True
        print(f"✅ Modèle local EfficientNet chargé : {LOCAL_PT_PATH} ({num_classes} classes)")
        return _local_model
    except Exception as e:
        print(f"⚠️  Modèle local non chargeable ({e})")
        return None


# ── Chargement YOLO (fallback) ────────────────────────────────────────────────
def _get_yolo():
    global _yolo_model
    if _yolo_model is not None:
        return _yolo_model
    if not os.path.exists(YOLO_PATH):
        return None
    try:
        from ultralytics import YOLO
        _yolo_model = YOLO(YOLO_PATH)
        print(f"✅ Fallback YOLO chargé : {YOLO_PATH}")
        return _yolo_model
    except Exception as e:
        print(f"⚠️  YOLO non disponible ({e})")
        return None


# ── Inference principale ──────────────────────────────────────────────────────
def run_inference(img_path):
    """
    Point d'entrée principal.
    Retourne un dict avec : label, confidence, all_predictions, disease_info
    """
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Image introuvable : {img_path}")

    # 1. Modèle local EfficientNet (le plus rapide si disponible)
    local = _get_local_model()
    if local is not None:
        return _infer_local(img_path, local)

    # 2. HuggingFace ViT (ne nécessite aucun entraînement local)
    hf = _get_hf_classifier()
    if hf is not None:
        return _infer_hf(img_path, hf)

    # 3. Fallback YOLO (modèle de détection d'objets)
    yolo = _get_yolo()
    if yolo is not None:
        return _infer_yolo(img_path, yolo)

    raise RuntimeError(
        "Aucun modèle disponible. "
        "Lancez 'python train_model.py' pour entraîner le modèle local, "
        "ou installez 'pip install transformers' pour le modèle HuggingFace."
    )


# ── Inférence HuggingFace ─────────────────────────────────────────────────────
def _infer_hf(img_path, classifier):
    img  = Image.open(img_path).convert("RGB")
    preds = classifier(img)           # list of {label, score}

    best  = preds[0]
    label = best['label']
    conf  = float(best['score'])

    return _build_response(label, conf, preds)


# ── Inférence modèle local EfficientNet ──────────────────────────────────────
def _infer_local(img_path, model_tuple):
    import torch
    import torch.nn.functional as F
    from torchvision import transforms

    model, class_names = model_tuple

    tf = transforms.Compose([
        transforms.Resize(420),
        transforms.CenterCrop(380),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    img    = Image.open(img_path).convert("RGB")
    tensor = tf(img).unsqueeze(0)

    with torch.no_grad():
        logits = model(tensor)
        probs  = F.softmax(logits, dim=1)[0]

    top5_idx  = probs.argsort(descending=True)[:5].tolist()
    top5_preds = [{'label': class_names[i], 'score': float(probs[i])} for i in top5_idx]

    best  = top5_preds[0]
    label = best['label']
    conf  = best['score']

    return _build_response(label, conf, top5_preds)


# ── Inférence YOLO (fallback) ─────────────────────────────────────────────────
def _infer_yolo(img_path, model):
    """Fallback YOLO — convertit les boîtes de détection en format classification."""
    # YOLO class index → label PlantVillage (ordre original du dataset)
    YOLO_CLASS_MAP = {
        0:  "Tomato___Bacterial_spot",
        1:  "Tomato___Early_blight",
        2:  "Tomato___Late_blight",
        3:  "Tomato___Leaf_Mold",
        4:  "Tomato___Septoria_leaf_spot",
        5:  "Tomato___Spider_mites Two-spotted_spider_mite",
        6:  "Tomato___Target_Spot",
        7:  "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        8:  "Tomato___Tomato_mosaic_virus",
        9:  "Tomato___healthy",
        10: "Apple___Apple_scab",
        11: "Apple___Black_rot",
        12: "Apple___Cedar_apple_rust",
        13: "Apple___healthy",
        14: "Blueberry___healthy",
        15: "Cherry_(including_sour)___Powdery_mildew",
        16: "Cherry_(including_sour)___healthy",
        17: "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
        18: "Corn_(maize)___Common_rust_",
        19: "Corn_(maize)___Northern_Leaf_Blight",
        20: "Corn_(maize)___healthy",
        21: "Grape___Black_rot",
        22: "Grape___Esca_(Black_Measles)",
        23: "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
        24: "Grape___healthy",
        25: "Orange___Haunglongbing_(Citrus_greening)",
        26: "Peach___Bacterial_spot",
        27: "Peach___healthy",
        28: "Pepper,_bell___Bacterial_spot",
        29: "Pepper,_bell___healthy",
        30: "Potato___Early_blight",
        31: "Potato___Late_blight",
        32: "Potato___healthy",
        33: "Raspberry___healthy",
        34: "Soybean___healthy",
        35: "Squash___Powdery_mildew",
        36: "Strawberry___Leaf_scorch",
        37: "Strawberry___healthy",
    }

    results  = model(img_path)
    boxes    = results[0].boxes if results else None

    if boxes is None or len(boxes) == 0:
        return _build_response(None, 0.0, [])

    confidences = boxes.conf.numpy()
    classes     = boxes.cls.numpy().astype(int)

    best_idx  = confidences.argmax()
    best_cls  = int(classes[best_idx])
    best_conf = float(confidences[best_idx])
    label     = YOLO_CLASS_MAP.get(best_cls, f"Classe_{best_cls}")

    preds = [{'label': YOLO_CLASS_MAP.get(int(classes[i]), f"Classe_{classes[i]}"),
               'score': float(confidences[i])} for i in range(len(classes))]

    return _build_response(label, best_conf, preds)


# ── Construction de la réponse finale ────────────────────────────────────────
def _build_response(label, confidence, all_predictions):
    info = CLASS_INFO.get(label) if label else None

    if info is None or confidence < CONFIDENCE_THRESHOLD:
        if confidence < CONFIDENCE_THRESHOLD:
            # Confiance trop faible = plante hors dataset probablement
            niveau = "unknown"
            maladie_fr = "Espèce non reconnue — Confiance insuffisante"
            conseil = (
                f"Le modèle a retourné une confiance de {confidence*100:.0f}% (seuil : {CONFIDENCE_THRESHOLD*100:.0f}%). "
                "La plante photographiée n'est probablement pas dans le dataset PlantVillage. "
                "Le modèle couvre 14 espèces végétales : tomate, pomme, maïs, raisin, pêche, "
                "poivron, pomme de terre, fraise, cerise, myrtille, orange, soja, courge, framboise."
            )
            info_out = {
                "fr": maladie_fr,
                "plante": "Inconnue",
                "maladie": "Espèce non reconnue",
                "niveau": niveau,
                "description": "Le modèle ne reconnaît pas cette espèce végétale avec une confiance suffisante.",
                "traitement": "Non applicable.",
                "conseil": conseil,
            }
        else:
            # Label connu mais pas dans notre map
            info_out = {
                "fr": (label or "").replace("___", " — ").replace("_", " "),
                "plante": "Inconnue",
                "maladie": label or "Inconnue",
                "niveau": "sick",
                "description": f"Détection : {label}",
                "traitement": "Consulter un agronome.",
                "conseil": "Résultat présent mais non référencé dans notre base. Analyse approfondie recommandée.",
            }
    else:
        info_out = info

    return {
        "label":           label,
        "confidence":      round(confidence, 4),
        "all_predictions": all_predictions[:5],
        "disease_info":    info_out,
    }
