import re
import requests
import msal
import subprocess

def load_values_from_1password(Onepass_cred_name):
    """Load values from 1Password."""
    result = subprocess.run(["op", "item", "get", Onepass_cred_name, "--fields", "label=tenant_id"], check=True, capture_output=True, text=True)
    TENANT_ID = result.stdout.strip()

    result = subprocess.run(["op", "item", "get", Onepass_cred_name, "--fields", "label=client_id"], check=True, capture_output=True, text=True)
    CLIENT_ID = result.stdout.strip()

    result = subprocess.run(["op", "item", "get", Onepass_cred_name, "--fields", "label=client_secret"], check=True, capture_output=True, text=True)
    CLIENT_SECRET = result.stdout.strip()

    return CLIENT_ID, CLIENT_SECRET, TENANT_ID

def get_access_token(app):
    """Get an access token from Azure."""
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" in result:
        return result['access_token']
    else:
        raise Exception(f"Error acquiring token: {result}")

def get_users(url, headers):
    """Get users from Microsoft Graph API."""
    while url:
        response = requests.get(url, headers=headers)
        data = response.json()
        yield from data['value']
        url = data.get('@odata.nextLink')

def user_matches_pattern(user, pattern_upn, pattern_employeetype, pattern_department):
    """Check if a user matches the specified patterns."""
    return (
        user['employeeId'] is None and 
        user['jobTitle'] is None and 
        not re.search(pattern_upn, user['userPrincipalName']) and 
        (user['employeeType'] is None or not re.search(pattern_employeetype, user['employeeType'])) and 
        (user['department'] is None or not re.search(pattern_department, user['department']))
    )

def main():
    """Main function."""
    # Patterns for matching users which are most probably machine accounts
    pattern_upn = re.compile(r'\.(concentrix|teleperformance|external|terceiro|terceiroite|terceiratp|azure|google|admin|external)@sumup\.com$')
    pattern_employeetype = re.compile(r'^(ThirdParty|third party)$')
    pattern_department = re.compile(r'^(freelancers|Engineering)$')
    Onepass_cred_name = "EntraID"

    try:
        CLIENT_ID, CLIENT_SECRET, TENANT_ID = load_values_from_1password(Onepass_cred_name)
    except Exception as e:
        print("Something went wrong with loading of values from 1Password.\n", e)
        return
    
    AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
    ENDPOINT = 'https://graph.microsoft.com/v1.0/users?$select=id,userPrincipalName,mail,employeeId,jobTitle,department,employeeType'


    app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )

    try:
        access_token = get_access_token(app)
    except Exception as e:
        print(e)
        return

    headers = {'Authorization': 'Bearer ' + access_token}
    count = 0

    for user in get_users(ENDPOINT, headers):
        if user_matches_pattern(user, pattern_upn, pattern_employeetype, pattern_department):
            print(f"{user['id']} {user['userPrincipalName']})
            count += 1

    print(f"Number of machine users in EntraID: {count}")

if __name__ == "__main__":
    main()