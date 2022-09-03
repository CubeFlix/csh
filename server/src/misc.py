"""

- CSH Server 'misc.py' Source Code -

(C) Cubeflix 2021 (CSH)

"""


# ---------- IMPORTS ----------

# Operating system level access
import os

# System signals
import signal

# Path and filesystem modules
import shutil

# JSON formatting
import json

# Socket functionality
import socket

# SSL functionality
import ssl

# Multi threading capabilities for asynchronous requests
import threading, queue

# Hashing tools
import hashlib

# Random token generation
import secrets

# Timestamp generation and calculation tools
import datetime, time

# For logging purposes
import logging

# Server rate limitation
import pyrate_limiter

# System
import sys


# ---------- CONSTANTS ----------

ENCODING = 'utf-8'

VERSION = '1.3.3'

LANG = 'python'


# Rate limiter duration constants
MINUTE, HOUR, DAY, MONTH = pyrate_limiter.Duration.MINUTE, pyrate_limiter.Duration.HOUR, pyrate_limiter.Duration.DAY, pyrate_limiter.Duration.MONTH


# ---------- LOGGING ----------

# Logging constants
VERBOSE = True

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

CH = logging.StreamHandler()
CH.setLevel(logging.DEBUG)

FORMATTER = logging.Formatter('CSH (' + VERSION + ') - %(asctime)s - %(levelname)s - %(message)s')
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)


# ---------- FUNCTIONS ----------

def set_verbose(verbose):

	"""Sets the verbosity of the logger.
	   Args: verbose -> Should the logger write to the console."""

	global VERBOSE
	global LOGGER

	VERBOSE = verbose
	
	if VERBOSE:
		logging.disable(logging.NOTSET)
	else:
		logging.disable(sys.maxsize)


def set_file_handler(filename):

	"""Creates a file handler for the logger.
	   Args: filename -> The name of the file to write the logs to."""

	global FH
	global LOGGER
	global FORMATTER

	FH = logging.FileHandler(filename)
	FH.setLevel(logging.DEBUG)
	FH.setFormatter(FORMATTER)
	LOGGER.addHandler(FH)


# ---------- CLASSES ----------

class CSHError(Exception):

	"""The base CSH exception class."""


class SerializingException(Exception):

	"""The base serializing exception."""


class DeserializingException(Exception):

	"""The base deserializing exception."""
