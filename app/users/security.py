from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


def generate_password_hash(pw_rw):
    ph = PasswordHasher()
    return ph.hash(pw_rw)


def verify_password(pw_hash, pw_rw):
    ph = PasswordHasher()
    verified = False
    msg = ""
    try:
        verified = ph.verify(pw_hash, pw_rw)
    except VerifyMismatchError as e:
        verified = False
        msg = "Invalid password."
    except Exception as e:
        msg = f"Unexcepted error: \n{e}"
    return verified, msg
