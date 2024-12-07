import secrets
import string
from cryptainer.logger import log


class PasswordGenerator:
    def __init__(self, max_length=20):
        """
        Initializes the PasswordGenerator with the given configuration.
        """
        self.passgen_length = max_length  # Default length is 20 if not specified

    def generate_password(self) -> str:
        """
        Generates a secure password based on the configured passgen_length.

        :return: A randomly generated secure password.
        """
        if not isinstance(self.passgen_length, int) or self.passgen_length <= 0:
            log.error(f"Invalid passgen_length: {self.passgen_length}. Using default length of 20.")
            self.passgen_length = 20

        # Define the character pool for the password
        characters = string.ascii_letters + string.digits + string.punctuation

        # Generate a random password
        password = ''.join(secrets.choice(characters) for _ in range(self.passgen_length))

        # log.info(f"Generated a password of length {self.passgen_length}")
        return password


if __name__ == "__main__":
    # Create a PasswordGenerator instance
    password_generator = PasswordGenerator(30)

    # Generate a password
    password = password_generator.generate_password()

    # Output the password
    print(f"Generated Password: {password}")
