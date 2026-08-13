; Setup script for AgenticBrowser Windows package
; Build with Inno Setup: https://jrsoftware.org/isdl.php

[Setup]
AppId=AgenticBrowser
AppName=AgenticBrowser
AppVersion=0.1.0
DefaultDirName={autopf}\AgenticBrowser
DefaultGroupName=AgenticBrowser
OutputDir=release
OutputBaseFilename=AgenticBrowser-Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "agentic-browser-extension\dist\*"; DestDir: "{app}\extension"; Flags: recursesubdirs
Source: "agentic-browser-web-ui\dist\*"; DestDir: "{app}\web-ui"; Flags: recursesubdirs
Source: "scripts\*"; DestDir: "{app}\scripts"; Flags: recursesubdirs

[Icons]
Name: "{group}\AgenticBrowser"; Filename: "{app}\scripts\run.ps1"
Name: "{group}\Uninstall AgenticBrowser"; Filename: "{uninstallexe}"

[Run]
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\scripts\run.ps1"""; Flags: postinstall nowait
