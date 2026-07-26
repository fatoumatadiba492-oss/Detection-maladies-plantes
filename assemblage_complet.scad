// ============================================================
// ASSEMBLAGE COMPLET - Système de détection maladies plantes
// ESP32-CAM + Servo Pan/Tilt + Pince de fixation
// Hauteur totale: ~170mm
// ============================================================

$fn = 32;

// ============================================================
// PARAMÈTRES GLOBAUX
// ============================================================

// Pince
W=70; D=45; H_CLAMP=70; WT=5;
SLOT_W=26; SLOT_D=35; SLOT_H=45;

// Housing servo
HW=55; HD=45; H_HOUSING=45; WT2=3;
SG_W=25; SG_D=14; SG_H=31; AXIS_D=7;

// Boîtier ESP32-CAM
CW=35; CD=32; H_CAM=55; WT3=2.5;

// Axe servo (connecteur entre pince et housing)
SERVO_AXLE_D = 6;

// ============================================================
// MODULE 1 : PINCE DE FIXATION (Base)
// ============================================================
module pince() {
    difference() {
        cube([W, D, H_CLAMP]);

        // Slot C (rebord jardinière 25mm + 1mm jeu)
        translate([(W-SLOT_W)/2, -1, 0])
            cube([SLOT_W, SLOT_D+1, SLOT_H]);

        // Canal câbles 10×10mm
        translate([W-WT-10, D/2-5, -1])
            cube([10, 10, H_CLAMP+2]);

        // 4 trous M3 plateau supérieur
        for (p = [[12,10],[12,D-10],[W-12,10],[W-12,D-10]])
            translate([p[0], p[1], H_CLAMP-WT-1])
                cylinder(d=3.4, h=WT+2);

        // Chanfrein interne slot pour clipsage facile
        translate([(W-SLOT_W)/2, SLOT_D-2, SLOT_H-6])
            rotate([45,0,0]) cube([SLOT_W, 5, 5]);
    }
}

// ============================================================
// MODULE 2 : CONNECTEUR PIVOT (entre pince et servo pan)
// Pièce intermédiaire qui relie la pince au servo horizontal
// ============================================================
module pivot_connector() {
    difference() {
        union() {
            // Corps du pivot
            cylinder(d=20, h=12);
            // Bride de fixation plate (se visse sur la pince)
            translate([-HW/2, -HD/2, -8])
                cube([HW, HD, 8]);
        }
        // Trou axe servo central
        cylinder(d=SERVO_AXLE_D, h=15, center=true);

        // 4 trous M3 pour vissage sur pince (alignés avec les trous pince)
        dx = HW/2 - 12; dy = HD/2 - 10;
        for (p = [[-dx,-dy],[-dx,dy],[dx,-dy],[dx,dy]])
            translate([p[0], p[1], -9])
                cylinder(d=3.4, h=10);
    }
}

// ============================================================
// MODULE 3 : PAN-TILT HOUSING (corps principal avec 2 servos)
// ============================================================
module pan_tilt_housing() {
    difference() {
        cube([HW, HD, H_HOUSING]);

        // Logement servo PAN (bas, rotation horizontale)
        translate([(HW-SG_W)/2, (HD-SG_D)/2, WT2])
            cube([SG_W, SG_D, SG_H+1]);

        // Trou axe PAN vers le bas (connexion avec pivot_connector)
        translate([HW/2, HD/2, -1])
            cylinder(d=AXIS_D, h=WT2+2);

        // Logement servo TILT (paroi gauche, rotation verticale)
        translate([-1, (HD-SG_W)/2, H_HOUSING-SG_H-WT2])
            cube([SG_D+1, SG_W, SG_H]);

        // Trou axe TILT (horizontal, vers bras caméra)
        translate([SG_D+1, HD/2, H_HOUSING-SG_H/2-WT2])
            rotate([0,90,0])
                cylinder(d=AXIS_D, h=12);

        // Canal câbles 10×10mm (côté droit)
        translate([HW-WT2-10, HD/2-5, -1])
            cube([10, 10, H_HOUSING+2]);

        // 4 trous M3 base pour vissage sur pince
        for (p = [[10,10],[10,HD-10],[HW-10,10],[HW-10,HD-10]])
            translate([p[0], p[1], -1])
                cylinder(d=3.4, h=WT2+2);

        // Fentes ventilation face avant
        for (z = [8, 20, 32])
            translate([-1, HD/2-8, z])
                cube([WT2+2, 16, 4]);
    }
}

// ============================================================
// MODULE 4 : BRAS DE LIAISON SERVO TILT → CAMÉRA
// Bras articulé qui connecte le servo TILT au boîtier caméra
// ============================================================
module servo_arm_tilt() {
    difference() {
        union() {
            // Corps du bras (L-shape)
            cube([30, 10, 8]);
            // Bride de fixation côté servo
            translate([0, -5, -4])
                cylinder(d=14, h=12);
            // Bride de fixation côté caméra
            translate([30, 0, 0])
                cube([10, CW, 8]);
        }
        // Trou axe servo tilt
        translate([0, 0, -5])
            cylinder(d=SERVO_AXLE_D, h=14);
        // 2 trous M3 pour fixer le boîtier caméra
        for (y = [CW/2-10, CW/2+10])
            translate([35, y, -1])
                cylinder(d=3.4, h=10);
    }
}

// ============================================================
// MODULE 5 : BOÎTIER ESP32-CAM (fermé, amélioré)
// ============================================================
module boitier_esp32cam() {
    difference() {
        cube([CW, CD, H_CAM]);

        // Évidement intérieur
        translate([WT3, WT3, WT3])
            cube([CW-2*WT3, CD-2*WT3, H_CAM-WT3+1]);

        // Ouverture objectif (face avant Y=0): 12×12mm
        translate([(CW-12)/2, -1, H_CAM-38])
            cube([12, WT3+2, 12]);

        // Ouverture flash LED: 8×8mm
        translate([(CW-8)/2+12, -1, H_CAM-36])
            cube([8, WT3+2, 8]);

        // Trou USB/alimentation bas: 12×6mm centré
        translate([(CW-12)/2, (CD-6)/2, -1])
            cube([12, 6, WT3+2]);

        // Ouverture antenne WiFi haut: 5×20mm
        translate([CW-WT3-6, (CD-20)/2, H_CAM-WT3-1])
            cube([5, 20, WT3+2]);

        // Fentes ventilation latérales
        for (z = [12, 25, 38]) {
            translate([-1, (CD-14)/2, z]) cube([WT3+2, 14, 3]);
            translate([CW-WT3-1, (CD-14)/2, z]) cube([WT3+2, 14, 3]);
        }

        // 2 trous M3 base pour fixation sur bras servo
        for (x = [(CW-20)/2, (CW+0)/2+10])
            translate([x, CD/2, -1])
                cylinder(d=3.4, h=WT3+2);
    }

    // Bossages internes pour maintenir l'ESP32-CAM
    for (p = [[WT3,WT3],[CW-WT3-2,WT3],[WT3,CD-WT3-2],[CW-WT3-2,CD-WT3-2]])
        translate([p[0], p[1], WT3]) cube([2, 2, 4]);
}

// ============================================================
// ASSEMBLAGE FINAL - toutes les pièces en position
// ============================================================

// Z positions
Z_CLAMP   = 0;
Z_PIVOT   = H_CLAMP;
Z_HOUSING = H_CLAMP + 8;       // 8mm = hauteur bride pivot
Z_CAM     = Z_HOUSING + H_HOUSING + 5;  // 5mm bras servo

// Centrage horizontal (tout aligné sur X/Y)
OFFSET_X = (W - HW) / 2;   // Centre housing sur pince
OFFSET_Y = (D - HD) / 2;

// 1. Pince de fixation (bas)
color("gray", 0.9)
    translate([0, 0, Z_CLAMP])
        pince();

// 2. Pivot connector (liaison pince ↔ servo)
color("darkgray", 0.9)
    translate([W/2, D/2, Z_PIVOT])
        pivot_connector();

// 3. Pan-Tilt Housing (milieu)
color("gray", 0.85)
    translate([OFFSET_X, OFFSET_Y, Z_HOUSING])
        pan_tilt_housing();

// 4. Bras servo TILT (liaison housing ↔ caméra)
color("darkgray", 0.85)
    translate([OFFSET_X - 30, OFFSET_Y + HD/2 - CW/2, Z_CAM - 8])
        servo_arm_tilt();

// 5. Boîtier ESP32-CAM (haut)
color("gray", 0.8)
    translate([OFFSET_X - 30 + 30, OFFSET_Y + HD/2 - CD/2, Z_CAM])
        boitier_esp32cam();

// ============================================================
// NOTE: Exporter chaque pièce individuellement pour impression
// Commenter toutes les sections sauf celle à exporter,
// puis cliquer "Download STL"
// ============================================================
