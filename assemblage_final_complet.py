import FreeCAD as App
import Part
import FreeCADGui as Gui

# ╔══════════════════════════════════════════════════════════════╗
# ║  ASSEMBLAGE FINAL COMPLET — DÉTECTION MALADIES PLANTES     ║
# ║  Pince + SG90 + Boîtier caméra + ESP32-CAM                 ║
# ║  La caméra tourne ±90° avec le servo                       ║
# ║  Macro → Macros → Créer → Coller → Exécuter               ║
# ╚══════════════════════════════════════════════════════════════╝

doc = App.newDocument("Assemblage_Final")
V = App.Vector

# Axe servo — point de rotation commun à toutes les pièces
AX, AY = 40.0, 15.0

# ═══════════════════════════════════════════════════════════════
# PIÈCE 1 — PINCE JARDINIÈRE (bleue, FIXE sur le pot)
# 80×30×60mm — slot 10mm mord la paroi — vis M4 latérale
# ═══════════════════════════════════════════════════════════════
PW, PD, PH = 80.0, 30.0, 60.0
SLOT, ARM  = 10.0, 30.0

p = Part.makeBox(PW, PD, PH)
p = p.cut(Part.makeBox(SLOT, PD+2, ARM+1).translated(V((PW-SLOT)/2, -1, -1)))
p = p.cut(Part.makeBox(23.5, 13.3, 24.0).translated(V(AX-11.75, AY-6.65, PH-24)))
p = p.cut(Part.makeBox(PW, 13.3, 4.5).translated(V(0, AY-6.65, PH-4.5)))
p = p.cut(Part.makeCylinder(2.5, PH+2, V(AX, AY, -1), V(0, 0, 1)))
p = p.cut(Part.makeCylinder(2.0, PW+2, V(-1, AY, ARM/2), V(1, 0, 0)))

o1 = doc.addObject("Part::Feature","1_Pince_Jardiniere")
o1.Shape = p
o1.ViewObject.ShapeColor = (0.20, 0.40, 0.70)

# ═══════════════════════════════════════════════════════════════
# COMPOSANT SG90 (gris foncé transparent — dans la pince)
# Corps réel 22.5×11.8×22.7mm centré sur AX, AY
# ═══════════════════════════════════════════════════════════════
sg = Part.makeBox(22.5, 11.8, 22.7)
o_sg = doc.addObject("Part::Feature","2_SG90_Servo")
o_sg.Shape = sg
o_sg.Placement = App.Placement(V(AX-11.25, AY-5.9, PH-23.2), App.Rotation())
o_sg.ViewObject.ShapeColor = (0.08, 0.08, 0.08)
o_sg.ViewObject.Transparency = 30

# Axe servo Ø4.7mm (jaune — sort du SG90 vers le haut)
axe = Part.makeCylinder(2.35, 16, V(AX, AY, PH-2), V(0, 0, 1))
o_ax = doc.addObject("Part::Feature","3_Axe_Servo")
o_ax.Shape = axe
o_ax.ViewObject.ShapeColor = (1.0, 0.85, 0.0)

# ═══════════════════════════════════════════════════════════════
# PIÈCE 2 — BOÎTIER ESP32-CAM (gris, MOBILE — tourne avec servo)
# 32×45×22mm + goulotte Ø14/Ø4 × 60mm + bossage Ø20mm
# Axe de rotation Z centré sur AX, AY
# ═══════════════════════════════════════════════════════════════
BW, BL, BH = 32.0, 45.0, 22.0
tx = AX - BW/2    # 24.0
ty = AY - BL/2    # -7.5
tz = PH + 5.0     # 65.0 (5mm au-dessus pince, espace palonnier)

# Solides bruts fusionnés AVANT tout cut
box_raw    = Part.makeBox(BW, BL, BH)
tube_raw   = Part.makeCylinder(7.0, 60.0, V(BW/2, BL/2, -60), V(0, 0, 1))
flange_raw = Part.makeCylinder(10.0, 4.0, V(BW/2, BL/2, -60), V(0, 0, 1))
cam = box_raw.fuse(tube_raw).fuse(flange_raw)

cam = cam.cut(Part.makeBox(28.0, 41.0, 19.0).translated(V(2.0, 2.0, 3.0)))
cam = cam.cut(Part.makeCylinder(4.0, BL+2, V(BW/2, -1, BH/2), V(0, 1, 0)))
cam = cam.cut(Part.makeCylinder(2.0, 65.0, V(BW/2, BL/2, -61), V(0, 0, 1)))

# Position 0° (face à la plante saine)
o2 = doc.addObject("Part::Feature","4_Boitier_Camera_0deg")
o2.Shape = cam
o2.Placement = App.Placement(V(tx, ty, tz), App.Rotation(V(0,0,1), 0), V(BW/2, BL/2, 0))
o2.ViewObject.ShapeColor = (0.25, 0.25, 0.30)

# Position +75° (face à la plante malade) — semi-transparent pour illustrer rotation
o2b = doc.addObject("Part::Feature","5_Boitier_Camera_75deg")
o2b.Shape = cam
o2b.Placement = App.Placement(V(tx, ty, tz), App.Rotation(V(0,0,1), 75), V(BW/2, BL/2, 0))
o2b.ViewObject.ShapeColor = (0.50, 0.50, 0.55)
o2b.ViewObject.Transparency = 55

# ═══════════════════════════════════════════════════════════════
# COMPOSANT ESP32-CAM PCB (vert transparent — dans le boîtier)
# PCB réel 40.5×27×1.6mm + module caméra OV2640
# ═══════════════════════════════════════════════════════════════
pcb = Part.makeBox(40.5, 27.0, 1.6)
o_pcb = doc.addObject("Part::Feature","6_ESP32CAM_PCB")
o_pcb.Shape = pcb
o_pcb.Placement = App.Placement(V(tx+2, ty+2, tz+4), App.Rotation())
o_pcb.ViewObject.ShapeColor = (0.05, 0.50, 0.05)
o_pcb.ViewObject.Transparency = 20

# Module objectif OV2640 (noir — face avant du boîtier)
objectif = Part.makeCylinder(4.0, 10.0, V(AX, AY-1, tz+BH/2), V(0, -1, 0))
o_obj = doc.addObject("Part::Feature","7_OV2640_Objectif")
o_obj.Shape = objectif
o_obj.ViewObject.ShapeColor = (0.05, 0.05, 0.05)

# ═══════════════════════════════════════════════════════════════
doc.recompute()
Gui.activeDocument().activeView().viewIsometric()
Gui.SendMsgToActiveView("ViewFit")

print("")
print("╔═══════════════════════════════════════════════════════╗")
print("║      ASSEMBLAGE FINAL COMPLET                        ║")
print("╠═══════════════════════════════════════════════════════╣")
print("║  1. Pince jardiniere    (bleu)    — FIXE sur pot     ║")
print("║  2. SG90 servo          (noir)    — dans la pince    ║")
print("║  3. Axe servo           (jaune)   — rotation ±90°   ║")
print("║  4. Boitier 0°          (gris)    — plante saine     ║")
print("║  5. Boitier 75°         (transparent) — pl. malade  ║")
print("║  6. ESP32-CAM PCB       (vert)    — dans le boitier  ║")
print("║  7. Objectif OV2640     (noir)    — face avant       ║")
print("╠═══════════════════════════════════════════════════════╣")
print("║  Rotation servo : 0° → plante saine                 ║")
print("║                   75° → plante malade               ║")
print("║  Cables : tunnel Ø4mm dans la goulotte              ║")
print("╚═══════════════════════════════════════════════════════╝")
