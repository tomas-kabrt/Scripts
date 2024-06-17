import subprocess
import json
import os

# this script checks the list of the users that will be added under sso againts the 1Password-SSO, so we are not sending emails to already added people

# Set the name of the group
group = "1Password-SSO"
file = "1password_8th.txt"

# Grant the user access to the new group
# Run the op group user list command and capture the output
output = subprocess.check_output(["op", "group", "user", "list", group, "--format=json"])
members = json.loads(output)
# Extract the email addresses of the members
onepass_members_emails = [member["email"] for member in members]


script_dir = os.path.dirname(__file__)

with open(os.path.join(script_dir, file), 'r') as f:
    emails = [line.strip() for line in f]

count = 0
# Print only the emails that are not in members
for email in emails:
    if email not in onepass_members_emails:
        count += 1
        print(email)

print("Total cound is " + str(count))