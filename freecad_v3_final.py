import FreeCAD as App, Part, FreeCADGui as Gui

# ╔══════════════════════════════════════════════════════════════╗
# ║  SYSTÈME DÉTECTION MALADIES PLANTES — V3 FINALE            ║
# ║  3 pièces  |  câbles cachés  |  dimensions réelles         ║
# ╚══════════════════════════════════════════════════════════════╝

doc = App.newDocument("PlantDetection_V3")

V = App.Vector

# ── 3 helpers propres, aucun rotate() ──────────────────────────
def box(W, D, H, x=0, y=0, z=0):
    return Part.makeBox(W, D, H).translated(V(x, y, z))

def cylZ(r, H, x=0, y=0, z=0):
    """Cylindre vertical (axe +Z)"""
    return Part.makeCylinder(r, H, V(x, y, z), V(0, 0, 1))

def cylY(r, H, x=0, y=0, z=0):
    """Cylindre horizontal (axe +Y) — pour trous face avant/arrière"""
    return Part.makeCylinder(r, H, V(x, y, z), V(0, 1, 0))

def cylX(r, H, x=0, y=0, z=0):
    """Cylindre horizontal (axe +X) — pour trous face gauche/droite"""
    return Part.makeCylinder(r, H, V(x, y, z), V(1, 0, 0))

# ── Dimensions réelles + jeux FDM PLA ──────────────────────────
SGL, SGW, SGH = 23.0, 12.3, 23.2   # SG90 corps + jeu 0.5mm
SGA = 5.0                            # Ø axe SG90 + jeu 0.3mm
CL,  CW,  CD  = 41.0, 27.5, 15.5   # ESP32-CAM PCB + jeu 0.5mm
MUR = 2.5
HP, HS = 72, 110                     # hauteurs pince et mât

print("=== Création pièce 1/3 — Pince ===")

# ══════════════════════════════════════════════════════════════
# PIÈCE 1 — PINCE DE FIXATION  90 × 48 × 72 mm
#   Clips sur le rebord du pot (16 mm = 15 mm pot + 1 mm jeu)
#   Canal câbles 8×8 mm intégré côté arrière
#   4× trous M3 en haut pour visser le mât
# ══════════════════════════════════════════════════════════════
PW, PD, PH = 90, 48, HP

p = box(PW, PD, PH)

# Slot C — rebord pot (centré en X, ouvert vers le bas)
p = p.cut(box(16, 24, 56,  37, -1,  0))

# Canal câbles 8×8 mm (côté arrière, toute la hauteur)
p = p.cut(box( 8,  8, PH+2, 77, 20, -1))

# 4 trous M3 plateau supérieur
for px, py in [(15,10),(15,38),(75,10),(75,38)]:
    p = p.cut(cylZ(1.7, 10, px, py, PH-9))

# Chanfrein d'entrée slot (facilite le clippage)
p = p.cut(box(20, 8, 7, 35, 16, 0))

# Allègements latéraux (économie matière)
p = p.cut(box(14, 20, 26, 13, 14, 38))
p = p.cut(box(14, 20, 26, 63, 14, 38))

o1 = doc.addObject("Part::Feature","P1_Pince_Fixation")
o1.Shape = p
o1.ViewObject.ShapeColor = (0.75, 0.42, 0.32)   # terracotta
print("✓ Pièce 1 — Pince 90×48×72 mm  (slot 16 mm, canal câbles 8×8)")

print("=== Création pièce 2/3 — Mât + Servo ===")

# ══════════════════════════════════════════════════════════════
# PIÈCE 2 — MÂT + SUPPORT SERVO  90 × 48 × 110 mm
#   Mât solide, servo SG90 logé en haut (axe sort par le dessus)
#   L'axe vertical → rotation gauche/droite du boîtier caméra
#   Canal câbles aligné avec la pince
#   Se visse sur la pince avec 4× M3
# ══════════════════════════════════════════════════════════════
MW, MD, MH = 90, 48, HS
lx = (MW - SGL) / 2       # ~33.5  (X départ logement servo)
ly = (MD - SGW) / 2       # ~17.8  (Y départ logement servo)
lz = MH - SGH - 4         # ~82.8  (Z départ logement servo)

m = box(MW, MD, MH)

# Logement corps SG90
m = m.cut(box(SGL, SGW, SGH+6, lx, ly, lz))

# Rainures pour les pattes latérales SG90 (2 × 5.5 mm de chaque côté)
m = m.cut(box(SGL + 11, SGW, 4, lx-5.5, ly, MH-4))

# Trou axe servo Ø5 mm (vertical, sort par le haut)
m = m.cut(cylZ(SGA/2, 22, MW/2, MD/2, MH-20))

# Dégagement corne servo Ø23 mm (5 mm de profondeur)
m = m.cut(cylZ(11.5, 6, MW/2, MD/2, MH-5))

# Sortie câbles servo (3 fils vers le bas, canal 10×8)
m = m.cut(box(10, MD/2+2, lz+8, MW/2-5, -1, 0))

# Canal câbles 8×8 mm (aligné avec pince)
m = m.cut(box(8, 8, MH+2, MW-13, MD/2-4, -1))

# 4 trous M3 base (vissage sur pince)
for px, py in [(15,10),(15,38),(75,10),(75,38)]:
    m = m.cut(cylZ(1.7, 12, px, py, -1))

# 2 trous M3 latéraux blocage servo (axe X)
sv_z = lz + SGH / 2       # Z centre du servo
m = m.cut(cylX(1.7, 10,  -1,      MD/2, sv_z))
m = m.cut(cylX(1.7, 10, MW-9,    MD/2, sv_z))

o2 = doc.addObject("Part::Feature","P2_Mat_Servo")
o2.Shape = m
o2.Placement = App.Placement(V(0, 0, HP), App.Rotation())
o2.ViewObject.ShapeColor = (0.20, 0.20, 0.23)   # gris anthracite
print("✓ Pièce 2 — Mât+Servo 90×48×110 mm  (SG90 logé, axe sort en haut)")

print("=== Création pièce 3/3 — Boîtier ESP32-CAM ===")

# ══════════════════════════════════════════════════════════════
# PIÈCE 3 — BOÎTIER ESP32-CAM  ≈ 46 × 21 × 33 mm
#   Monte directement sur l'axe + corne du servo SG90
#   Tourne avec le servo (±75°) pour viser chaque plante
#   Objectif OV2640 Ø11 mm sur face avant (−Y)
#   Flash LED Ø7 mm, fente USB, antenne WiFi, ventilation
#   Câbles passent par trou central Ø5 mm (même canal que l'axe)
# ══════════════════════════════════════════════════════════════
BW = CL + 2*MUR    # ~46 mm  largeur (axe X)
BD = CD + 2*MUR    # ~20.5 mm profondeur (axe Y, face objectif vers −Y)
BH = CW + 2*MUR    # ~32.5 mm hauteur (axe Z)

# Corps boîtier  — centré en X, face arrière en Y=0, face avant en Y=−BD
cam = box(BW, BD, BH,  -BW/2, -BD, 2)

# Évidement intérieur PCB (laisser parois 2.5 mm)
cam = cam.cut(box(CL, CD, CW+2,  -CL/2, -BD+MUR, 2+MUR))

# ── Trou OBJECTIF OV2640 Ø11 mm ──────────────────────────────
# Face avant (Y = −BD), axe horizontal Y → cylindre cylY
# Objectif décentré : X = −7 mm, centré en hauteur Z
cam = cam.cut(cylY(5.5, BD+2,  -7.0, -BD-1, 2+BH/2))

# ── Trou FLASH LED Ø7 mm (à côté objectif) ───────────────────
cam = cam.cut(cylY(3.5, BD+2,   4.0, -BD-1, 2+BH/2))

# ── Fente USB / alimentation (face droite +X) ─────────────────
cam = cam.cut(box(MUR+2, 10, 5.5,   BW/2-1,   -BD+MUR+2, 2+MUR+3))

# ── Ouverture antenne WiFi (face gauche −X, haut) ─────────────
cam = cam.cut(box(MUR+2, BD-MUR, 8,  -BW/2-1,  -BD+MUR,   2+BH-10))

# ── Fentes ventilation × 3 (côté gauche et droit) ────────────
for i in range(3):
    fz = 2 + 4 + i*9
    cam = cam.cut(box(MUR+2, 12, 2.5,  -BW/2-1,     -BD+4, fz))
    cam = cam.cut(box(MUR+2, 12, 2.5,   BW/2-MUR-1,  -BD+4, fz))

# ── Trou axe servo central Ø5 mm (monte depuis en dessous) ───
cam = cam.cut(cylZ(SGA/2, 14, 0, 0, -1))

# ── 4 trous M2 corne servo (croix SG90, rayon 9 mm) ──────────
for hx, hy in [(-9, 0),(9, 0),(0, -9),(0, 9)]:
    cam = cam.cut(cylZ(1.15, 10, hx, hy, -1))

# ── Passage câbles (fond boîtier, communique avec canal mât) ──
cam = cam.cut(box(8, 8, MUR+2, -4, -4, -1))

o3 = doc.addObject("Part::Feature","P3_Boitier_ESP32CAM")
o3.Shape = cam
# Placé sur l'axe servo : centre du mât (MW/2, MD/2) à Z = HP+HS
o3.Placement = App.Placement(V(MW/2, MD/2, HP+HS), App.Rotation())
o3.ViewObject.ShapeColor = (0.10, 0.10, 0.12)   # noir mat (ESP32-CAM)
print(f"✓ Pièce 3 — Boîtier ESP32-CAM {BW:.0f}×{BD:.0f}×{BH:.0f} mm")
print(f"  Trou objectif Ø11 mm | Flash Ø7 mm | USB | Antenne | Ventilation")

# ══════════════════════════════════════════════════════════════
# AFFICHAGE FINAL
# ══════════════════════════════════════════════════════════════
doc.recompute()
Gui.activeDocument().activeView().viewIsometric()
Gui.SendMsgToActiveView("ViewFit")

print()
print("╔══════════════════════════════════════════════════════╗")
print("║   SYSTÈME DÉTECTION MALADIES PLANTES — V3 FINALE   ║")
print("╠══════════════════════════════════════════════════════╣")
print(f"║  ① Pince    90×48×{HP}mm   — terracotta             ║")
print(f"║  ② Mât      90×48×{HS}mm  — gris anthracite         ║")
print(f"║  ③ Boîtier  {BW:.0f}×{BD:.0f}×{BH:.0f}mm  — noir mat              ║")
print(f"║  Hauteur totale ~{HP+HS+int(BH)+2}mm au-dessus du rebord     ║")
print("╠══════════════════════════════════════════════════════╣")
print("║  Servo ±75° → plante malade (G) | plante saine (D) ║")
print("║  Câbles 100% cachés dans les canaux 8×8 mm          ║")
print("╠══════════════════════════════════════════════════════╣")
print("║  IMPRESSION PLA 0.20 mm :                           ║")
print("║  ① 40% infill + supports  ② 30%  ③ 25%             ║")
print("╠══════════════════════════════════════════════════════╣")
print("║  Export STL : sélectionner pièce → File → Export   ║")
print("╚══════════════════════════════════════════════════════╝")
