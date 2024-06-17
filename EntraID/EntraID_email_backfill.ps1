# The script fills-in email field for the list of users based their UserPrincipalName field. The script was created to backfill the UPN that is required for proper functionality of 1Password SSO.
# Prerequisities: Install-Module -Name Microsoft.Graph
# Usabe: pwsh ./EntraID_email_backfill.ps1

# Connect to Microsoft Graph using PowerShell
Connect-MgGraph -Scopes "Group.Read.All", "User.ReadWrite.All"

# Set the name of the group to retrieve users from
$groupname = "1password SSO"

# Get the group object using the group name
$group = Get-MgGroup -Filter "displayName eq '$groupname'"

# Get all the users in the group
$groupMembers = Get-MgGroupMember -GroupId $group.Id -All

# Loop through each member
foreach ($member in $groupMembers) {
  # Get the user details
  $user = Get-MgUser -UserId $member.Id

  # Check if the user has an email address
  if ($null -eq $user.Mail) {
    # Set the email address to the userprincipalname
    $user.Mail = $user.UserPrincipalName

    # Update the user object in Azure AD
    Update-MgUser -UserId $user.Id -Mail $user.Mail
      
    Write-Output "Updated email address for $($user.DisplayName) to $($user.Mail)."
  } else {
    Write-Output "User $($user.DisplayName) already have an email filled in."
  }
}
