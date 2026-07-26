// ============================================================
// PAN-TILT HOUSING - Double servo SG90
// Dimensions: 55mm(L) × 45mm(l) × 45mm(H)
// Servo SG90 corps: 23mm × 12.5mm × 29mm
// Servo PAN: rotation horizontale (bas)
// Servo TILT: inclinaison verticale (haut)
// Canal câbles intégré + 4 trous M3 pour fixation sur pince
// ============================================================

$fn = 32;

// Paramètres boîtier
HW = 55;   // Largeur
HD = 45;   // Profondeur
HH = 45;   // Hauteur
WT = 3;    // Épaisseur paroi

// Servo SG90 dimensions (avec 1mm jeu)
SG_W = 25;    // 23 + 2mm jeu
SG_D = 14;    // 12.5 + 1.5mm jeu
SG_H = 31;    // 29 + 2mm jeu
AXIS_D = 7;   // Diamètre trou axe servo

CABLE_W = 10; // Canal câbles
SCREW_D = 3.4; // Trou vis M3

module pan_tilt_housing() {
    difference() {
        // Corps principal
        cube([HW, HD, HH]);

        // ---- SERVO PAN (bas, rotation horizontale) ----
        // Logement centré en bas
        translate([(HW - SG_W)/2, (HD - SG_D)/2, WT])
            cube([SG_W, SG_D, SG_H]);

        // Trou d'axe PAN (vertical, depuis le haut)
        translate([HW/2, HD/2, WT + SG_H - 2])
            cylinder(d = AXIS_D, h = HH - SG_H);

        // ---- SERVO TILT (haut, dans paroi latérale gauche) ----
        // Logement dans la paroi gauche, centré en Y
        translate([-1, (HD - SG_W)/2, HH - SG_H - WT])
            cube([SG_D + 1, SG_W, SG_H]);

        // Trou d'axe TILT (horizontal, traversant vers la droite)
        translate([SG_D + 1, HD/2, HH - SG_H/2 - WT])
            rotate([0, 90, 0])
                cylinder(d = AXIS_D, h = 10);

        // ---- Canal câbles vertical (10×10mm) côté droit ----
        translate([HW - WT - CABLE_W, HD/2 - CABLE_W/2, -1])
            cube([CABLE_W, CABLE_W, HH + 2]);

        // ---- 4 trous M3 base pour vissage sur pince ----
        for (pos = [[10, 10], [10, HD-10], [HW-10, 10], [HW-10, HD-10]]) {
            translate([pos[0], pos[1], -1])
                cylinder(d = SCREW_D, h = WT + 2);
        }

        // ---- Ouverture ventilation face avant ----
        for (z = [8, 18, 28]) {
            translate([-1, HD/2 - 8, z])
                cube([WT + 2, 16, 3]);
        }
    }
}

pan_tilt_housing();
