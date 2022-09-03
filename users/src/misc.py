"""

- CSH User Tool 'misc.py' Source Code -

(C) Cubeflix 2022 (CSH)

"""


# ---------- IMPORTS ----------

# JSON formatting
import json

# Hashing tools
import hashlib


# ---------- CONSTANTS ----------

VERSION = '1.0'


ENCODING = 'utf-8'


# ---------- CLASSES ----------

class UserToolError(Exception):

    """The main CSH user tool error class."""

