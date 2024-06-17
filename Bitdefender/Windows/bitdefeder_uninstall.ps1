<#
Description:
Uninstall Bitdefender
The script is provided "AS IS" with no warranties.
#>
function Check_BD {
  $check = (Get-Item "HKLM:Software\Bitdefender\Endpoint Security\Bdec\" -EA Ignore).Property -contains "install_version"
  return $check;
}

# Fill the unsintall password for Bitdefender
$UNINTALL_PW = ""
$exitCode = 0

try {
	if (Check_BD) {
		# Define variables
		$url = "https://download.bitdefender.com/SMB/Hydra/release/bst_win/uninstallTool/BEST_uninstallTool.exe"
		$tempDir = "$env:TEMP\BEST_uninstallTool.exe"
		$params = "/bdparams /password=`"$UNINTALL_PW`" -noWait"

		# Download the file to the temp directory
		Invoke-WebRequest -Uri $url -OutFile $tempDir

		$executableCertHash = (Get-AuthenticodeSignature ($tempDir)).SignerCertificate.Thumbprint

		if ($executableCertHash -eq "09F279D3828B8FD31B771A7596D702198739D180") {
			# Run the uninstall tool with params and silently
			$process = Start-Process -FilePath $tempDir -ArgumentList $params -NoNewWindow -Wait
		}

		Remove-Item -LiteralPath $tempDir -Force
	}
} catch {
  Remove-Item -LiteralPath $tempDir -Force
  $_
  $exitCode = -1
}
exit $exitCode
