## azureaz_accounts_last_signin.py

The script extract last sign-in for all the users within EntraID and save it all into `entraid_stale_accounts_audit.txt` file. This is ideal script to find out stale accounts in your EntraID tenant.

The credentials needs to be added to `.env` file in the same folder as is the script. The client secrets should be generated as a time limited credentials (ideally just for a few days you need to run the script).

### .env format

```
client_id='Application (client) ID'
client_secret='Client Secret'
tenant_id='Directory (tenant) ID'
```

## EntraID_UPN_validation.ps1

Validate the list of users against the EntraID and return accounts that doesn't exist in the tenant.

## EntraID_add_csv_users_group.ps1

Add the list of users to EntraID group.

## EntraID_email_backfill.ps1

Fills-in email field for the list of users based their UserPrincipalName field. Can be used in conjunction with `EntraID_add_csv_users_group`

## EntraID_shared_accounts.ps1

Try to count the number of possible shared accounts in the EntraID tenant.

### Documentation

https://learn.microsoft.com/it-it/graph/api/user-get?view=graph-rest-beta&tabs=http
