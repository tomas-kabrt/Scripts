import subprocess
import json

# Set the name of the groups
old_group_name = "1Password-ABCD"
new_group_name = "1Password-DCBA"

# Run the op group user list command and capture the output
output = subprocess.check_output(["op", "group", "user", "list", old_group_name, "--format=json"])

# Parse the output as JSON
members = json.loads(output)

# Extract the email addresses of the members
emails = [member["email"] for member in members]

for email in emails:
    if email == "tomas.kabrt@sumup.com":
        print("Skipping")
        continue

	# Grant the user access to the new group
    subprocess.run(["op", "group", "user", "grant", "--group", new_group_name, "--user", email])
    print("User {} is added to group {}".format(email, new_group_name))

	# Revoke the user's access to the old group
    subprocess.run(["op", "group", "user", "revoke", "--group", old_group_name, "--user", email])
    print("User {} is removed from group {}".format(email, old_group_name))
