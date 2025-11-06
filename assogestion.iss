; ======================================================
; Script d'installation - Assogestion
; ======================================================

[Setup]
AppName=Assogestion
AppVersion=1.3
AppPublisher=ABO'TECH
AppPublisherURL=https://abotech-informatique.com
DefaultDirName={pf}\Assogestion
DefaultGroupName=Assogestion
OutputDir=Output
OutputBaseFilename=AssogestionSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
WizardStyle=modern
SetupIconFile=logo_abo_tech.ico
UninstallDisplayIcon={app}\AssoGestion.exe
Uninstallable=yes

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis :"

[Files]
; === Fichier exécutable compilé ===
Source: "dist\AssoGestion.exe"; DestDir: "{app}"; Flags: ignoreversion

; === Dossiers sources ===
Source: "IHM\*"; DestDir: "{app}\IHM"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "modele\*"; DestDir: "{app}\modele"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "utils\*"; DestDir: "{app}\utils"; Flags: recursesubdirs createallsubdirs ignoreversion

; === (optionnel) Inclure les tests et la doc si souhaité ===
; Source: "tests\*"; DestDir: "{app}\tests"; Flags: recursesubdirs createallsubdirs ignoreversion
; Source: "Documentation\*"; DestDir: "{app}\Documentation"; Flags: recursesubdirs createallsubdirs ignoreversion

; === Ressources images et config ===
Source: "*.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "*.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "config_assogestion.ini"; DestDir: "{app}"; Flags: ignoreversion
Source: "version.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Assogestion"; Filename: "{app}\AssoGestion.exe"
Name: "{commondesktop}\Assogestion"; Filename: "{app}\AssoGestion.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AssoGestion.exe"; Description: "Lancer Assogestion"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\temp"
