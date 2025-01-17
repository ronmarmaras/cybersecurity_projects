#!/bin/bash
# passwd_info.sh - display and save password information for all users

# Prompt user for file name
read -p "Enter the file name to save the password information: " file_name

# Check if a file name was provided
if [ -z "$file_name" ]; then
  echo "No file name provided. Exiting."
  exit 1
fi

# Initialize the file
echo "Password information for all users" > "$file_name"
echo "===================================" >> "$file_name"

# Retrieve user list and append password information to the file
list=$(cut -d : -f 1 /etc/passwd)
for user in $list; do
  echo "Password information for $user" >> "$file_name"
  sudo chage -l $user >> "$file_name"
  echo "----------" >> "$file_name"
done

echo "Password information has been saved to $file_name."
