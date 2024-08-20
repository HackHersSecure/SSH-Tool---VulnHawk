import sys  # Import sys to handle exit
import common_brute_force  # Import the scripts directly
import custom_brute_force
import ssh_key_injection
import user_enumeration
import vulnerability_scanner

# Function to display the tool's logo
def print_logo():
    logo = r"""
          .-.
         (o.o)   
          |=|  
        __|=|__  
       //.\ /.\\ 
      //   o   \\
     /  .  .  .  \
    /_._._._._._._\ 
     -=[ VulnHawk - SSH Exploitation Tool ]=-
    """
    print(logo)

# Function to display the disclaimer to the user
def print_disclaimer():
    disclaimer = """
    Disclaimer:
    This tool is for educational purposes only.
    This project was developed as part of my final year project at university.
    The primary goal is to demonstrate the potential vulnerabilities in SSH
    configurations and how attackers might exploit them. Use this tool
    responsibly and only on systems where you have explicit permission to test.
    Unauthorized use of this tool may violate the law.

    The author assumes no responsibility for any misuse or damage caused by this tool.
    """
    print(disclaimer)

# Main menu function to navigate between different tool options
def main_menu():
    print_logo()
    print_disclaimer()  # Ensure the disclaimer is printed before the menu
    print("\nWelcome to VulnHawk - SSH Exploitation Tool")
    print("\n[1] Common Brute Force Attack")
    print("[2] Custom Brute Force Attack")
    print("[3] SSH Key Injection")
    print("[4] User Enumeration")
    print("[5] Vulnerability Scanner")
    print("[0] Exit")
    
    choice = input("\nSelect an option: ")

    # Call the appropriate script based on the user's choice
    if choice == '1':
        common_brute_force.main()
    elif choice == '2':
        custom_brute_force.main()
    elif choice == '3':
        ssh_key_injection.main()
    elif choice == '4':
        user_enumeration.main()
    elif choice == '5':
        vulnerability_scanner.main()
    elif choice == '0':
        sys.exit()
    else:
        print("[!] Invalid selection.")
        main_menu()

if __name__ == "__main__":
    main_menu()
