# The script counts the accounts that are most probably shared based on a empty or specific attributes.
# Prerequisities: Install-Module -Name Microsoft.Graph
# Usabe: pwsh ./EntraID_honeypot_account.ps1

# Import the module
Import-Module Microsoft.Graph.Users.Authentication

# Define variables for the
$displayName = "Backup Admin"
$userPrincipalName = "backup.admin@test.com"
$firstName = "Backup"
$lastName = "Admin"
$password = [guid]::NewGuid().ToString() # Generate a random password

# Convert the password to a secure string
$securePassword = ConvertTo-SecureString -String $password -AsPlainText -Force

# Authenticate to Microsoft Graph
Connect-MgGraph -Scopes User.ReadWrite.All

# Create the user
New-MgUser -DisplayName $displayName -UserPrincipalName $userPrincipalName -MailNickname ($userPrincipalName.Split("@")[0]) -GivenName $firstName -Surname $lastName -PasswordProfile_Password $password -ForceChangePasswordNextSignIn $true

# Output the generated password
Write-Host "User $userPrincipalName created with the password: $password"
