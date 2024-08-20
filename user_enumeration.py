import os
import paramiko
import socket
import time
import sys  # Import sys to handle exit

def check_username(host, username):
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
        print(f" Exception Message: {str(e)}")
    except socket.error as e:
        print(f"[!] Connection error while checking username: {username} - {e}")
    except Exception as e:
        print(f"[!] Unexpected error: {str(e)}")
    else:
        # If by some strange occurrence it doesn't throw an exception, the username exists.
        print(f"[+] Valid username found: {username}")
    finally:
        client.close()

def enumerate_users(host, username_file):
    """Iterates over a list of usernames to identify valid ones."""
    try:
        with open(username_file, 'r') as file:
            usernames = file.read().splitlines()
    except IOError:
        print("[!] Could not open the username file.")
        return

    for username in usernames:
        check_username(host, username)

def main():
    print("SSH User Enumeration Script started...\n")
    
    host = input("Enter the target SSH server IP: ")

    # Ask the user whether they want to use the inbuilt username file or upload their own
    use_inbuilt = input("Do you want to use the inbuilt username.txt file? (y/n): ").strip().lower()
    
    if use_inbuilt == 'y':
        username_file = os.path.join(os.path.dirname(__file__), 'username.txt')
    else:
        username_file = input("Enter the path to your username list file: ").strip()
        while not os.path.isfile(username_file):
            print("[!] The file does not exist. Please try again.")
            username_file = input("Enter the path to your username list file: ").strip()

    print(f"\n[+] Using username file: {username_file}")
    
    print("\n[+] Enumerating users...")
    enumerate_users(host, username_file)

    print("\n[+] User enumeration completed.")
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
