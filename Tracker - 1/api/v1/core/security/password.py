from pwdlib import PasswordHash

# Create a password hashing context using the
# library's recommended secure hashing algorithm.
pwd_context = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash a plain-text password securely.

    The resulting hash includes:
    - hashing algorithm metadata
    - salt
    - configured hashing parameters

    Args:
        password: Plain-text user password.

    Returns:
        Secure hashed password string.
    """

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against a stored hash.

    Args:
        plain_password: User-provided plain-text password.
        hashed_password: Stored password hash from the database.

    Returns:
        True if the password matches the hash.
        False otherwise.
    """

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )