# The script counts the accounts that are most probably shared based on a empty or specific attributes.
# Prerequisities: Install-Module -Name Microsoft.Graph
# Usabe: pwsh ./EntraID_shared_accounts.ps1
# Install the Microsoft.Graph.PowerShell module

# Authenticate and authorize your application
Connect-MgGraph -Scopes "User.Read.All"

# It is not possible to filter on empty data fields, so we need to get all the users and check for the empty fields locally
$users = Get-MgUser -All -Property "Id, UserPrincipalName, Mail, EmployeeId, JobTitle"

# Define the regular expression pattern for email addresses that are most likely human users
$pattern = "\.(concentrix|teleperformance|external|terceiro|terceiroite|azure|google)@sumup\.com$"

$count = 0
foreach ($user in $users) {

  # Check if the user has an email address
  if ($null -eq $user.EmployeeId -and $null -eq $user.JobTitle -and $user.UserPrincipalName -notmatch $pattern) {
    $count++
    Write-Host "$($user.Id) $($user.UserPrincipalName)"
    Write-Host "--------"
  }
}

Write-Host "Number of machine users: $count"
