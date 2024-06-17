# The script add the users from the csv to a EntraID group. This can be useful in cases when you need to add multiple specific people to a group.
# Prerequisities: Install-Module -Name Microsoft.Graph
# Usabe: pwsh ./EntraID_add_csv_users_group.ps1

### TO EDIT ###
$group_name = "1Password SSO"
$csv_file_user = "1pass_sso_users.csv"

# Connect to Microsoft Graph using PowerShell
Connect-MgGraph -Scopes "GroupMember.ReadWrite.All", "User.Read.All"

# one of the quirks with the New-MgGroupMember cmdlet is that it is not possible to use username, but it requires the directory ObjectID instead
$group = Get-MgGroup -Search "DisplayName:$group_name" -ConsistencyLevel eventual

# Construct the path to the CSV file in the same folder as the script
$csvPath = Join-Path -Path $PSScriptRoot -ChildPath $csv_file_user

# Import the CSV file containing the users to add
$users = Import-Csv -Path $csvPath

# Loop through each member
foreach ($user in $users) {
  $user_id = Get-MgUser -Search "UserPrincipalName:$($user.UserPrincipalName)" -ConsistencyLevel eventual

  if ($($user_id.UserPrincipalName)) {
    # Adding user to the group
    Write-Output "User $($user_id.UserPrincipalName) $($user_id.id) is added to $($group.DisplayName)."
    New-MgGroupMember -GroupId $group.id -DirectoryObjectId $user_id.id
  }
  else {
    Write-Output "User $user is not in EntraID."
  }
}
