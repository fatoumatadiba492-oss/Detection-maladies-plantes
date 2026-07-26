import FreeCAD as App
import Part
import FreeCADGui as Gui

# ╔══════════════════════════════════════════════════════════════╗
# ║  SUPPORT ARTICULÉ ESP32-CAM + SG90 — V5 DIMENSIONS EXACTES ║
# ║  Macro → Macros → Créer → Coller → Exécuter                ║
# ╚══════════════════════════════════════════════════════════════╝

doc = App.newDocument("Support_V5")
V = App.Vector

# ══════════════════════════════════════════════════════════════
# PIÈCE 1 — BOÎTIER CAMÉRA  32×45×22mm
#   Cavité ESP32-CAM : 28×41×18mm
#   Objectif : Ø8mm (face avant)
#   Goulotte : Ø14mm ext / Ø4mm int × 60mm
#   Bossage palonnier SG90 : Ø20mm × 4mm (dessous goulotte)
# ══════════════════════════════════════════════════════════════
BW, BL, BH = 32.0, 45.0, 22.0

# Solides bruts fusionnés AVANT tout cut → OCCT valide
box_raw    = Part.makeBox(BW, BL, BH)
tube_raw   = Part.makeCylinder(7.0, 60.0, V(BW/2, BL/2, -60), V(0, 0, 1))
flange_raw = Part.makeCylinder(10.0, 4.0,  V(BW/2, BL/2, -60), V(0, 0, 1))
cam = box_raw.fuse(tube_raw).fuse(flange_raw)

# Cavité ESP32-CAM 28×41×18mm (ouverte par le haut, parois 2mm, sol à z=4)
cam = cam.cut(Part.makeBox(28.0, 41.0, 19.0).translated(V(2.0, 2.0, 3.0)))

# Trou objectif Ø8mm (face avant y=0, axe horizontal +Y)
cam = cam.cut(Part.makeCylinder(4.0, BL+2, V(BW/2, -1, BH/2), V(0, 1, 0)))

# Tunnel câbles Ø4mm (du bas de la goulotte jusqu'au sol de la cavité)
cam = cam.cut(Part.makeCylinder(2.0, 65.0, V(BW/2, BL/2, -61), V(0, 0, 1)))

o1 = doc.addObject("Part::Feature", "Boitier_Camera")
o1.Shape = cam
o1.ViewObject.ShapeColor = (0.25, 0.25, 0.30)
print("OK Piece 1 — Boitier 32x45x22mm + goulotte 60mm + bossage Ø20mm")

# ══════════════════════════════════════════════════════════════
# PIÈCE 2 — PINCE DE FIXATION  30×32×38mm
#   U rebord pot : 22mm interne, parois 4mm × hauteur 15mm
#   Logement SG90 : 23×13×23mm (par le haut, centré)
#   Rainures pattes SG90 : 30×13×4mm (ras du dessus)
#   Trou axe servo : Ø4mm vertical (centré)
#   Vis serrage M4 : Ø4mm latérale (rebord pot)
#   Fente câbles : 10×5mm (face avant, bas)
# ══════════════════════════════════════════════════════════════
PW, PD, PH = 30.0, 32.0, 38.0

pince = Part.makeBox(PW, PD, PH)

# U-slot rebord pot 22mm (s'ouvre vers le bas, hauteur 15mm)
pince = pince.cut(Part.makeBox(22.0, PD+2, 16.0).translated(V(4.0, -1, -1)))

# Logement SG90 23×13×23mm (centré en XY, par le haut)
pince = pince.cut(Part.makeBox(23.0, 13.0, 24.0).translated(V(3.5, 9.5, 14.0)))

# Rainures pattes latérales SG90 (30×13×4mm, ras du dessus)
pince = pince.cut(Part.makeBox(30.0, 13.0, 4.5).translated(V(0.0, 9.5, 33.5)))

# Trou axe servo Ø4mm (vertical, centré, traversant)
pince = pince.cut(Part.makeCylinder(2.0, PH+2, V(PW/2, PD/2, -1), V(0, 0, 1)))

# Vis serrage M4 Ø4mm (latérale, z=7 = milieu du rebord pot)
pince = pince.cut(Part.makeCylinder(2.0, PW+2, V(-1, PD/2, 7.0), V(1, 0, 0)))

# Fente sortie câbles servo 10×5mm (face avant, bas)
pince = pince.cut(Part.makeBox(10.0, 3.0, 5.0).translated(V(10.0, -1, 0.0)))

o2 = doc.addObject("Part::Feature", "Pince_Fixation")
o2.Shape = pince
o2.Placement = App.Placement(V(50, 0, 0), App.Rotation())
o2.ViewObject.ShapeColor = (0.20, 0.20, 0.25)
print("OK Piece 2 — Pince 30x32x38mm + SG90 + vis M4 + fente cables")

# ══════════════════════════════════════════════════════════════
doc.recompute()
Gui.activeDocument().activeView().viewIsometric()
Gui.SendMsgToActiveView("ViewFit")

print("")
print("╔═════════════════════════════════════════════════╗")
print("║  SUPPORT V5 — DIMENSIONS EXACTES DU PLAN       ║")
print("╠═════════════════════════════════════════════════╣")
print("║  Boitier  32x45x22mm   cavite 28x41x18mm       ║")
print("║  Objectif Ø8mm         goulotte Ø14/4 x60mm    ║")
print("║  Bossage  Ø20mm x4mm  (fixation palonnier)     ║")
print("╠═════════════════════════════════════════════════╣")
print("║  Pince    30x32x38mm   U 22mm interne          ║")
print("║  SG90     23x13x23mm   vis M4 + fente cables   ║")
print("╠═════════════════════════════════════════════════╣")
print("║  ASSEMBLAGE :                                   ║")
print("║  1. Clipser pince sur rebord pot                ║")
print("║  2. Serrer vis M4 laterale                      ║")
print("║  3. Emboiter bossage Ø20mm sur palonnier SG90  ║")
print("║  4. Cables dans tunnel Ø4mm (goulotte creuse)  ║")
print("╚═════════════════════════════════════════════════╝")
