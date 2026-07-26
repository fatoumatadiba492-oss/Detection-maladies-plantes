import FreeCAD as App, Part, FreeCADGui as Gui
doc = App.newDocument("Boitier_ESP32CAM")
V = App.Vector

def box(W,D,H,x=0,y=0,z=0): return Part.makeBox(W,D,H).translated(V(x,y,z))
def cylZ(r,H,x=0,y=0,z=0):  return Part.makeCylinder(r,H,V(x,y,z),V(0,0,1))
def cylY(r,H,x=0,y=0,z=0):  return Part.makeCylinder(r,H,V(x,y,z),V(0,1,0))

SGA = 5.0
MUR = 2.5
CL,CW,CD = 41.0,27.5,15.5
BW = CL+2*MUR   # ~46mm
BD = CD+2*MUR   # ~20.5mm
BH = CW+2*MUR   # ~32.5mm

cam = box(BW,BD,BH,  -BW/2,-BD,2)

# intérieur PCB
cam = cam.cut(box(CL,CD,CW+2,  -CL/2,-BD+MUR,2+MUR))

# trou objectif OV2640 Ø11mm (face avant, axe Y)
cam = cam.cut(cylY(5.5,BD+2,  -7.0,-BD-1,2+BH/2))

# trou flash LED Ø7mm (face avant, axe Y)
cam = cam.cut(cylY(3.5,BD+2,   4.0,-BD-1,2+BH/2))

# fente USB (face droite)
cam = cam.cut(box(MUR+2,10,5.5,  BW/2-1,-BD+MUR+2,2+MUR+3))

# antenne WiFi (face gauche, haut)
cam = cam.cut(box(MUR+2,BD-MUR,8,  -BW/2-1,-BD+MUR,2+BH-10))

# fentes ventilation × 3
for i in range(3):
    fz = 2+4+i*9
    cam = cam.cut(box(MUR+2,12,2.5,  -BW/2-1,   -BD+4,fz))
    cam = cam.cut(box(MUR+2,12,2.5,   BW/2-MUR-1,-BD+4,fz))

# trou axe servo Ø5mm
cam = cam.cut(cylZ(SGA/2,14,  0,0,-1))

# 4 trous corne servo M2 (croix SG90, rayon 9mm)
for hx,hy in [(-9,0),(9,0),(0,-9),(0,9)]:
    cam = cam.cut(cylZ(1.15,10, hx,hy,-1))

# passage câbles fond
cam = cam.cut(box(8,8,MUR+2, -4,-4,-1))

o = doc.addObject("Part::Feature","Boitier_ESP32CAM")
o.Shape = cam
o.ViewObject.ShapeColor = (0.10,0.10,0.12)

doc.recompute()
Gui.activeDocument().activeView().viewIsometric()
Gui.SendMsgToActiveView("ViewFit")
print(f"✓ Boîtier ESP32-CAM {BW:.0f}×{BD:.0f}×{BH:.0f}mm")
print("  Trou objectif Ø11mm | Flash Ø7mm | USB | Antenne | Ventilation")
print("  Impression : PLA, 0.2mm, 25% infill, pas de supports")
