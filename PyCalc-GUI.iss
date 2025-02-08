[Setup]
AppName=PyCalc GUI
AppVerName=PyCalc GUI v1.0
AppPublisher=Chill-Astro
DefaultDirName={autopf}\Chill-Astro\PyCalc-GUI
DefaultGroupName=Chill-Astro
UninstallDisplayIcon={app}\PycalcGUI.exe
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=Output
OutputBaseFilename=PyCalcGUI-Setup
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\Master\Chill-Astro\PyCalc-GUI\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
[Icons]
Name: "{group}\PyCalc GUI"; Filename: "{app}\PycalcGUI.exe"; IconFilename: "{app}\Pycalc.ico"
Name: "{commondesktop}\PyCalc GUI"; Filename: "{app}\PycalcGUI.exe"; IconFilename: "{app}\Pycalc.ico"; Tasks: desktopicon