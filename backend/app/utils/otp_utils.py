import random
import string


def generate_otp(size: int = 8, digits: str = None) -> str:
    if not digits:
        digits = string.ascii_uppercase + string.digits
    return "".join(random.choices(digits, k=size))
