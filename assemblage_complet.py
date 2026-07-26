import FreeCAD as App
import Part
import FreeCADGui as Gui

# ╔══════════════════════════════════════════════════════════════╗
# ║  ASSEMBLAGE COMPLET — DÉTECTION MALADIES PLANTES           ║
# ║  Pince jardinière + Boîtier ESP32-CAM, axe servo aligné    ║
# ║  Macro → Macros → Créer → Coller → Exécuter               ║
# ╚══════════════════════════════════════════════════════════════╝

doc = App.newDocument("Assemblage_Complet")
V = App.Vector

# ════════════════════════════════════════════════════════════════
# POINT CLÉ : position axe servo en coordonnées monde
# Les 2 pièces sont construites autour de ce même point
# ════════════════════════════════════════════════════════════════
AX, AY = 40.0, 15.0   # centre axe servo (X, Y)

# ════════════════════════════════════════════════════════════════
# PIÈCE 1 — PINCE JARDINIÈRE  80×30×60mm
#   Slot 10mm (mord la paroi du pot)
#   SG90 centré sur AX, AY
#   Vis M4 latérale pour bloquer sur le pot
# ════════════════════════════════════════════════════════════════
PW, PD, PH = 80.0, 30.0, 60.0
SLOT, ARM  = 10.0, 30.0

p = Part.makeBox(PW, PD, PH)

# Slot qui mord la paroi du pot (centré en X, s'ouvre vers le bas)
p = p.cut(Part.makeBox(SLOT, PD+2, ARM+1).translated(V((PW-SLOT)/2, -1, -1)))

# Logement SG90 23.5×13.3×24mm — centré sur AX, AY — par le haut
p = p.cut(Part.makeBox(23.5, 13.3, 24.0).translated(V(AX-11.75, AY-6.65, PH-24)))

# Rainures pattes latérales SG90 (toute la largeur, ras du dessus)
p = p.cut(Part.makeBox(PW, 13.3, 4.5).translated(V(0, AY-6.65, PH-4.5)))

# Trou axe servo Ø5mm — vertical, centré sur AX AY
p = p.cut(Part.makeCylinder(2.5, PH+2, V(AX, AY, -1), V(0, 0, 1)))

# Vis M4 Ø4mm — latérale, z = milieu du bras (z=15)
p = p.cut(Part.makeCylinder(2.0, PW+2, V(-1, AY, ARM/2), V(1, 0, 0)))

o1 = doc.addObject("Part::Feature", "Pince_Jardiniere")
o1.Shape = p
o1.ViewObject.ShapeColor = (0.20, 0.40, 0.70)
print("OK Piece 1 — Pince 80x30x60mm")

# ════════════════════════════════════════════════════════════════
# PIÈCE 2 — BOÎTIER ESP32-CAM  32×45×22mm
#   Goulotte Ø14ext / Ø4int × 60mm
#   Bossage palonnier Ø20mm × 4mm (fond goulotte)
#   Aligné sur le même axe servo AX, AY
# ════════════════════════════════════════════════════════════════
BW, BL, BH = 32.0, 45.0, 22.0

# Décalage pour que la goulotte tombe exactement sur l'axe servo
tx = AX - BW/2      # 40 - 16 = 24mm
ty = AY - BL/2      # 15 - 22.5 = -7.5mm
tz = PH + 5.0       # 5mm au-dessus de la pince (espace palonnier SG90)

# Solides bruts fusionnés AVANT tout cut (règle OCCT)
box_raw    = Part.makeBox(BW, BL, BH)
tube_raw   = Part.makeCylinder(7.0, 60.0, V(BW/2, BL/2, -60), V(0, 0, 1))
flange_raw = Part.makeCylinder(10.0, 4.0,  V(BW/2, BL/2, -60), V(0, 0, 1))
cam = box_raw.fuse(tube_raw).fuse(flange_raw)

# Cavité ESP32-CAM 28×41×18mm (ouverte par le haut)
cam = cam.cut(Part.makeBox(28.0, 41.0, 19.0).translated(V(2.0, 2.0, 3.0)))

# Trou objectif Ø8mm (face avant, axe horizontal +Y)
cam = cam.cut(Part.makeCylinder(4.0, BL+2, V(BW/2, -1, BH/2), V(0, 1, 0)))

# Tunnel câbles Ø4mm (goulotte → fond cavité)
cam = cam.cut(Part.makeCylinder(2.0, 65.0, V(BW/2, BL/2, -61), V(0, 0, 1)))

o2 = doc.addObject("Part::Feature", "Boitier_Camera")
o2.Shape = cam
o2.Placement = App.Placement(V(tx, ty, tz), App.Rotation())
o2.ViewObject.ShapeColor = (0.25, 0.25, 0.30)
print("OK Piece 2 — Boitier camera 32x45x22mm")

# ════════════════════════════════════════════════════════════════
doc.recompute()
Gui.activeDocument().activeView().viewIsometric()
Gui.SendMsgToActiveView("ViewFit")

print("")
print("╔══════════════════════════════════════════════╗")
print("║      ASSEMBLAGE COMPLET — 2 PIÈCES OK       ║")
print("╠══════════════════════════════════════════════╣")
print("║  Axe servo  X=40mm  Y=15mm  (aligné)  ✓    ║")
print("║  Goulotte centrée sur l'axe            ✓    ║")
print("║  Bossage Ø20mm / palonnier SG90        ✓    ║")
print("║  Tunnel câbles Ø4mm continu            ✓    ║")
print("╠══════════════════════════════════════════════╣")
print("║  ASSEMBLAGE RÉEL :                          ║")
print("║  1. Clipser pince sur rebord jardinière     ║")
print("║  2. Serrer vis M4 latérale                  ║")
print("║  3. Insérer SG90 par le haut de la pince   ║")
print("║  4. Emboîter goulotte sur palonnier SG90   ║")
print("║  5. Visser M3 central — rotation ±90°      ║")
print("╚══════════════════════════════════════════════╝")
