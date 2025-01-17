import socket
from scapy.all import *
from threading import Thread
import ipaddress

# Timeout for each socket connection
timeout = 2

# Results storage for file output
scan_results = []


# Function to grab banner with advanced handling for specific protocols
def grab_banner(ip, port):
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        
        if port == 80 or port == 8080:  # HTTP
            s.sendall(b"GET / HTTP/1.1\r\nHost: %s\r\n\r\n" % ip.encode())
            banner = s.recv(1024).decode().strip()
        elif port == 21:  # FTP
            banner = s.recv(1024).decode().strip()
        elif port == 25:  # SMTP
            banner = s.recv(1024).decode().strip()
        else:
            banner = s.recv(1024).decode().strip()
        
        if banner:
            result = f"[+] {ip}:{port} - {banner}"
        else:
            result = f"[-] {ip}:{port} - No banner found"
        
        print(result)
        scan_results.append(result)
        s.close()
    except Exception as e:
        result = f"[-] {ip}:{port} - Unable to connect ({str(e)})"
        print(result)
        scan_results.append(result)


# Function to perform a SYN scan to identify open ports
def syn_scan(ip, port):
    src_port = RandShort()  # Use a random source port
    packet = IP(dst=ip) / TCP(sport=src_port, dport=port, flags="S")
    response = sr1(packet, timeout=timeout, verbose=0)
    
    if response:
        if response.haslayer(TCP) and response.getlayer(TCP).flags == 0x12:
            # SYN-ACK received, port is open
            print(f"[+] {ip}:{port} is open.")
            scan_results.append(f"[+] {ip}:{port} is open.")
            return True
    return False


# Function to handle the scan of a single port
def scan_port(ip, port):
    if syn_scan(ip, port):
        grab_banner(ip, port)
    else:
        result = f"[-] {ip}:{port} is closed or filtered."
        print(result)
        scan_results.append(result)


# Function to perform multi-threaded port scanning and banner grabbing
def scan_ports(ip, ports):
    threads = []
    for port in ports:
        t = Thread(target=scan_port, args=(ip, port))
        t.start()
        threads.append(t)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()


# Function to allow the user to input a custom list of ports
def get_ports_from_user():
    user_input = input("Enter a list of ports (comma-separated), or press Enter to use the default common ports: ")
    
    if user_input.strip():
        try:
            # Parse the user's input into a list of integers
            ports = [int(port.strip()) for port in user_input.split(',')]
            return ports
        except ValueError:
            print("Invalid input! Please enter only comma-separated numbers.")
            return get_ports_from_user()
    else:
        # Default list of common ports
        return [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 3306, 3389, 5900, 8080]


# Function to allow the user to specify a range of ports
def get_port_range_from_user():
    try:
        start_port = int(input("Enter the starting port: "))
        end_port = int(input("Enter the ending port: "))
        
        if start_port < 1 or end_port > 65535 or start_port > end_port:
            print("Invalid range! Please enter a valid range between 1 and 65535.")
            return get_port_range_from_user()
        
        # Create a list of ports within the specified range
        return list(range(start_port, end_port + 1))
    
    except ValueError:
        print("Please enter valid integers.")
        return get_port_range_from_user()


# Function to get the list of IP addresses from a subnet
def get_ip_range():
    subnet = input("Enter a subnet in CIDR format (e.g., 192.168.1.0/24): ")
    try:
        ip_network = ipaddress.ip_network(subnet, strict=False)
        return [str(ip) for ip in ip_network.hosts()]
    except ValueError:
        print("Invalid subnet! Please enter a valid CIDR.")
        return get_ip_range()


# Function to save scan results to a file
def save_results_to_file():
    filename = input("Enter the filename to save results (e.g., scan_results.txt): ")
    try:
        with open(filename, 'w') as file:
            file.write("\n".join(scan_results))
        print(f"Results saved to {filename}")
    except Exception as e:
        print(f"Failed to save results: {str(e)}")


# Main function
if __name__ == "__main__":
    print("Multi-IP Banner Grabbing Tool")
    
    # Get the list of IPs to scan
    ip_list = get_ip_range()
    print(f"Scanning {len(ip_list)} IP addresses...")
    
    # Get the dynamic list or range of ports from the user
    choice = input("Do you want to (1) enter a list of ports or (2) specify a range of ports? Enter 1 or 2: ")
    ports_to_scan = get_ports_from_user() if choice == '1' else get_port_range_from_user()
    
    # Scan each IP address
    for ip in ip_list:
        print(f"\nScanning IP: {ip}")
        scan_ports(ip, ports_to_scan)
    
    # Save results to a file
    save_results_to_file()
