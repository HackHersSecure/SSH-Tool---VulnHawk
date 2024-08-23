import os
import paramiko
import socket
import time
import sys  # Import sys to handle exit
import datetime

# Report class to gather and save the results
class Report:
    def __init__(self, target_ip, attack_type):
        self.target_ip = target_ip
        self.attack_type = attack_type
        self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.details = []
        self.valid_usernames = []

    def add_detail(self, description):
        self.details.append(description)

    def add_valid_username(self, username):
        self.valid_usernames.append(username)

    def generate_report(self):
        report_content = f"""
        SSH Exploitation Report
        =======================
        
        Target IP: {self.target_ip}
        Attack Type: {self.attack_type}
        Date: {self.date}
        
        Summary:
        --------
        Valid Usernames Found: {len(self.valid_usernames)}
        
        Details:
        --------
        """
        for idx, detail in enumerate(self.details, 1):
            report_content += f"{idx}. {detail}\n"

        if self.valid_usernames:
            report_content += "\nValid Usernames:\n----------------\n"
            for idx, username in enumerate(self.valid_usernames, 1):
                report_content += f"{idx}. {username}\n"
        else:
            report_content += "\nNo valid usernames were found.\n"

        report_content += "\nRecommendations:\n-----------------\n"
        report_content += "1. Implement account lockout policies to prevent enumeration.\n"
        report_content += "2. Use consistent timing for authentication failures to prevent timing attacks.\n"
        report_content += "3. Regularly audit SSH logs to detect and respond to enumeration attempts.\n"

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

def check_username(host, username, report):
    """Attempts to connect to SSH with the given username and analyzes the response."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    invalid_password = "invalid_password"  # Intentionally incorrect password

    try:
        print(f"[*] Checking username: {username}")
        start_time = time.time()
        client.connect(hostname=host, username=username, password=invalid_password, timeout=5)
    except paramiko.AuthenticationException as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"[-] Authentication failed for username: {username} (response time: {duration:.2f}s)")
        report.add_detail(f"Checked username: {username} - Authentication failed (response time: {duration:.2f}s)")
    except socket.error as e:
        print(f"[!] Connection error while checking username: {username} - {e}")
        report.add_detail(f"Connection error while checking username: {username} - {e}")
    except Exception as e:
        print(f"[!] Unexpected error: {str(e)}")
        report.add_detail(f"Unexpected error while checking username: {username} - {str(e)}")
    else:
        # If by some strange occurrence it doesn't throw an exception, the username exists.
        print(f"[+] Valid username found: {username}")
        report.add_valid_username(username)
    finally:
        client.close()

def enumerate_users(host, username_file, report):
    """Iterates over a list of usernames to identify valid ones."""
    try:
        with open(username_file, 'r') as file:
            usernames = file.read().splitlines()
    except IOError:
        print("[!] Could not open the username file.")
        report.add_detail(f"Could not open the username file: {username_file}")
        return

    for username in usernames:
        check_username(host, username, report)

def main():
    print("SSH User Enumeration Script started...\n")
    
    host = input("Enter the target SSH server IP: ")

    # Initialize report with attack type
    report = Report(target_ip=host, attack_type="user_enumeration")

    # Ask the user whether they want to use the inbuilt username file or upload their own
    use_inbuilt = input("Do you want to use the inbuilt username.txt file? (y/n): ").strip().lower()
    
    if use_inbuilt == 'y':
        username_file = os.path.join(os.path.dirname(__file__), 'username.txt')
        report.add_detail(f"Using inbuilt username file: {username_file}")
    else:
        username_file = input("Enter the path to your username list file: ").strip()
        while not os.path.isfile(username_file):
            print("[!] The file does not exist. Please try again.")
            username_file = input("Enter the path to your username list file: ").strip()
        report.add_detail(f"Using custom username file: {username_file}")

    print(f"\n[+] Using username file: {username_file}")
    
    print("\n[+] Enumerating users...")
    enumerate_users(host, username_file, report)

    print("\n[+] User enumeration completed.")
    
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
