; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
AppName=Python Data Shell
AppVersion=0.1
OutputBaseFilename=PyDataShellInstaller
AppPublisher=Tom Trainor, Craig Biwer, Joanne Stubbs, Peter Eng, MattNewville, Univ of Alaska, Univ of Chicago
AppPublisherURL=http://cars.uchicago.edu/ifeffit/tdl/Pds
AppCopyright=Copyright (C) 2013 Tom Trainor, Craig Biwer et al
DefaultDirName=C:\Program Files\PyDataShell
DefaultGroupName=PyDataShell
AlwaysRestart=no
LicenseFile=C:\Program Files\PyDataShell\COPYING.txt

[Dirs]
Name: "{localappdata}\PyDataShell"

[Files]
Source: "C:\Program Files\PyDataShell\*";   DestDir: "{app}";  Flags: "recursesubdirs"
Source: "C:\Program Files\PyDataShell\README.txt"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\pds"; WorkingDir: "{userappdata}\pds"; Filename: "{app}\pds.exe";     IconFilename: "{app}\TDL.ico"
Name: "{group}\Uninstall PDS"; Filename: "{uninstallexe}"


