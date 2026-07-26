// ============================================================
// PINCE DE FIXATION - Système de détection maladies plantes
// Dimensions: 70mm(L) × 45mm(l) × 70mm(H)
// Slot C: rebord jardinière 25mm + 1mm jeu = 26mm
// ============================================================

$fn = 32;

// Paramètres
W = 70;      // Largeur totale
D = 45;      // Profondeur totale
H = 70;      // Hauteur totale
WT = 5;      // Épaisseur paroi min

SLOT_W = 26; // Largeur slot (rebord 25mm + 1mm jeu)
SLOT_D = 35; // Profondeur slot
SLOT_H = 45; // Hauteur ouverture slot (depuis bas)

CABLE_W = 10; // Canal câbles
SCREW_D = 3.4; // Diam trou vis M3

module pince() {
    difference() {
        // Corps principal
        cube([W, D, H]);

        // Slot C (ouvert vers le bas) - centré en largeur
        translate([(W - SLOT_W) / 2, -1, 0])
            cube([SLOT_W, SLOT_D + 1, SLOT_H]);

        // Canal passage câbles vertical (10×10mm) côté droit
        translate([W - WT - CABLE_W, D/2 - CABLE_W/2, -1])
            cube([CABLE_W, CABLE_W, H + 2]);

        // 4 trous de vis M3 (diam 3.4mm) sur plateau supérieur
        for (pos = [[12, 10], [12, D-10], [W-12, 10], [W-12, D-10]]) {
            translate([pos[0], pos[1], H - WT - 1])
                cylinder(d = SCREW_D, h = WT + 2);
        }

        // Chanfreins internes du slot pour faciliter le clipsage
        translate([(W - SLOT_W) / 2, SLOT_D - 1, SLOT_H - 5])
            rotate([45, 0, 0])
                cube([SLOT_W, 4, 4]);
    }
}

pince();
