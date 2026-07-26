import FreeCAD as App
import Part
import FreeCADGui as Gui

# ╔══════════════════════════════════════════════════════════════╗
# ║  SUPPORT ARTICULÉ ESP32-CAM + SG90 — V4                    ║
# ║  Pièce 1 : Boîtier caméra 32×45×20mm + goulotte Ø12/Ø8    ║
# ║  Pièce 2 : Pince fixation U 42×20×38mm + logement SG90     ║
# ╚══════════════════════════════════════════════════════════════╝
# UTILISER : Macro → Macros → Créer → Coller → Exécuter
# NE PAS coller dans la console Python (multi-lignes = bug)

doc = App.newDocument("Support_ESP32CAM_SG90")
V = App.Vector

# ══════════════════════════════════════════════════════════════
# PIÈCE 1 — BOÎTIER CAMÉRA  32×45×20mm
#   Cavité PCB 28×41×8mm | Objectif Ø10mm
#   Goulotte Ø12ext / Ø8int × 40mm (passage câbles vers le bas)
# ══════════════════════════════════════════════════════════════
BW, BL, BH = 32.0, 45.0, 20.0   # largeur, longueur, hauteur

# RÈGLE : fusionner les solides BRUTS avant tout cut → géométrie valide
box_raw  = Part.makeBox(BW, BL, BH).translated(V(-BW/2, -BL/2, 0))
tube_raw = Part.makeCylinder(6.0, 40.0, V(0, 0, -40), V(0, 0, 1))
cam = box_raw.fuse(tube_raw)

# Cavité ESP32-CAM 28×41×8mm — ouverte par le haut
cam = cam.cut(Part.makeBox(28.4, 41.4, 9.0).translated(V(-14.2, -20.7, BH-8.5)))

# Trou objectif Ø10mm — face avant, axe horizontal Y
cam = cam.cut(Part.makeCylinder(5.0, BL+2, V(0, -BL/2-1, BH/2), V(0, 1, 0)))

# Canal interne goulotte Ø8mm — traverse toute la hauteur + tube
cam = cam.cut(Part.makeCylinder(4.0, BH+42, V(0, 0, -41), V(0, 0, 1)))

o1 = doc.addObject("Part::Feature", "Boitier_Camera")
o1.Shape = cam
o1.ViewObject.ShapeColor = (0.25, 0.25, 0.30)
print("OK Piece 1 — Boitier camera 32x45x20mm + goulotte Ø12/8 x40mm")

# ══════════════════════════════════════════════════════════════
# PIÈCE 2 — PINCE DE FIXATION  42×20×38mm
#   U-shape 22mm interne (rebord pot) ouverte vers le BAS
#   Logement SG90 23×13×25mm (par le HAUT, centré)
#   Vis de serrage M4 Ø4.2mm (latéral, bloque sur le rebord)
#   Trou axe servo Ø5mm (vertical, centré)
# ══════════════════════════════════════════════════════════════
PW, PD, PH = 42.0, 20.0, 38.0   # largeur, profondeur, hauteur
SLOT_W = 22.0                    # largeur interne U (rebord pot)
SLOT_H = 25.0                    # hauteur de l'encoche U

pince = Part.makeBox(PW, PD, PH)

# Évidement U — rebord pot 22mm, ouverte vers le bas
pince = pince.cut(Part.makeBox(SLOT_W, PD+2, SLOT_H+1).translated(V((PW-SLOT_W)/2, -1, -1)))

# Logement SG90 23×13×25mm — par le haut, centré
pince = pince.cut(Part.makeBox(23.5, 13.3, 26.0).translated(V((PW-23.5)/2, (PD-13.3)/2, PH-25.0)))

# Trou axe servo Ø5mm — vertical, centré, sort par le haut
pince = pince.cut(Part.makeCylinder(2.5, PH+2, V(PW/2, PD/2, -1), V(0, 0, 1)))

# Vis de serrage M4 Ø4.2mm — latéral, presse sur le rebord du pot
pince = pince.cut(Part.makeCylinder(2.1, PW+2, V(-1, PD/2, SLOT_H/2), V(1, 0, 0)))

o2 = doc.addObject("Part::Feature", "Pince_Fixation")
o2.Shape = pince
o2.Placement = App.Placement(V(50, 0, 0), App.Rotation())
o2.ViewObject.ShapeColor = (0.20, 0.40, 0.70)
print("OK Piece 2 — Pince U 42x20x38mm + SG90 + vis M4")

# ══════════════════════════════════════════════════════════════
doc.recompute()
Gui.activeDocument().activeView().viewIsometric()
Gui.SendMsgToActiveView("ViewFit")

print("")
print("╔════════════════════════════════════════════╗")
print("║  SUPPORT ARTICULÉ ESP32-CAM + SG90 — OK  ║")
print("╠════════════════════════════════════════════╣")
print("║  Piece 1 : Boitier camera  32x45x20mm     ║")
print("║            Goulotte        Ø12/8 x40mm    ║")
print("║  Piece 2 : Pince U         42x20x38mm     ║")
print("║            SG90 loge       23x13x25mm     ║")
print("╠════════════════════════════════════════════╣")
print("║  ASSEMBLAGE :                              ║")
print("║  1. Clipser pince sur rebord du pot        ║")
print("║  2. Serrer vis M4 laterale                 ║")
print("║  3. Emboiter goulotte sur axe SG90         ║")
print("║  4. Câbles passent dans la goulotte Ø8mm   ║")
print("╚════════════════════════════════════════════╝")
