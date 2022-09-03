"""

- CSH User Tool 'auth.py' Source Code -

(C) Cubeflix 2022 (CSH)

"""


# ---------- IMPORTS ----------

from .misc import *


# ---------- FUNCTIONS ----------

def hash_password(password):

    """Hash a password using SHA-256, and return the resulting digest as a hexadecimal string.
           Args: password -> The password string to hash."""

    return hashlib.sha256(bytes(password, ENCODING)).hexdigest()

