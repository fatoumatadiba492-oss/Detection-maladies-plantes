// ============================================================
// BOÎTIER ESP32-CAM (fermé, amélioré)
// ESP32-CAM: 27mm × 40mm × 15mm
// Boîtier ext: 35mm(L) × 32mm(l) × 55mm(H)
// Parois: 2.5mm
// Ouvertures: objectif 12×12, flash 8×8, USB 12×6
// Fentes ventilation + ouverture antenne WiFi
// ============================================================

$fn = 32;

// Paramètres
CW = 35;     // Largeur ext
CD = 32;     // Profondeur ext
CH = 55;     // Hauteur ext
WT = 2.5;    // Épaisseur paroi

// Ouvertures
LENS_W = 12;    // Trou objectif
LENS_H = 12;
FLASH_W = 8;    // Trou flash
FLASH_H = 8;
USB_W = 12;     // Trou USB
USB_H = 6;

module boitier_esp32cam() {
    difference() {
        // Corps externe
        cube([CW, CD, CH]);

        // Évidement intérieur (fond WT, pas de couvercle = ouvert en haut)
        translate([WT, WT, WT])
            cube([CW - 2*WT, CD - 2*WT, CH - WT + 1]);

        // ---- Face avant (Y=0) ----
        // Trou objectif: centré en X, à 18mm du bas
        translate([(CW - LENS_W)/2, -1, CH - 38])
            cube([LENS_W, WT + 2, LENS_H]);

        // Trou flash LED: à droite de l'objectif
        translate([(CW - FLASH_W)/2 + 13, -1, CH - 36])
            cube([FLASH_W, WT + 2, FLASH_H]);

        // ---- Face bas (Z=0): trou USB/alimentation centré ----
        translate([(CW - USB_W)/2, (CD - USB_H)/2, -1])
            cube([USB_W, USB_H, WT + 2]);

        // ---- Face haut (Z=CH): ouverture antenne WiFi ----
        translate([CW - WT - 6, (CD - 20)/2, CH - WT - 1])
            cube([5, 20, WT + 2]);

        // ---- Fentes ventilation latérales gauche (X=0) ----
        for (z = [12, 25, 38]) {
            translate([-1, (CD - 16)/2, z])
                cube([WT + 2, 16, 3]);
        }

        // ---- Fentes ventilation latérales droite (X=CW) ----
        for (z = [12, 25, 38]) {
            translate([CW - WT - 1, (CD - 16)/2, z])
                cube([WT + 2, 16, 3]);
        }

        // ---- Rainure de guidage pour ESP32-CAM (rails intérieurs) ----
        translate([WT, WT, WT + 5])
            cube([1.5, CD - 2*WT, CH]);
        translate([CW - WT - 1.5, WT, WT + 5])
            cube([1.5, CD - 2*WT, CH]);
    }

    // ---- Bossages internes pour caler l'ESP32-CAM ----
    translate([WT, WT, WT])
        cube([2, 2, 3]);
    translate([CW - WT - 2, WT, WT])
        cube([2, 2, 3]);
    translate([WT, CD - WT - 2, WT])
        cube([2, 2, 3]);
    translate([CW - WT - 2, CD - WT - 2, WT])
        cube([2, 2, 3]);
}

boitier_esp32cam();
