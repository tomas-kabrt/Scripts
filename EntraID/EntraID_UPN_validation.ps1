# The script checks the existence of the users from the csv in EntraID. Usually it is used to validate all the users on the list are still active in EntraID.
# Prerequisities: Install-Module -Name Microsoft.Graph
# Usabe: pwsh ./update-email.ps1

$csv_file_user = "user_list.csv"

# Connect to Microsoft Graph using PowerShell
Connect-MgGraph -Scopes "User.Read.All"

# Construct the path to the CSV file in the same folder as the script
$csvPath = Join-Path -Path $PSScriptRoot -ChildPath $csv_file_user

# Import the CSV file containing the users to add
$users = Import-Csv -Path $csvPath

# Loop through each member
foreach ($user in $users) {
  $user_id = Get-MgUser -Search "UserPrincipalName:$($user.UserPrincipalName)" -ConsistencyLevel eventual

  if (-not ($user_id)) {
    Write-Output "User $user doesn't exists in EntraID."
  }
}
