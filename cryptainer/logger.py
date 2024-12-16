import logging
from colorama import Fore, Style
from getpass import getpass

class CustomLogger:
    """
    A customizable logger with simple prefixes ([+], [-], etc.) for common messages,
    and a debug mode that shows detailed logs with timestamps.
    """
    def __init__(self, name: str, debug: bool = False):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Console handler
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self._get_formatter(debug))
        self.logger.addHandler(self.console_handler)

        # Internal state for debug mode
        self.debug_mode = debug

    def _get_formatter(self, debug: bool):
        """
        Returns the appropriate formatter based on debug mode.
        """
        if debug:
            return logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        else:
            return logging.Formatter("%(message)s")

    def set_debug(self, debug: bool):
        """
        Enable or disable debug mode dynamically.
        """
        self.debug_mode = debug
        self.console_handler.setFormatter(self._get_formatter(debug))

    def info(self, message: str):
        """
        Log an informational message with a [*] prefix.
        """
        self.logger.info(Fore.BLUE + "[*] " + Style.RESET_ALL + str(message))

    def success(self, message: str):
        """
        Log a success message with a [+] prefix.
        """
        self.logger.info(Fore.GREEN + "[+] " + Style.RESET_ALL + str(message))

    def error(self, message: str):
        """
        Log an error message with a [-] prefix.
        """
        self.logger.error(Fore.RED + "[-] " + Style.RESET_ALL + str(message))

    def warning(self, message: str):
        """
        Log a warning message with a [!] prefix.
        """
        self.logger.warning(Fore.YELLOW + "[!] " + Style.RESET_ALL + str(message))

    def debug(self, message: str):
        """
        Log a debug message with a [DEBUG] prefix.
        """
        if self.debug_mode:
            self.logger.debug(Fore.MAGENTA + "[DEBUG] " + Style.RESET_ALL + str(message))
        # Debug messages are suppressed when debug mode is off.

    def prompt(self, message: str):
        password = getpass(Fore.YELLOW + "[>] " + Style.RESET_ALL + str(message))
        return password

# Instantiate the logger
log = CustomLogger("VolumX")

# Example usage
if __name__ == "__main__":
    # Normal mode
    log.info("This is an informational message.")
    log.success("The operation was successful.")
    log.error("An error occurred.")
    log.warning("This is a warning message.")
    log.debug("Debugging details (this won't appear by default).")

    # Enable debug mode
    log.set_debug(True)
    log.debug("Debugging details (now visible with timestamp).")
    log.info("Another informational message with debug mode enabled.")