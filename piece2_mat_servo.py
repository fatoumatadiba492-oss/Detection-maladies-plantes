import FreeCAD as App, Part, FreeCADGui as Gui
doc = App.newDocument("Mat_Servo")
V = App.Vector

def box(W,D,H,x=0,y=0,z=0): return Part.makeBox(W,D,H).translated(V(x,y,z))
def cylZ(r,H,x=0,y=0,z=0):  return Part.makeCylinder(r,H,V(x,y,z),V(0,0,1))
def cylX(r,H,x=0,y=0,z=0):  return Part.makeCylinder(r,H,V(x,y,z),V(1,0,0))

MW,MD,MH = 90,48,110
SGL,SGW,SGH,SGA = 23.0,12.3,23.2,5.0
lx=(MW-SGL)/2
ly=(MD-SGW)/2
lz=MH-SGH-4
sv_z=lz+SGH/2

m = box(MW,MD,MH)
m = m.cut(box(SGL,SGW,SGH+6,        lx,ly,lz))
m = m.cut(box(SGL+11,SGW,4,         lx-5.5,ly,MH-4))
m = m.cut(cylZ(SGA/2,22,            MW/2,MD/2,MH-20))
m = m.cut(cylZ(11.5,6,              MW/2,MD/2,MH-5))
m = m.cut(box(10,MD/2+2,lz+8,       MW/2-5,-1,0))
m = m.cut(box(8,8,MH+2,             MW-13,MD/2-4,-1))
for px,py in [(15,10),(15,38),(75,10),(75,38)]:
    m = m.cut(cylZ(1.7,12, px,py,-1))
m = m.cut(cylX(1.7,10,  -1,   MD/2,sv_z))
m = m.cut(cylX(1.7,10,  MW-9, MD/2,sv_z))

o = doc.addObject("Part::Feature","Mat_Servo")
o.Shape = m
o.ViewObject.ShapeColor = (0.20,0.20,0.23)

doc.recompute()
Gui.activeDocument().activeView().viewIsometric()
Gui.SendMsgToActiveView("ViewFit")
print("✓ Mât+Servo 90×48×110mm — logement SG90 — axe Ø5mm en haut")
print("  Impression : PLA, 0.2mm, 30% infill, pas de supports")
