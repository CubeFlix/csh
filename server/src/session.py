"""

- CSH Server 'session.py' Source Code -

(C) Cubeflix 2021 (CSH)

"""


# ---------- IMPORTS ----------

from .misc import *


# ---------- CLASSES ----------

class Session:

	"""The main CSH session object."""

	def __init__(self, addr, session_id, username, timestamp, server, expire_after=None):

		"""Create the session object.
		   Args: addr -> The address associated with the session.
		         session_id -> The session ID for the session.
		         username -> The username for the session.
		         timestamp -> The timestamp when the session was created.
		         server -> The server object the session is from.
		         expire_after -> If the session should expire, this should be an integer containing the number of seconds we should expire after without new commands. Defaults to None, meaning no expiration."""

		self.addr = addr
		self.session_id = session_id
		self.username = username
		self.timestamp = timestamp
		self.server = server
		self.expire_after = expire_after

		self.current_directory = os.path.normpath('')

		self.expires = None

		# Calculate when to expire the session
		if self.expire_after:
			self.expires = timestamp + datetime.timedelta(seconds=self.expire_after)

	def validate(self):

		"""Check if the session is still valid."""

		# Check if the session has been forcibly destroyed
		if not self.session_id in self.server.sessions:
			return False

		# Check if the session is expired
		if self.expires:
			if datetime.datetime.now() > self.expires:
				# Expired, so not a valid session
				
				# Remove this session
				del self.server.sessions[self.session_id]

				# Return false
				return False

			# If not expired, renew the session
			self.expires = datetime.datetime.now() + datetime.timedelta(seconds=self.expire_after)

		return True

	def validate_path(self, path):

		"""Validate a path for the session.
		   Args: path -> The path to check."""

		# Get the full path
		full_path = self.get_full_path(path)

		# Compare the path with the server's path
		if len(full_path) < len(os.path.abspath(self.server.path)) or not full_path.startswith(os.path.abspath(self.server.path)):
			# Path is not valid
			return False

		return True

	def get_full_path(self, path):

		"""Get a full path for a given path.
		   Args: path -> The given path."""

		if os.path.normpath(path).startswith('\\') or os.path.normpath(path).startswith('/'):
			return os.path.abspath(os.path.join(self.server.path, os.path.normpath(path)[1 : ]))

		# Get the full path
		return os.path.abspath(os.path.join(self.server.path, os.path.join(self.current_directory, path)))

	def __repr__(self):

		"""Return a string representation of the object."""

		return "<Session " + self.username + ">"

	def __str__(self):

		 """Return a string representation of the object."""

		 return self.__repr__()


class SessionIDGenerationItem:

	"""An internal session ID generation queue item."""

	def __init__(self):

		"""Create the queue item."""

		self.session_id = None
		self.finished = False

	def finish(self, session_id):

		"""Finish the session generation.
		   Args: session_id -> The new session ID."""

		self.session_id = session_id
		self.finished = True

	def wait_until_finished(self):

		"""Wait until the session ID is created and the item is finished."""

		while not self.finished:
			pass

	def __repr__(self):

		"""Return a string representation of the object."""

		return "<SessionIDGenerationItem finished=" + str(self.finished) + ">"

	def __str__(self):

		 """Return a string representation of the object."""

		 return self.__repr__()
