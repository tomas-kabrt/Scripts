import subprocess
import os

# Set the name of the group
group = "1Password-ABCD"
# The name of the file with the emails of the users to be added to the group - one email per line
file = "users.txt"

script_dir = os.path.dirname(__file__)

with open(os.path.join(script_dir, file), 'r') as f:
    emails = [line.strip() for line in f]

for email in emails:
	# Assign the user to the new group
    subprocess.run(["op", "group", "user", "grant", "--group", group, "--user", email])
    print("User {} is added to group {}".format(email, group))