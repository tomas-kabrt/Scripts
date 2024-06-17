import subprocess
import json
import os

# this script extract the members that didn't completed their migration

# Set the name of the group
group = "1Password-SSO-deferred-deadline"
file = "1password_status.txt"

# Grant the user access to the new group
# Run the op group user list command and capture the output
output = subprocess.check_output(["op", "group", "user", "list", group, "--format=json"])
users = json.loads(output)

#print(users)

script_dir = os.path.dirname(__file__)

with open(os.path.join(script_dir, file), 'r') as f:
    names = [line.strip() for line in f]

# Find the users whose names are in the list and output their email addresses
count = 0
for user in users:
    if user['name'] in names:
        print(user['email'])
        count += 1

print("Total count is: " + str(count))