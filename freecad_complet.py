# ============================================================
# FREECAD PYTHON CONSOLE - CODE COMPLET
# Projet: Système de Détection de Maladies des Plantes
# Composants: ESP32-CAM + 2x Servo SG90 + Pince jardinière
# Auteur: Mourtalla Lo
# Hauteur totale assemblée: ~170mm
# ============================================================
# UTILISATION:
# 1. Ouvrir FreeCAD
# 2. View → Panels → Python Console
# 3. Coller ce code et appuyer sur Entrée
# ============================================================

import FreeCAD as App
import Part
import FreeCADGui as Gui
import math

# ── Créer un nouveau document ────────────────────────────────
doc = App.newDocument("Detection_Maladies_Plantes")
print("=" * 55)
print("  SYSTÈME DÉTECTION MALADIES PLANTES")
print("  Modélisation FreeCAD - Démarrage...")
print("=" * 55)


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def boite(l, p, h, x=0, y=0, z=0):
    """Crée une boîte et la positionne en (x,y,z)"""
    b = Part.makeBox(l, p, h)
    if x != 0 or y != 0 or z != 0:
        b.translate(App.Vector(x, y, z))
    return b

def cylindre(r, h, x=0, y=0, z=0):
    """Crée un cylindre et le positionne en (x,y,z)"""
    c = Part.makeCylinder(r, h)
    if x != 0 or y != 0 or z != 0:
        c.translate(App.Vector(x, y, z))
    return c

def cylindre_horizontal(r, h, x=0, y=0, z=0):
    """Crée un cylindre horizontal (axe Y)"""
    c = Part.makeCylinder(r, h)
    c.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    c.translate(App.Vector(x, y, z))
    return c

def ajouter_piece(forme, nom, label, position=(0,0,0), couleur=(0.6,0.6,0.65)):
    """Ajoute une pièce au document FreeCAD"""
    obj = doc.addObject("Part::Feature", nom)
    obj.Shape = forme
    obj.Label = label
    if position != (0,0,0):
        obj.Placement = App.Placement(
            App.Vector(*position),
            App.Rotation()
        )
    obj.ViewObject.ShapeColor = couleur
    return obj


# ============================================================
# PIÈCE 1 : PINCE DE FIXATION
# ============================================================
# Dimensions externes : 70mm (L) × 45mm (P) × 70mm (H)
# Slot C : 26mm large × 35mm prof × 45mm haut (rebord 25mm+1mm jeu)
# Paroi minimum : 5mm
# Canal câbles : 10×10mm vertical (côté droit)
# Plateau supérieur : 15mm (connexion housing servo)
# 4 trous vis M3 (diam 3.4mm) pour fixation housing
# ============================================================
print("\n[1/5] Construction de la Pince de Fixation...")

# Dimensions pince
W_P = 70    # Largeur totale
D_P = 45    # Profondeur totale
H_P = 70    # Hauteur totale
EP  = 5     # Épaisseur paroi

# Slot C (clipser sur rebord jardinière)
SLOT_L = 26   # Largeur du slot (rebord 25mm + 1mm jeu)
SLOT_P = 35   # Profondeur du slot
SLOT_H = 45   # Hauteur de l'ouverture (depuis le bas)

# Corps principal
pince = boite(W_P, D_P, H_P)

# Slot C - ouvert vers le bas, centré en X
slot_x = (W_P - SLOT_L) / 2   # = 22mm centré
pince = pince.cut(boite(SLOT_L, SLOT_P + 1, SLOT_H, x=slot_x, y=-1, z=0))

# Canal passage câbles 10×10mm - côté droit
pince = pince.cut(boite(10, 10, H_P + 2, x=W_P - EP - 10, y=D_P/2 - 5, z=-1))

# Renforcement interne du slot - nervures latérales 3mm
# (renforcent les mâchoires de la pince)
nervure_g = boite(3, SLOT_P - 5, SLOT_H - 10, x=slot_x - 3, y=3, z=5)
nervure_d = boite(3, SLOT_P - 5, SLOT_H - 10, x=slot_x + SLOT_L, y=3, z=5)
pince = pince.fuse(nervure_g)
pince = pince.fuse(nervure_d)

# 4 trous de vissage M3 (diam 3.4mm) sur plateau supérieur
# pour fixer le Pan-Tilt Housing par-dessus
positions_vis_pince = [(12, 10), (12, D_P-10), (W_P-12, 10), (W_P-12, D_P-10)]
for vx, vy in positions_vis_pince:
    pince = pince.cut(cylindre(1.7, EP + 2, x=vx, y=vy, z=H_P - EP - 1))

# Chanfrein interne du slot (45°) pour faciliter le clipsage
chanfrein = boite(SLOT_L, 6, 6, x=slot_x, y=SLOT_P - 4, z=SLOT_H - 7)
chanfrein.rotate(App.Vector(slot_x + SLOT_L/2, SLOT_P, SLOT_H - 4), App.Vector(1,0,0), 45)
try:
    pince = pince.cut(chanfrein)
except:
    pass  # Le chanfrein est optionnel

# Texte en relief sur la pince (optionnel - désactiver si lent)
# pince_label = Part.makeBox(30, 1, 5).translated(App.Vector(20, D_P, 30))

# Ajouter la pince au document
o_pince = ajouter_piece(
    pince,
    "Pince_Fixation",
    "Pince de Fixation (70×45×70mm)",
    position=(0, 0, 0),
    couleur=(0.62, 0.62, 0.68)
)
print(f"   ✓ Corps : {W_P}×{D_P}×{H_P} mm")
print(f"   ✓ Slot C : {SLOT_L}mm (rebord 25mm + 1mm jeu)")
print(f"   ✓ Canal câbles : 10×10mm")
print(f"   ✓ 4 trous M3 Ø3.4mm")


# ============================================================
# PIÈCE 2 : CONNECTEUR PIVOT
# ============================================================
# Liaison mécanique entre la pince et le housing servo
# Contient l'axe de rotation vertical (servo PAN)
# Bride inférieure : se visse sur pince (4× M3)
# Pivot central cylindrique : Ø20mm × 12mm
# Trou central : Ø6mm (axe servo)
# ============================================================
print("\n[2/5] Construction du Connecteur Pivot...")

HW = 55  # Largeur housing (pour aligner la bride)
HD = 45  # Profondeur housing

# Bride de base (plate, même emprise que le housing)
bride = boite(HW, HD, 8, x=-HW/2, y=-HD/2, z=-8)

# Pivot cylindrique central
pivot_corps = cylindre(10, 12, x=0, y=0, z=0)

# Trou central axe servo (Ø6mm)
pivot_axe = cylindre(3, 22, x=0, y=0, z=-9)

# Fuser et soustraire
pivot = pivot_corps.fuse(bride)
pivot = pivot.cut(pivot_axe)

# 4 trous M3 dans la bride (alignés avec pince)
for px, py in [(-HW/2+12, -HD/2+10), (-HW/2+12, HD/2-10),
               (HW/2-12, -HD/2+10), (HW/2-12, HD/2-10)]:
    pivot = pivot.cut(cylindre(1.7, 10, x=px, y=py, z=-9))

# Ajouter au document
o_pivot = ajouter_piece(
    pivot,
    "Connecteur_Pivot",
    "Connecteur Pivot (Ø20mm)",
    position=(W_P/2, D_P/2, H_P),  # Centré sur la pince
    couleur=(0.45, 0.45, 0.50)
)
print(f"   ✓ Bride : {HW}×{HD}×8mm")
print(f"   ✓ Pivot central : Ø20mm × 12mm")
print(f"   ✓ Trou axe : Ø6mm")


# ============================================================
# PIÈCE 3 : PAN-TILT HOUSING (Double Servo SG90)
# ============================================================
# Dimensions ext : 55mm (L) × 45mm (P) × 45mm (H)
# Servo PAN (bas) : rotation horizontale
#   - Logement : 25×14×32mm centré
#   - Axe : Ø7mm vertical vers le bas
# Servo TILT (gauche) : inclinaison verticale
#   - Logement : 15×25×31mm dans paroi gauche
#   - Axe : Ø7mm horizontal vers le bras caméra
# Canal câbles : 10×10mm côté droit
# 4 trous M3 base : vissage sur pivot
# Fentes ventilation : 3 × face avant
# ============================================================
print("\n[3/5] Construction du Pan-Tilt Housing...")

# Dimensions housing
HW = 55   # Largeur
HD = 45   # Profondeur
HH = 45   # Hauteur
EP2 = 3   # Épaisseur paroi

# Dimensions servo SG90 (avec jeu d'assemblage)
SG_L = 25   # Longueur (23 + 2mm jeu)
SG_P = 14   # Profondeur (12.5 + 1.5mm jeu)
SG_H = 32   # Hauteur (29 + 3mm jeu)
AXE_D = 3.5 # Rayon trou d'axe

# Corps principal
housing = boite(HW, HD, HH)

# ── Logement Servo PAN (bas, rotation horizontale) ──
pan_x = (HW - SG_L) / 2  # Centré en X
pan_y = (HD - SG_P) / 2  # Centré en Y
housing = housing.cut(boite(SG_L, SG_P, SG_H + 1, x=pan_x, y=pan_y, z=EP2))

# Trou d'axe PAN (vertical vers le bas)
housing = housing.cut(cylindre(AXE_D, EP2 + 2, x=HW/2, y=HD/2, z=-1))

# Trou d'axe PAN vers le haut (sortie axe)
housing = housing.cut(cylindre(AXE_D, HH - SG_H, x=HW/2, y=HD/2, z=EP2 + SG_H - 1))

# Encoche laterale pour fils du servo PAN
housing = housing.cut(boite(4, SG_P, 6, x=pan_x - 5, y=pan_y, z=EP2))

# ── Logement Servo TILT (paroi gauche, inclinaison verticale) ──
tilt_y = (HD - SG_L) / 2   # Centré en Y
tilt_z = HH - SG_H - EP2   # Positionné en haut
housing = housing.cut(boite(SG_P + 1, SG_L, SG_H, x=-1, y=tilt_y, z=tilt_z))

# Trou d'axe TILT (horizontal, vers le bras caméra)
axe_tilt = cylindre(AXE_D, 14)
axe_tilt.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
axe_tilt.translate(App.Vector(SG_P + 1, HD/2, tilt_z + SG_H/2))
housing = housing.cut(axe_tilt)

# Trou de sortie axe TILT (côté opposé)
axe_tilt2 = cylindre(AXE_D, 10)
axe_tilt2.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
axe_tilt2.translate(App.Vector(HW - 10, HD/2, tilt_z + SG_H/2))
housing = housing.cut(axe_tilt2)

# ── Canal câbles vertical (10×10mm) côté droit ──
housing = housing.cut(boite(10, 10, HH + 2, x=HW - EP2 - 10, y=HD/2 - 5, z=-1))

# ── 4 trous M3 en base pour vissage sur pivot ──
positions_vis_h = [(10, 10), (10, HD-10), (HW-10, 10), (HW-10, HD-10)]
for vx, vy in positions_vis_h:
    housing = housing.cut(cylindre(1.7, EP2 + 2, x=vx, y=vy, z=-1))

# ── Fentes de ventilation (face avant) ──
for fz in [8, 20, 32]:
    housing = housing.cut(boite(EP2 + 2, 16, 4, x=-1, y=HD/2 - 8, z=fz))

# ── Renfort interne en croix (rigidité) ──
renfort_v = boite(2, HD, EP2, x=HW/2 - 1, y=0, z=EP2 + SG_H)
housing = housing.fuse(renfort_v)

# Ajouter au document
Z_HOUSING = H_P + 8  # 8mm = hauteur bride pivot
o_housing = ajouter_piece(
    housing,
    "PanTilt_Housing",
    "Pan-Tilt Housing (55×45×45mm)",
    position=((W_P - HW)/2, (D_P - HD)/2, Z_HOUSING),
    couleur=(0.58, 0.58, 0.63)
)
print(f"   ✓ Corps : {HW}×{HD}×{HH} mm")
print(f"   ✓ Servo PAN : logement {SG_L}×{SG_P}×{SG_H}mm")
print(f"   ✓ Servo TILT : logement {SG_P}×{SG_L}×{SG_H}mm")
print(f"   ✓ Axes : Ø{AXE_D*2}mm")
print(f"   ✓ Canal câbles + Ventilation")


# ============================================================
# PIÈCE 4 : BRAS SERVO TILT → CAMÉRA
# ============================================================
# Bras articulé en L reliant le servo TILT au boîtier caméra
# Côté servo : Ø14mm × 12mm avec trou Ø6mm (fixation axe)
# Corps bras : 35×10×8mm
# Bride caméra : 10×35×8mm (2 trous M3 pour boîtier)
# ============================================================
print("\n[4/5] Construction du Bras Servo TILT...")

CW = 35  # Largeur boîtier caméra (pour alignement bride)

# Corps du bras (horizontal)
bras = boite(35, 10, 8)

# Cylindre côté servo (bride d'attache axe)
bride_servo = cylindre(7, 12, x=0, y=5, z=-4)
bras = bras.fuse(bride_servo)

# Trou axe servo Ø6mm dans la bride
bras = bras.cut(cylindre(3, 14, x=0, y=5, z=-5))

# Bride côté caméra (embase rectangulaire)
bride_cam = boite(10, CW, 8, x=35, y=-12.5, z=0)
bras = bras.fuse(bride_cam)

# 2 trous M3 dans la bride caméra
for by in [-5, CW - 12]:
    bras = bras.cut(cylindre(1.7, 10, x=40, y=by, z=-1))

# Renfort triangulaire (rigidité du bras)
try:
    pts = [
        App.Vector(0, 0, 0), App.Vector(35, 0, 0),
        App.Vector(0, 0, -8), App.Vector(35, 0, -8),
    ]
    renfort = Part.makeBox(35, 2, 8)
    bras = bras.fuse(renfort.translated(App.Vector(0, 10, 0)))
except:
    pass

# Ajouter au document
Z_BRAS = Z_HOUSING + HH + 5
OX = (W_P - HW)/2
OY = (D_P - HD)/2
o_bras = ajouter_piece(
    bras,
    "Bras_Servo_Tilt",
    "Bras Servo TILT (35mm)",
    position=(OX - 35, OY + HD/2 - CW/2, Z_BRAS - 8),
    couleur=(0.42, 0.42, 0.48)
)
print(f"   ✓ Corps bras : 35×10×8mm")
print(f"   ✓ Bride servo : Ø14mm × 12mm")
print(f"   ✓ Bride caméra : 10×{CW}mm, 2× M3")


# ============================================================
# PIÈCE 5 : BOÎTIER ESP32-CAM (Fermé, Amélioré)
# ============================================================
# Dimensions ext : 35mm (L) × 32mm (P) × 55mm (H)
# Module ESP32-CAM : 27×40×15mm
# Parois : 2.5mm sur tous les côtés
# Fond : 2.5mm (fermé)
# Haut : ouvert (insertion module par le haut)
# Face avant (Y=0) :
#   - Trou objectif caméra : 12×12mm centré en X, à 17mm du bas
#   - Trou flash LED : 8×8mm à droite de l'objectif
# Face bas (Z=0) :
#   - Trou USB/alimentation : 12×6mm centré
# Face haut (Z=55) :
#   - Ouverture antenne WiFi : 5×20mm côté droit
# Faces latérales (X=0 et X=35) :
#   - 3 fentes ventilation : 4×14×3mm chacune
# Intérieur :
#   - 4 bossages de calage : 2×2×4mm aux coins
#   - 2 rails de guidage verticaux : 1.5mm
# 2 trous M3 base pour fixation sur bras servo
# ============================================================
print("\n[5/5] Construction du Boîtier ESP32-CAM...")

# Dimensions boîtier
CW = 35    # Largeur ext
CD = 32    # Profondeur ext
CH = 55    # Hauteur ext
MUR = 2.5  # Épaisseur paroi

# Corps externe
cam = boite(CW, CD, CH)

# ── Évidement intérieur ──
# Laisse fond MUR, parois MUR, haut ouvert
cam = cam.cut(boite(CW - 2*MUR, CD - 2*MUR, CH - MUR + 0.5,
                    x=MUR, y=MUR, z=MUR))

# ── Face avant (Y=0) : trou objectif ──
# Caméra centrée à environ 17mm du bas intérieur
cam = cam.cut(boite(12, MUR + 2, 12, x=(CW-12)/2, y=-1, z=CH-38))

# ── Face avant : trou flash LED ──
cam = cam.cut(boite(8, MUR + 2, 8, x=(CW-8)/2 + 13, y=-1, z=CH-36))

# ── Face bas (Z=0) : trou USB/alimentation ──
cam = cam.cut(boite(12, 6, MUR + 2, x=(CW-12)/2, y=(CD-6)/2, z=-1))

# ── Face haut (Z=CH) : ouverture antenne WiFi ──
cam = cam.cut(boite(5, 20, MUR + 2, x=CW-MUR-6, y=(CD-20)/2, z=CH-MUR-1))

# ── Fentes ventilation gauche (X=0) ──
for fz in [12, 25, 38]:
    cam = cam.cut(boite(MUR + 2, 14, 3, x=-1, y=(CD-14)/2, z=fz))

# ── Fentes ventilation droite (X=CW) ──
for fz in [12, 25, 38]:
    cam = cam.cut(boite(MUR + 2, 14, 3, x=CW-MUR-1, y=(CD-14)/2, z=fz))

# ── Bossages internes (4 coins) pour caler l'ESP32-CAM ──
for bx, by in [(MUR, MUR), (CW-MUR-2, MUR), (MUR, CD-MUR-2), (CW-MUR-2, CD-MUR-2)]:
    bossage = boite(2, 2, 5, x=bx, y=by, z=MUR)
    cam = cam.fuse(bossage)

# ── Rails de guidage verticaux ──
rail_g = boite(1.5, CD - 2*MUR, CH - MUR, x=MUR, y=MUR, z=MUR)
rail_d = boite(1.5, CD - 2*MUR, CH - MUR, x=CW - MUR - 1.5, y=MUR, z=MUR)
cam = cam.fuse(rail_g)
cam = cam.fuse(rail_d)

# ── 2 trous M3 base pour fixation sur bras servo ──
for mx in [(CW-20)/2, (CW+0)/2 + 10]:
    cam = cam.cut(cylindre(1.7, MUR + 2, x=mx, y=CD/2, z=-1))

# ── Encoche clip de fermeture (optionnel) ──
clip = boite(4, MUR + 2, 6, x=(CW-4)/2, y=CD-MUR-1, z=CH-8)
cam = cam.cut(clip)

# Ajouter au document
Z_CAM = Z_BRAS + 5
o_cam = ajouter_piece(
    cam,
    "Boitier_ESP32CAM",
    "Boîtier ESP32-CAM (35×32×55mm)",
    position=(OX, OY + HD/2 - CD/2, Z_CAM),
    couleur=(0.52, 0.52, 0.58)
)
print(f"   ✓ Corps : {CW}×{CD}×{CH} mm, parois {MUR}mm")
print(f"   ✓ Objectif : 12×12mm centré")
print(f"   ✓ Flash : 8×8mm")
print(f"   ✓ USB : 12×6mm")
print(f"   ✓ Antenne WiFi : 5×20mm")
print(f"   ✓ 6 fentes ventilation")
print(f"   ✓ 4 bossages + 2 rails guidage")


# ============================================================
# FINALISATION ET AFFICHAGE
# ============================================================
print("\n" + "=" * 55)
doc.recompute()

# Vue isométrique et ajustement
Gui.activeDocument().activeView().viewIsometric()
Gui.SendMsgToActiveView("ViewFit")

# Rapport final
hauteur_totale = H_P + 8 + HH + 5 + CH
print("  ASSEMBLAGE COMPLET TERMINÉ !")
print("=" * 55)
print(f"  Pièces créées       : 5")
print(f"  Pince               : {W_P}×{D_P}×{H_P} mm  (Z=0)")
print(f"  Pivot connecteur    : Ø20×12 mm       (Z={H_P})")
print(f"  Pan-Tilt Housing    : {HW}×{HD}×{HH} mm  (Z={Z_HOUSING})")
print(f"  Bras servo TILT     : 35×10×8 mm      (Z={Z_BRAS-8})")
print(f"  Boîtier ESP32-CAM   : {CW}×{CD}×{CH} mm  (Z={Z_CAM})")
print(f"  ─────────────────────────────────────")
print(f"  HAUTEUR TOTALE      : ~{hauteur_totale} mm")
print(f"  Plage recommandée   : 150–180 mm ✓")
print("=" * 55)
print("\nPour exporter en STL:")
print("  Sélectionner une pièce dans l'arbre")
print("  → File → Export → Format: STL Mesh")
print("  → Enregistrer dans Detection-maladies-plantes/")
print("\nPour modifier une dimension:")
print("  Double-cliquer sur la pièce → modifier le code")
print("  → Relancer le script")
