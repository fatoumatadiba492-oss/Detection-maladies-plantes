import FreeCAD as App
import Part
import FreeCADGui as Gui

# ╔══════════════════════════════════════════════════════════════╗
# ║  BOÎTIER ESP32-CAM + COUVERCLE AMOVIBLE                    ║
# ║  Corps : ESP32-CAM logé, ouvert par le haut                ║
# ║  Couvercle : se visse, trou objectif Ø8mm + flash Ø6mm     ║
# ╚══════════════════════════════════════════════════════════════╝

doc = App.newDocument("Boitier_Couvercle")
V = App.Vector

BW, BL, BH = 32.0, 45.0, 22.0   # extérieur boîtier

# ═══════════════════════════════════════════════════════════════
# PIÈCE A — CORPS BOÎTIER (goulotte + logement ESP32-CAM)
# ═══════════════════════════════════════════════════════════════
box_raw    = Part.makeBox(BW, BL, BH)
tube_raw   = Part.makeCylinder(7.0, 60.0, V(BW/2, BL/2, -60), V(0, 0, 1))
flange_raw = Part.makeCylinder(10.0, 4.0,  V(BW/2, BL/2, -60), V(0, 0, 1))
cam = box_raw.fuse(tube_raw).fuse(flange_raw)

# Cavité intérieure 28×41×18mm (ouverte par le HAUT pour glisser l'ESP32-CAM)
cam = cam.cut(Part.makeBox(28.0, 41.0, 19.0).translated(V(2.0, 2.0, 3.0)))

# Tunnel câbles Ø4mm (goulotte → fond cavité)
cam = cam.cut(Part.makeCylinder(2.0, 65.0, V(BW/2, BL/2, -61), V(0, 0, 1)))

# 4 trous M2 Ø2.2mm pour visser le couvercle (coins haut de la cavité)
cam = cam.cut(Part.makeCylinder(1.1, 8, V(5,   5,   15), V(0, 0, 1)))
cam = cam.cut(Part.makeCylinder(1.1, 8, V(27,  5,   15), V(0, 0, 1)))
cam = cam.cut(Part.makeCylinder(1.1, 8, V(5,   40,  15), V(0, 0, 1)))
cam = cam.cut(Part.makeCylinder(1.1, 8, V(27,  40,  15), V(0, 0, 1)))

# Fente USB (face droite, accès alimentation)
cam = cam.cut(Part.makeBox(4, 12, 5).translated(V(BW-3, 16, 4)))

o1 = doc.addObject("Part::Feature","A_Corps_Boitier")
o1.Shape = cam
o1.ViewObject.ShapeColor = (0.15, 0.15, 0.18)
print("OK Corps boitier 32x45x22mm — ouvert par le haut")

# ═══════════════════════════════════════════════════════════════
# PIÈCE B — COUVERCLE AMOVIBLE  32×45×4mm
# Referme le boîtier | Trou objectif Ø8mm | Trou flash Ø6mm
# Lèvre intérieure 28×41mm qui s'emboîte dans la cavité
# 4 trous M2 pour vissage
# ═══════════════════════════════════════════════════════════════
CW, CL, CH = 32.0, 45.0, 4.0   # dimensions couvercle

couv = Part.makeBox(CW, CL, CH)

# Lèvre intérieure 27.5×40.5mm × 2mm (s'emboîte dans cavité 28×41mm, jeu 0.5mm)
couv = couv.cut(Part.makeBox(22.0, 35.0, 2.1).translated(V(5.0, 5.0, -0.1)))

# TROU OBJECTIF Ø8mm (ESP32-CAM lens — légèrement décentré comme sur le vrai module)
couv = couv.cut(Part.makeCylinder(4.0, CH+2, V(14, 10, -1), V(0, 0, 1)))

# TROU FLASH LED Ø6mm (à côté de l'objectif)
couv = couv.cut(Part.makeCylinder(3.0, CH+2, V(22, 10, -1), V(0, 0, 1)))

# Zone dégagée autour objectif + flash (fenêtre rectangulaire 20×10mm)
# Optionnel — agrandit l'ouverture pour plus de lumière
couv = couv.cut(Part.makeBox(14, 6, CH+2).translated(V(11, 7, -1)))

# 4 trous M2 Ø2.2mm vissage (alignés sur le corps)
couv = couv.cut(Part.makeCylinder(1.1, CH+2, V(5,  5,  -1), V(0, 0, 1)))
couv = couv.cut(Part.makeCylinder(1.1, CH+2, V(27, 5,  -1), V(0, 0, 1)))
couv = couv.cut(Part.makeCylinder(1.1, CH+2, V(5,  40, -1), V(0, 0, 1)))
couv = couv.cut(Part.makeCylinder(1.1, CH+2, V(27, 40, -1), V(0, 0, 1)))

o2 = doc.addObject("Part::Feature","B_Couvercle")
o2.Shape = couv
o2.Placement = App.Placement(V(0, 0, BH+5), App.Rotation())
o2.ViewObject.ShapeColor = (0.30, 0.30, 0.35)
print("OK Couvercle 32x45x4mm — objectif Ø8mm + flash Ø6mm + 4x M2")

# ═══════════════════════════════════════════════════════════════
doc.recompute()
Gui.activeDocument().activeView().viewIsometric()
Gui.SendMsgToActiveView("ViewFit")

print("")
print("╔═════════════════════════════════════════════╗")
print("║  BOÎTIER ESP32-CAM — 2 PIÈCES              ║")
print("╠═════════════════════════════════════════════╣")
print("║  A. Corps  32x45x22mm  (gris foncé)        ║")
print("║     Ouvert par le haut pour insérer la cam ║")
print("║     Goulotte Ø14mm + tunnel câbles Ø4mm    ║")
print("║  B. Couvercle  32x45x4mm  (gris moyen)     ║")
print("║     Objectif Ø8mm + Flash Ø6mm             ║")
print("║     Lèvre emboîtée + 4x vis M2             ║")
print("╠═════════════════════════════════════════════╣")
print("║  MONTAGE :                                  ║")
print("║  1. Glisser ESP32-CAM dans le corps        ║")
print("║  2. Brancher les câbles                     ║")
print("║  3. Fermer avec le couvercle                ║")
print("║  4. Visser 4x M2 aux coins                 ║")
print("╚═════════════════════════════════════════════╝")
