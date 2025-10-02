; DIANA - Script Inno Setup pour créer un installateur Windows professionnel
; Compatible avec Inno Setup 6.x

[Setup]
; Informations de l'application
AppName=DIANA
AppVersion=1.0.0
AppVerName=DIANA 1.0.0
AppPublisher=DIANA Team
AppPublisherURL=https://diana-ai.com
AppSupportURL=https://diana-ai.com/support
AppUpdatesURL=https://diana-ai.com/updates
AppCopyright=Copyright (C) 2025 DIANA Team

; Paramètres d'installation
DefaultDirName={autopf}\DIANA
DefaultGroupName=DIANA
DisableProgramGroupPage=yes
OutputDir=dist\installer
OutputBaseFilename=DIANA-Setup-1.0.0
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=admin

; Interface
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\DIANA.exe
WizardStyle=modern
WizardImageFile=assets\installer-sidebar.bmp
WizardSmallImageFile=assets\installer-logo.bmp

; Licence et infos
LicenseFile=LICENSE
InfoBeforeFile=README.md

; Options de désinstallation
UninstallDisplayName=DIANA - Diagnostic IA
UninstallFilesDir={app}\uninstall

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "Créer une icône dans la barre de lancement rapide"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Lancer DIANA au démarrage de Windows"; GroupDescription: "Options de démarrage:"; Flags: unchecked

[Files]
; Exécutable principal
Source: "dist\DIANA.exe"; DestDir: "{app}"; Flags: ignoreversion

; Modèle chiffré (si présent)
Source: "models\*.enc"; DestDir: "{app}\models"; Flags: ignoreversion recursesubdirs createallsubdirs

; Fichiers de configuration
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Menu Démarrer
Name: "{group}\DIANA"; Filename: "{app}\DIANA.exe"; Comment: "Lancer DIANA - Diagnostic IA"
Name: "{group}\{cm:UninstallProgram,DIANA}"; Filename: "{uninstallexe}"
Name: "{group}\Guide utilisateur"; Filename: "{app}\README.md"

; Bureau
Name: "{autodesktop}\DIANA"; Filename: "{app}\DIANA.exe"; Tasks: desktopicon; Comment: "Diagnostic Intelligent Automatisé"

; Barre de lancement rapide
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\DIANA"; Filename: "{app}\DIANA.exe"; Tasks: quicklaunchicon

; Démarrage automatique
Name: "{userstartup}\DIANA"; Filename: "{app}\DIANA.exe"; Tasks: startupicon

[Registry]
; Ajouter au registre pour le démarrage automatique (si l'option est cochée)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "DIANA"; ValueData: "{app}\DIANA.exe"; Tasks: startupicon

; Informations de l'application dans le registre
Root: HKLM; Subkey: "Software\DIANA"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKLM; Subkey: "Software\DIANA"; ValueType: string; ValueName: "Version"; ValueData: "1.0.0"

[Run]
; Proposer de lancer l'application après installation
Filename: "{app}\DIANA.exe"; Description: "Lancer DIANA maintenant"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Fermer l'application avant désinstallation
Filename: "{cmd}"; Parameters: "/C taskkill /F /IM DIANA.exe"; Flags: runhidden

[UninstallDelete]
; Supprimer les fichiers de données utilisateur (avec confirmation)
Type: filesandordirs; Name: "{app}\data"
Type: filesandordirs; Name: "{app}\logs"

[Code]
// Code Pascal pour personnalisation avancée

function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Vérifier si une ancienne version est installée
  if RegKeyExists(HKLM, 'Software\DIANA') then
  begin
    if MsgBox('Une version de DIANA est déjà installée. Voulez-vous la mettre à jour ?', 
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Actions après installation
    MsgBox('DIANA a été installé avec succès !' + #13#10 + #13#10 +
           'Vous pouvez maintenant lancer l''application depuis :' + #13#10 +
           '- Le Bureau' + #13#10 +
           '- Le menu Démarrer' + #13#10 +
           '- Le raccourci créé', mbInformation, MB_OK);
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
  
  // Message avant désinstallation
  if MsgBox('Êtes-vous sûr de vouloir désinstaller DIANA ?' + #13#10 + #13#10 +
            'Toutes vos données locales (analyses effectuées) seront supprimées.',
            mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDNO then
  begin
    Result := False;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Nettoyer le registre
    RegDeleteKeyIncludingSubkeys(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Run\DIANA');
    RegDeleteKeyIncludingSubkeys(HKLM, 'Software\DIANA');
  end;
end;

