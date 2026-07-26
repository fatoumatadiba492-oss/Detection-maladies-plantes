import FreeCAD as App, Part, FreeCADGui as Gui
doc = App.newDocument("Pince_Secure")
V = App.Vector

def box(W,D,H,x=0,y=0,z=0): return Part.makeBox(W,D,H).translated(V(x,y,z))
def cylZ(r,H,x=0,y=0,z=0):  return Part.makeCylinder(r,H,V(x,y,z),V(0,0,1))
def cylX(r,H,x=0,y=0,z=0):  return Part.makeCylinder(r,H,V(x,y,z),V(1,0,0))

PW,PD,PH = 90,48,80

# Corps principal
p = box(PW,PD,PH)

# Slot C — 15mm large (ajustage serré sur rebord 15mm), 25mm profond, 65mm haut
# S'ouvre vers le bas (rebord entre par le bas)
p = p.cut(box(15, 26, 65,  37.5, -1, 0))

# Chanfrein d'entrée slot (guide le rebord, facilite le clippage)
p = p.cut(box(19, 6, 6,  35.5, -1, 0))

# 2 VIS M3 DE VERROUILLAGE (pressent sur les faces latérales du rebord)
# Vis gauche : entre par la face gauche (x=0) → presse sur côté gauche du rebord
vis_g = cylX(1.7, 38,   0, 24, 35)
p = p.cut(vis_g)
# Vis droite : entre par la face droite (x=90) → presse sur côté droit du rebord
vis_d = Part.makeCylinder(1.7, 38, V(90,24,35), V(-1,0,0))
p = p.cut(vis_d)

# Canal câbles 8×8mm (côté arrière, toute la hauteur)
p = p.cut(box(8, 8, PH+2,  77, 20, -1))

# 4 trous M3 plateau supérieur (vissage mât)
for px,py in [(15,10),(15,38),(75,10),(75,38)]:
    p = p.cut(cylZ(1.7, 10, px, py, PH-9))

o = doc.addObject("Part::Feature","Pince_Secure")
o.Shape = p
o.ViewObject.ShapeColor = (0.75,0.42,0.32)

doc.recompute()
Gui.activeDocument().activeView().viewIsometric()
Gui.SendMsgToActiveView("ViewFit")
print("✓ Pince SÉCURISÉE 90×48×80mm")
print("  Slot 15mm serré — 2 vis M3 latérales de verrouillage")
print()
print("  MODE D'EMPLOI :")
print("  1. Aligner la pince AU-DESSUS du rebord du pot")
print("  2. POUSSER VERS LE BAS — le rebord entre dans le slot")
print("  3. SERRER les 2 vis M3 sur les côtés → BLOQUÉ, ne tombe plus")
