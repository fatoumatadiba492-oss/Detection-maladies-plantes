import FreeCAD as App, Part, FreeCADGui as Gui
doc = App.newDocument("Detection_Maladies_Plantes")

# ── 1. PINCE DE FIXATION (70 x 45 x 70 mm) ──────────────────
p = Part.makeBox(70,45,70)
p = p.cut(Part.makeBox(26,36,45).translated(App.Vector(22,-1,0)))   # slot C
p = p.cut(Part.makeBox(10,10,72).translated(App.Vector(55,17.5,-1))) # canal câbles
for x,y in [(12,10),(12,35),(58,10),(58,35)]:                        # trous M3
    p = p.cut(Part.makeCylinder(1.7,7).translated(App.Vector(x,y,64)))
o1=doc.addObject("Part::Feature","Pince_Fixation"); o1.Shape=p
o1.ViewObject.ShapeColor=(0.6,0.6,0.65)
print("✓ Pince de Fixation")

# ── 2. PAN-TILT HOUSING (55 x 45 x 45 mm) ───────────────────
h = Part.makeBox(55,45,45)
h = h.cut(Part.makeBox(25,14,32).translated(App.Vector(15,15.5,3)))  # servo PAN
h = h.cut(Part.makeCylinder(3.5,12).translated(App.Vector(27.5,22.5,33))) # axe PAN
tilt = Part.makeBox(15,25,31).translated(App.Vector(-1,10,11))
h = h.cut(tilt)                                                       # servo TILT
axe_t = Part.makeCylinder(3.5,12)
axe_t.rotate(App.Vector(0,0,0),App.Vector(0,1,0),90)
axe_t = axe_t.translated(App.Vector(15,22.5,26.5))
h = h.cut(axe_t)                                                      # axe TILT
h = h.cut(Part.makeBox(10,10,47).translated(App.Vector(42,17.5,-1)))  # câbles
for x,y in [(10,10),(10,35),(45,10),(45,35)]:
    h = h.cut(Part.makeCylinder(1.7,5).translated(App.Vector(x,y,-1)))
o2=doc.addObject("Part::Feature","PanTilt_Housing"); o2.Shape=h
o2.Placement=App.Placement(App.Vector(7.5,0,78),App.Rotation())
o2.ViewObject.ShapeColor=(0.55,0.55,0.60)
print("✓ Pan-Tilt Housing")

# ── 3. BOITIER ESP32-CAM (35 x 32 x 55 mm) ──────────────────
c = Part.makeBox(35,32,55)
c = c.cut(Part.makeBox(30,27,52.5).translated(App.Vector(2.5,2.5,2.5))) # intérieur
c = c.cut(Part.makeBox(12,4,12).translated(App.Vector(11.5,-1,17)))      # objectif
c = c.cut(Part.makeBox(8,4,8).translated(App.Vector(24.5,-1,19)))        # flash
c = c.cut(Part.makeBox(12,6,4).translated(App.Vector(11.5,13,-1)))       # USB
for z in [12,25,38]:                                                      # ventilation
    c = c.cut(Part.makeBox(4,14,3).translated(App.Vector(-1,9,z)))
    c = c.cut(Part.makeBox(4,14,3).translated(App.Vector(32,9,z)))
o3=doc.addObject("Part::Feature","Boitier_ESP32CAM"); o3.Shape=c
o3.Placement=App.Placement(App.Vector(17.5,6.5,128),App.Rotation())
o3.ViewObject.ShapeColor=(0.5,0.5,0.55)
print("✓ Boitier ESP32-CAM")

# ── AFFICHAGE ────────────────────────────────────────────────
doc.recompute()
Gui.activeDocument().activeView().viewIsometric()
Gui.SendMsgToActiveView("ViewFit")
print("\n=== ASSEMBLAGE COMPLET — Hauteur totale ~170mm ===")
print("Pour exporter STL: sélectionner pièce → File → Export → .stl")
