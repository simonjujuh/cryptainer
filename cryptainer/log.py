from colorama import Fore, Style
from getpass import getpass

def print_info(message: str):
    """
    Display an informational message with a [*] prefix.
    """
    print(Fore.BLUE + Style.BRIGHT + "[*] " + Style.RESET_ALL + str(message))

def print_success(message: str):
    """
    Display a success message with a [+] prefix.
    """
    print(Fore.GREEN + Style.BRIGHT + "[+] " + Style.RESET_ALL + str(message))

def print_error(message: str):
    """
    Display an error message with a [-] prefix.
    """
    print(Fore.RED + Style.BRIGHT + "[-] " + Style.RESET_ALL + str(message))

def print_warning(message: str):
    """
    Display a warning message with a [!] prefix.
    """
    print(Fore.YELLOW + Style.BRIGHT + "[!] " + Style.RESET_ALL + str(message))

def print_debug(message: str, debug_mode: bool):
    """
    Display a debug message with a [DEBUG] prefix if debug mode is enabled.
    """
    if debug_mode:
        print(Fore.MAGENTA + Style.BRIGHT + "[DEBUG] " + Style.RESET_ALL + str(message))

def prompt(message: str):
    """
    Prompt the user for input with a [>] prefix.
    """
    return getpass(Fore.MAGENTA + Style.BRIGHT + "[*] " + Style.RESET_ALL + str(message))

# Example usage
if __name__ == "__main__":
    debug_mode = False  # Set debug mode to False by default

    # Normal mode
    print_info("This is an informational message.")
    print_success("The operation was successful.")
    print_error("An error occurred.")
    print_warning("This is a warning message.")
    print_debug("Debugging details (this won't appear by default).", debug_mode)
    prompt("Please enter your password: ")

    # Enable debug mode
    debug_mode = True
    print_debug("Debugging details (now visible).", debug_mode)
    print_info("Another informational message with debug mode enabled.")
