# Custom Script Library for CS RTR

## MacOS

### uninstallScriptMacOs.py

The script to uninstall Falcon sensor from MacOS operating system via RTR.

#### Usage

1. Get maintenance token for the host that you wish to uninstall via Falcon Console
2. Initiate RTR connection the the host
3. Run following command:
`runscript -CloudFile="uninstallScriptMacOs" -CommandLine="[maintenance token]" ``

## Windows

### uninstallScriptWindows.ps1
The script to uninstall Falcon sensor from Windows operating system via RTR.

#### Usage

1. Get maintenance token for the host that you wish to uninstall via Falcon Console
2. Initiate RTR connection the the host
3. Run following command:
`runscript -CloudFile="uninstallScriptWindows" -CommandLine="-maintenanceToken [maintenance token]"``
