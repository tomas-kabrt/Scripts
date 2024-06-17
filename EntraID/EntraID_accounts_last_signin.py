# Define imports and config dictionary
import msal
import requests
import time
from dotenv import load_dotenv
import os

# loading credentials from .env file
load_dotenv()

config = {
  'client_id': os.getenv("client_id"),
  'client_secret': os.getenv("client_secret"),
  'authority': 'https://login.microsoftonline.com/' + str(os.getenv("tenant_id")),
  'scope': ['https://graph.microsoft.com/.default']
}

# Define a function that takes parameter 'url' and executes a graph call.
# Optional parameter 'pagination' can be set to False to return only first page of graph results
def make_graph_call(url, pagination=True):
  # Firstly, try to lookup an access token in cache
  token_result = client.acquire_token_silent(config['scope'], account=None)

  # Log that token was loaded from the cache
  if token_result:
    print('Access token was loaded from cache.')

  # If token not available in cache, acquire a new one from Azure AD
  if not token_result:
    token_result = client.acquire_token_for_client(scopes=config['scope'])
    print('New access token aquired from AAD')

   # If token available, execute Graph query
  if 'access_token' in token_result:
    headers = {'Authorization': 'Bearer ' + token_result['access_token']}
    graph_results = []

    i = 0
    while url:
      try:
        graph_result = requests.get(url=url, headers=headers).json()
        graph_results.extend(graph_result['value'])
        if (pagination == True):
          i += 1
          print(i)
          url = graph_result['@odata.nextLink']
          time.sleep(10)
        else:
          url = None
      except:
         break
  else:
    print(token_result.get('error'))
    print(token_result.get('error_description'))
    print(token_result.get('correlation'))

  return graph_results

# Create an MSAL instance providing the client_id, authority and client_credential parameters
client = msal.ConfidentialClientApplication(config['client_id'], authority=config['authority'], client_credential=config['client_secret'])

# Make an MS Graph call
url = 'https://graph.microsoft.com/beta/users?$select=userPrincipalName,signInActivity&top=100'
data = make_graph_call(url, pagination=True)

# Open a file named 'azuread_stale_accounts_audit.txt' in write mode using a 'with' statement
with open('azuread_stale_accounts_audit.txt', 'w') as f:
    # Write a header line to the file that contains the column names for the data
    f.write("userPrincipalName;lastSignInDateTime;lastNonInteractiveSignInDateTime\n")

    # Loop through the 'data' list and write each line to the file
    for d in data:
        # Check if the 'signInActivity' property is present in the item
        if 'signInActivity' in d:
            # Get the 'lastSignInDateTime' and 'lastNonInteractiveSignInDateTime' values from the 'signInActivity' property
            last_sign_in = d['signInActivity'].get('lastSignInDateTime', 'never sign-in')
            last_non_interactive_sign_in = d['signInActivity'].get('lastNonInteractiveSignInDateTime', 'never sign-in')
            # Format the data into a string with semicolons as separators
            line = f"{d['userPrincipalName']};{last_sign_in};{last_non_interactive_sign_in}\n"
        else:
            # If the 'signInActivity' property is not present, write "never sign-in" instead
            line = f"{d['userPrincipalName']};never sign-in;never sign-in\n"
        # Write the formatted data to the file
        f.write(line)
