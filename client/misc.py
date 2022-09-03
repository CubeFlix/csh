"""

- CSH Client 'misc.py' Source Code -

(C) Cubeflix 2021 (CSH)

"""


# ---------- IMPORTS ----------

# Socket functionality
import socket

# SSL functionality
import ssl


# ---------- CONSTANTS ----------

ENCODING = 'utf-8'

VERSION = '1.3.3'


# ---------- CLASSES ----------

class CSHClientError(Exception):

	"""The base CSH client exception class."""


class SerializingException(Exception):

	"""The base serializing exception."""


class DeserializingException(Exception):

	"""The base deserializing exception."""


class StatusResponse:

	"""The status response object."""

	def __init__(self, status):

		"""Create the status response.
		   Args: status -> The status response dictionary."""

		self.code = status['code']
		self.status = status['status']
		self.timestamp = status['timestamp']
		self.version = status['version']
		self.name = status['name']
		self.os = status['os']
		self.language = status['language']
		
		self.original_status = status

	def __repr__(self):

		"""Return a string representation of the object."""

		return "<StatusResponse status=" + self.status + " version=" + self.version + " name=\"" + self.name + "\" os=" + self.os + " language=" + self.language + ">"

	def __str__(self):

		 """Return a string representation of the object."""

		 return self.__repr__()


class PathExistence:

	"""The path existence response object."""

	def __init__(self, response):

		"""Create the path existence response object.
		   Args: status -> The response dictionary."""

		self.exists = response['exists']
		self.isfile = response['isfile']
		self.isdir = response['isdir']
		self.path_type = ('file' if self.isfile else 'dir') if self.exists else None
		
		self.original_response = response

	def __repr__(self):

		"""Return a string representation of the object."""

		return "<PathExistence exists=" + str(self.exists) + " path_type=" + str(self.path_type) + ">"

	def __str__(self):

		 """Return a string representation of the object."""

		 return self.__repr__()


class UserInfoResponse:

	"""The user information response object."""

	def __init__(self, response):

		"""Create the user info response object.
		   Args: status -> The response dictionary."""

		self.password_hash = response["password_hash"]
		self.permissions = response["permissions"]
		
		self.original_response = response

	def __repr__(self):

		"""Return a string representation of the object."""

		return "<UserInfoResponse>"

	def __str__(self):

		 """Return a string representation of the object."""

		 return self.__repr__()
