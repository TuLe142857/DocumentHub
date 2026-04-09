import random
import string


def generate_otp(size: int = 8, digits: str = None) -> str:
    if not digits:
        digits = string.ascii_uppercase + string.digits
    if size <= 0:
        raise ValueError("size must be > 0")
    if len(digits) <= 0:
        raise ValueError("len of digits must be > 0")
    return "".join(random.choices(digits, k=size))
