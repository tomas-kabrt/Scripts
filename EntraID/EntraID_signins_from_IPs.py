import msal
import requests
import os
import subprocess

ip_address_file = "ip_addresses.txt"
ip_address_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ip_address_file)
batch_size = 50
total_sign_ins = 0
Onepass_cred_name = "EntraID"

# Load credentials from 1password
try:
    result = subprocess.run(["op", "item", "get", Onepass_cred_name, "--fields", "label=tenant_id"], check=True, capture_output=True, text=True)
    tenant_id = result.stdout.strip()

    result = subprocess.run(["op", "item", "get", Onepass_cred_name, "--fields", "label=client_id"], check=True, capture_output=True, text=True)
    client_id = result.stdout.strip()

    result = subprocess.run(["op", "item", "get", Onepass_cred_name, "--fields", "label=client_secret"], check=True, capture_output=True, text=True)
    client_secret = result.stdout.strip()
except Exception as e:
    print("Something went wrong with loading of values from 1Password.\n", e)




# Create MSAL app object
app = msal.ConfidentialClientApplication(
    client_id=client_id,
    client_credential=client_secret,
    authority=f"https://login.microsoftonline.com/{tenant_id}"
)

# Authenticate with Microsoft Graph API
result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
access_token = result["access_token"]

# Read IP addresses from file
with open(ip_address_file, "r") as f:
    ip_addresses = f.read().splitlines()

# Loop through IP addresses in batches and retrieve sign-in logs
for i in range(0, len(ip_addresses), batch_size):
    batch = ip_addresses[i:i+batch_size]
    ip_address_filter = "' or ipAddress eq '".join(batch)
    sign_in_url = "https://graph.microsoft.com/v1.0/auditLogs/signIns"
    sign_in_params = {
        "$filter": f"ipAddress eq '{ip_address_filter}'"
    }
    sign_in_headers = {
        "Authorization": f"Bearer {access_token}"
    }
    try:
        sign_in_response = requests.get(sign_in_url, params=sign_in_params, headers=sign_in_headers)
        sign_in_logs = sign_in_response.json()["value"]
        total_sign_ins += len(sign_in_logs)
        print(f"Sign-in logs for IP addresses {batch[0]} - {batch[-1]}:")
        for log in sign_in_logs:
            print(f"IP: {log['ipAddress']}, User: {log['userDisplayName']}")
    except Exception as e:
        print("Something went wrong.\n", e)

print(f"Total sign-in events: {total_sign_ins}")