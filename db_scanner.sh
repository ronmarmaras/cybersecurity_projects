#!/bin/bash

# This script scans a range of IP addresses to find hosts with a specified database installed.

# Check if nmap is installed
if ! command -v nmap &> /dev/null; then
  echo "Error: nmap is not installed. Please install it before running this script."
  exit 1
fi

# Prompt user for the database name
read -p "Enter the database name (e.g., MySQL, PostgreSQL, MongoDB, etc.): " db_name
if [[ -z "$db_name" ]]; then
  echo "No database name provided. Exiting."
  exit 1
fi

# Prompt user for the port number and validate it
read -p "Enter the port number to scan for (e.g., 3306 for MySQL): " port
if [[ ! $port =~ ^[0-9]+$ ]] || [ "$port" -le 0 ] || [ "$port" -gt 65535 ]; then
  echo "Invalid port number. Port must be between 1 and 65535. Exiting."
  exit 1
fi

# Prompt user for the IP range or CIDR
read -p "Enter the starting IP address or CIDR (e.g., 192.168.1.1 or 192.168.1.0/24): " FirstIP
if [[ ! $FirstIP =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] && [[ ! $FirstIP =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]{1,2}$ ]]; then
  echo "Invalid IP address or CIDR format. Exiting."
  exit 1
fi

if [[ $FirstIP =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
  read -p "Enter the last octet of the last IP address (e.g., 254): " LastOctetIP
  if [[ ! $LastOctetIP =~ ^[0-9]{1,3}$ ]] || [ "$LastOctetIP" -gt 254 ]; then
    echo "Invalid last octet. Exiting."
    exit 1
  fi
  ip_range="$FirstIP-${FirstIP%.*}.$LastOctetIP"
else
  ip_range="$FirstIP"
fi

# Prepare file names with timestamps
timestamp=$(date +'%Y%m%d_%H%M%S')
output_file="${db_name}_scan_$timestamp.log"
filtered_file="${db_name}_scan_filtered_$timestamp.log"

# Perform the scan with optimized speed
echo "Scanning IPs in range $ip_range on port $port for $db_name..."
nmap --min-rate 1000 -sT "$ip_range" -p "$port" -oG "$output_file" > /dev/null

# Filter results
grep "open" "$output_file" > "$filtered_file"

# Display results and save to log
if [ -s "$filtered_file" ]; then
  echo "The following hosts have $db_name open on port $port:"
  cat "$filtered_file"
else
  echo "No hosts with $db_name open on port $port were found."
fi

echo "Raw scan results saved to: $output_file"
echo "Filtered results saved to: $filtered_file"