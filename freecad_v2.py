import FreeCAD as App, Part, FreeCADGui as Gui

doc = App.newDocument("Detection_Plantes_V2")

# ══════════════════════════════════════════════════════════════════
# DIMENSIONS RÉELLES (mesurées + jeu impression FDM PLA)
# SG90 corps : 22.5 × 11.8 × 22.7 mm
# ESP32-CAM  : PCB 40.5 × 27 mm, épaisseur 15mm, objectif Ø8mm
# Jeu logements : +0.5mm | jeu axes : +0.3mm
# ══════════════════════════════════════════════════════════════════

SG_L  = 23.0   # longueur corps servo + jeu
SG_W  = 12.3   # largeur corps servo + jeu
SG_H  = 23.2   # hauteur corps servo + jeu  (CORRIGÉ vs ancienne version)
AXE_D =  5.0   # Ø axe servo + jeu

CAM_L = 41.0   # longueur PCB ESP32-CAM + jeu
CAM_W = 27.5   # largeur PCB ESP32-CAM + jeu
CAM_D = 15.5   # épaisseur (profil) PCB + jeu
MUR   =  2.5   # épaisseur paroi boîtier

# ══════════════════════════════════════════════════════════════════
# PIÈCE 1 — PINCE DE FIXATION sur le pot  (70 × 45 × 70 mm)
# Se clippe sur le rebord du pot (25mm). Hauteur 70mm.
# ══════════════════════════════════════════════════════════════════
p = Part.makeBox(70, 45, 70)

# Slot C : s'ouvre vers le bas pour clipser le rebord 25mm
p = p.cut(Part.makeBox(26, 37, 55).translated(App.Vector(22, -1, 0)))

# Canal câbles 10×10mm (côté droit, toute la hauteur)
p = p.cut(Part.makeBox(10, 10, 72).translated(App.Vector(56, 17.5, -1)))

# 4 trous M3 en plateau supérieur pour fixer le support servo
for x, y in [(14,10),(14,35),(56,10),(56,35)]:
    p = p.cut(Part.makeCylinder(1.7, 8).translated(App.Vector(x, y, 63)))

# Nervures de renfort latérales (évite que la pince s'écarte)
r1 = Part.makeBox(3, 2, 55).translated(App.Vector(22, 36, 0))
r2 = Part.makeBox(3, 2, 55).translated(App.Vector(22, -2, 0))
r3 = Part.makeBox(3, 2, 55).translated(App.Vector(45, 36, 0))
r4 = Part.makeBox(3, 2, 55).translated(App.Vector(45, -2, 0))

o1 = doc.addObject("Part::Feature","Pince_Fixation")
o1.Shape = p
o1.ViewObject.ShapeColor = (0.6, 0.6, 0.65)
print("✓ Pièce 1 — Pince de fixation (70×45×70mm)")

# ══════════════════════════════════════════════════════════════════
# PIÈCE 2 — SUPPORT SERVO PAN  (70 × 45 × 50 mm)
# Contient le SG90. L'axe sort vers le haut → rotation gauche/droite.
# Se visse sur la pince avec 4 vis M3.
# ══════════════════════════════════════════════════════════════════
s = Part.makeBox(70, 45, 50)

# Logement SG90 centré (axe vertical = servo tourne le bras gauche/droite)
sx = (70 - SG_L) / 2
sy = (45 - SG_W) / 2
s = s.cut(Part.makeBox(SG_L, SG_W, SG_H + 3).translated(
    App.Vector(sx, sy, 50 - SG_H - 5)))

# Trou axe servo (sort par le dessus, centré)
s = s.cut(Part.makeCylinder(AXE_D/2, 20).translated(App.Vector(35, 22.5, 33)))

# Encoche câbles servo (3 fils sortent par le bas du logement)
s = s.cut(Part.makeBox(8, 4, 10).translated(App.Vector(31, 20.5, 50 - SG_H - 5 - 1)))

# Canal câbles 10×10mm (aligné avec la pince)
s = s.cut(Part.makeBox(10, 10, 52).translated(App.Vector(56, 17.5, -1)))

# 4 trous M3 base (alignés avec les trous de la pince)
for x, y in [(14,10),(14,35),(56,10),(56,35)]:
    s = s.cut(Part.makeCylinder(1.7, 6).translated(App.Vector(x, y, -1)))

o2 = doc.addObject("Part::Feature","Support_Servo_PAN")
o2.Shape = s
o2.Placement = App.Placement(App.Vector(0, 0, 70), App.Rotation())
o2.ViewObject.ShapeColor = (0.55, 0.55, 0.60)
print("✓ Pièce 2 — Support Servo PAN (70×45×50mm)")

# ══════════════════════════════════════════════════════════════════
# PIÈCE 3 — BRAS + BOÎTIER ESP32-CAM  (pièce mobile, fixée sur l'axe)
# Hub bas : se fixe sur l'axe servo (Ø5mm)
# Bras vertical : monte à 80mm de hauteur
# Boîtier en haut : tient l'ESP32-CAM, objectif orienté vers le bas
# ══════════════════════════════════════════════════════════════════

# — Hub circulaire (fixé sur l'axe servo sortant du support) —
hub = Part.makeCylinder(12, 8)
hub = hub.cut(Part.makeCylinder(AXE_D/2, 10))   # trou central axe
# 2 petits trous M2 pour vis de blocage de l'axe
hub = hub.cut(Part.makeCylinder(1.2, 14).translated(App.Vector(0, 10, 4)))
hub = hub.cut(Part.makeCylinder(1.2, 14).translated(App.Vector(0,-10, 4)))

# — Bras vertical (relie hub à boîtier caméra) —
bras = Part.makeBox(10, 10, 78).translated(App.Vector(-5, -5, 0))

# — Boîtier ESP32-CAM (objectif pointe vers le bas pour photographier les plantes) —
BW = CAM_L + 2*MUR   # ~46mm largeur ext
BD = CAM_D + 2*MUR   # ~20mm profondeur ext
BH = CAM_W + 2*MUR   # ~32mm hauteur ext
ARM_H = 78

cam_ext = Part.makeBox(BW, BD, BH).translated(App.Vector(-BW/2, -BD/2, ARM_H))

# Évidement intérieur (accueille le PCB)
cam_int = Part.makeBox(CAM_L, CAM_D, CAM_W + 1).translated(
    App.Vector(-CAM_L/2, -CAM_D/2, ARM_H + MUR))
cam_ext = cam_ext.cut(cam_int)

# Trou objectif (face inférieure -Z, Ø10mm, centré X, décalé vers l'avant en Y)
lens = Part.makeCylinder(5, MUR + 2).translated(App.Vector(-6, -BD/2 + MUR + 3, ARM_H - 1))
cam_ext = cam_ext.cut(lens)

# Trou flash LED (Ø6mm à côté de l'objectif)
flash = Part.makeCylinder(3.5, MUR + 2).translated(App.Vector(8, -BD/2 + MUR + 3, ARM_H - 1))
cam_ext = cam_ext.cut(flash)

# Trou USB alimentation (face arrière +Y, centré)
usb = Part.makeBox(12, MUR + 2, 5).translated(App.Vector(-6, BD/2 - 1, ARM_H + MUR + 5))
cam_ext = cam_ext.cut(usb)

# Fentes ventilation latérales (3 fentes × 2 côtés)
for z_off in [4, 12, 20]:
    v1 = Part.makeBox(MUR + 2, 12, 2.5).translated(App.Vector(-BW/2 - 1, -6, ARM_H + MUR + z_off))
    v2 = Part.makeBox(MUR + 2, 12, 2.5).translated(App.Vector(BW/2 - MUR - 1, -6, ARM_H + MUR + z_off))
    cam_ext = cam_ext.cut(v1)
    cam_ext = cam_ext.cut(v2)

# Assemblage des 3 sous-pièces du bras
bras_complet = hub.fuse(bras).fuse(cam_ext)

o3 = doc.addObject("Part::Feature","Bras_Camera")
o3.Shape = bras_complet
# Positionné sur l'axe servo (x=35, y=22.5, z=70+50=120 → axe sort à z=120+33=153... centré)
o3.Placement = App.Placement(App.Vector(35, 22.5, 123), App.Rotation())
o3.ViewObject.ShapeColor = (0.5, 0.5, 0.55)
print("✓ Pièce 3 — Bras + Boîtier ESP32-CAM (bras 78mm + boîtier 32mm)")

# ══════════════════════════════════════════════════════════════════
# AFFICHAGE FINAL
# ══════════════════════════════════════════════════════════════════
doc.recompute()
Gui.activeDocument().activeView().viewIsometric()
Gui.SendMsgToActiveView("ViewFit")

print()
print("═══════════════════════════════════════════")
print("  ASSEMBLAGE V2 — 3 pièces séparées")
print("═══════════════════════════════════════════")
print("  Pince fixation  :  70mm  (bas)")
print("  Support servo   :  50mm  (milieu)")
print("  Bras + caméra   :  80mm  (haut, mobile)")
print("  ─────────────────────────")
print("  Hauteur totale  : ~200mm ✓")
print()
print("  Rotation servo PAN : ±60° gauche/droite")
print("  → Position gauche  : photo plante malade")
print("  → Position droite  : photo plante saine")
print()
print("  Pour exporter chaque pièce en STL :")
print("  Clic sur la pièce → File → Export → .stl")
print("═══════════════════════════════════════════")
