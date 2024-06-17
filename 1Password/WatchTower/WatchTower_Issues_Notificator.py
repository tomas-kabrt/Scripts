import os
import subprocess
import json
import csv
import openpyxl
from slack_bolt import App
from datetime import datetime

def extract_vaults(script_dir, all_vaults_file):
    """
    Extracts vault information from an Excel file.

    Parameters:
    script_dir (str): Directory where '1pass_exp.xlsx' is located.

    Returns:
    list: A list of dictionaries with 'vault_id' and 'vault_name' from the Excel file.

    The function loads the Excel file, iterates over its rows, and for each row with a hyperlink,
    it extracts the URL and the display name, storing them in a dictionary. The list of these
    dictionaries is returned.
    """
    # load the xlsx file
    workbook = openpyxl.load_workbook((os.path.join(script_dir, all_vaults_file)))

    # select the active worksheet
    worksheet = workbook.worksheets[0]

    # create an empty list to store the extracted URLs and names
    all_vaults = []

    # iterate over the rows of the worksheet
    for row in worksheet.iter_rows(min_row=1):
        cell = row[0]
        if cell is None:
            continue
        if cell._hyperlink:
            # extract the URL and name from the hyperlink
            url = cell._hyperlink.target
            name = cell.value
            # add the URL and name to the list
            all_vaults.append({'vault_id': url.split('/')[-1], 'vault_name': name})

    # return the list of extracted URLs and names
    return all_vaults

def find_vault_id(vault_name, vaults):
    """
    Search for a vault by name in a list of vault dictionaries.

    Parameters:
    vault_name (str): The name of the vault to search for.
    vaults (list): A list of dictionaries, each representing a vault.

    Returns:
    str: The 'vault_id' of the matching vault.

    Raises:
    ValueError: If no match is found or if multiple matches are found.
    """
    matching_vaults = [vault for vault in vaults if vault['vault_name'] == vault_name]

    if not matching_vaults:
        raise ValueError(f"{vault_name} - No vault found with this name, skipping")

    if len(matching_vaults) > 1:
        raise ValueError(f"{vault_name} - Multiple vaults found with this name, cannot determine which is the correct one, skipping.")

    return matching_vaults[0]['vault_id']

def find_vault_owners(vault_id, vault_name):
    """
    Find the owners of a vault.

    Parameters:
    vault_id (str): The ID of the vault.
    vault_name (str): The name of the vault.

    Returns:
    list: A list of the owners' email addresses.

    Raises:
    subprocess.CalledProcessError: If there is an error running the subprocess command.
    """
    # Run the op group user list command and capture the output
    output = subprocess.check_output(["op", "vault", "user", "list", vault_id, "--format=json"], stderr=subprocess.DEVNULL)

    # Parse the output as JSON
    members = json.loads(output)

    # Initialize a list to track the owners' email addresses
    owners_email = []
    members_email = []

    # Loop through each member and check if they are active and an owner
    for member in members:
        if member['state'] == 'ACTIVE' and 'manage_vault' in member['permissions']:
            owners_email.append(member['email'])
        else:
            members_email.append(member['email'])

    return owners_email, members_email


def send_to_slack(vault_name, vault_id, owners, number_issues, slack_access_token_cred_name):
    """
    Sends a message to the owners of a vault via Slack.

    Parameters:
    vault_name (str): The name of the vault.
    vault_id (str): The ID of the vault.
    owners (list of str): A list of the owners of the vault.
    number_issues (int): The number of security issues found in the vault.

    Returns:
    None
    """
    
    # Load credentials from 1password
    try:
        result = subprocess.run(["op", "item", "get", slack_access_token_cred_name, "--fields", "label=credential"], check=True, capture_output=True, text=True)
        slack_access_token = result.stdout.strip()
    except Exception as e:
        print("Something went wrong with loading of values from 1Password.\n", e)

    # Initialize the Slack app
    app = App(token=slack_access_token)

    for owner_email in owners:
        # Get the user ID from the email address
        response = app.client.users_lookupByEmail(email=owner_email)
        owner_id = response.get('user', {}).get('id')

        if owner_id is None:
            print(f"Could not find a user with the email address {owner_email}")
            continue

         # Send a message to the owner
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hello :wave:,"
                }
            },            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"""
I'm SecOps Bot :robotface:, and I'm assisting the security team in maintaining the security of :1password:1Password vaults and secrets.
With the help of 1Password WatchTower :llighthouse:, I found  *{number_issues}* items in your vault \"*{vault_name}*\" that have recommendation to improve their security.
I am sending this notification message to you as you are one of the owners of the vault.

*What is WatchTower?* WatchTower is a feature in 1Password that helps you find and fix weak, reused, and compromised passwords or fix other security issues.
*How can you check the recomendation?* The easiest way is to use the WatchTower dashboard which shows the items with findings and tips on how to fix or dismiss them.
You can access the dahsboard from browser via <https://team-sumup.1password.eu/vaults/{vault_id}/watchtower|this link> or via the 1Password desktop app in the Watchtower section.
*Do you need to fix all the recommendation?* No, you can dismiss the recommendation if you think it is not relevant. One such examples are Two-factor authentication recommendations, which might be dismissed if you use other authenticator apps like Microsoft Authenticator or Google Authenticator.

Detailed documenation about 1Password Watchtower can be read <https://support.1password.com/watchtower/#use-watchtower-in-the-1password-apps|here>.

*Disclamer:* All owners of the vault will receive this message, and it is sent on a per-vault basis. Therefore, you may receive multiple messages for different vaults. If you have any questions, please feel free to contact #infosec.
                    """
                }
            }
        ]

        # Send a message to the owner
        response = app.client.chat_postMessage(channel=owner_id, text=f"Hi there, this is a security advise from SecOps bot about 1Password vaults" ,blocks=blocks)

        if response.status_code != 200:
            raise ValueError(f"Request to slack returned an error {response.status_code}, the response is:\n{response.text}")


def process_vaults(script_dir, watchtower_export, vaults, slack_access_token_cred_name):
    """
    This function processes the vaults, checking for security issues and sending notifications to the owners.

    Parameters:
    script_dir (str): The directory where the script is located.
    watchtower_export (str): The name of the CSV file containing the WatchTower export.
    vaults (list): A list of the vaults to be processed.

    Returns:
    list: A list of lists, where each inner list contains the vault name, vault ID, and owners.
    """
    report_data = []
    with open(os.path.join(script_dir, watchtower_export)) as f:
        reader = csv.DictReader(f)
        for row in reader:
            vault_name = row['Vault']
            number_issues = row['Issues']
            if int(number_issues) == 0:
                print(vault_name + " - No issues found")
                continue
            try:
                vault_id = find_vault_id(vault_name, vaults)
                owners, members = find_vault_owners(vault_id, vault_name)
                if len(owners) > 0:
                    print(vault_name + " - " + str(number_issues) + " issues - Owners: " + ", ".join(owners))
                    send_to_slack(vault_name, vault_id, owners, number_issues, slack_access_token_cred_name)
                    report_data.append([vault_name, vault_id, "Notified", "; ".join(owners)])
                elif len(members) > 0:
                    print(vault_name + " - " + str(number_issues) + " issues - No Owners, I am not seding any message. But users available " + ", ".join(members))
                    report_data.append([vault_name, vault_id, "No owners found - users available " + ", ".join(members)])
                else:
                    print(vault_name + " - " + str(number_issues) + " issues - No Owners or users, I am not seding any message")
                    report_data.append([vault_name, vault_id, "No owners found"])
            except (ValueError, subprocess.CalledProcessError) as e:
                if isinstance(e, ValueError):
                    print(e)
                    report_data.append([vault_name, "n/a", "Multiple vaults with the same name - skipping"])
                    continue
                elif e.returncode == 6:
                    print(vault_name + " - You aren't authorized to access this resource - most probably the script is not run with 1Password Owner permissions.")
                    report_data.append([vault_name, "n/a", "You aren't authorized to access this resource - most probably the script is not run with 1Password Owner permissions."])
                    continue
                else:
                    raise e
    return report_data

def write_report(script_dir, report_data):
        # Get current date and time
    now = datetime.now()

    # Format as a string
    now_str = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Use in filename
    with open(f"{script_dir}/report_{now_str}.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Vault Name", "Vault ID", "Status", "People contacted"])
        writer.writerows(report_data)


def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    all_vaults_file = '1password_vault_export.xlsx'
    watchtower_export = 'watchtower_report.csv'
    slack_access_token_cred_name = 'Slack_Access_Token'
    report_data = []
        
    vaults = extract_vaults(script_dir, all_vaults_file)
    report_data = []
    try:
        report_data = process_vaults(script_dir, watchtower_export, vaults, slack_access_token_cred_name)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        write_report(script_dir, report_data)

if __name__ == "__main__":
    main()