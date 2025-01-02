import random
import string

def generate_password(length: int = 12, use_uppercase: bool = True, use_digits: bool = True, use_special: bool = True) -> str:
    """
    Generates a random password.

    Args:
        length (int): The length of the password. Default is 12.
        use_uppercase (bool): Include uppercase letters. Default is True.
        use_digits (bool): Include digits. Default is True.
        use_special (bool): Include special characters. Default is True.

    Returns:
        str: The generated password.
    
    Raises:
        ValueError: If the password length is less than 8.
    """
    
    # Initialize the characters to use
    characters = string.ascii_lowercase  # Lowercase letters

    if use_uppercase:
        characters += string.ascii_uppercase  # Add uppercase letters

    if use_digits:
        characters += string.digits  # Add digits

    if use_special:
        characters += string.punctuation  # Add special characters

    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")

    # Generate the password
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


if __name__ == "__main__":
    # Example usage
    try:
        # Generate a custom password
        custom_password = generate_password(length=30, use_uppercase=True, use_digits=True, use_special=True)
        print(f"Generated custom password: {custom_password}")
        
    except ValueError as e:
        print(f"Error: {e}")
