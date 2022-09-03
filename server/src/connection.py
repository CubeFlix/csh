"""

- CSH Server 'connection.py' Source Code -

(C) Cubeflix 2021 (CSH)

"""


# ---------- IMPORTS ----------

from .misc import *
from .binary import *
from .auth import *
from .session import *


# ---------- CLASSES ----------

class Connection:

	"""The main CSH connection class."""

	def __init__(self, connection_socket, addr, server):

		"""Create the connection object.
		   Args: connection_socket -> The connection socket object.
		         addr -> The address of the connection.
		         server -> The CSH server object."""

		self.connection_socket = connection_socket
		self.addr = addr
		self.server = server

	def respond(self, data, error=False, keepalive=False):

		"""Respond to the client with data.
		   Args: data -> The data to send to the client.
		         error -> If this is an error message. Defaults to false.
		         keepalive -> If the socket should be kept alive for further use. Defaults to false."""

		# Respond with data
		try:
			# Convert the data to binary
			try:
				binary = serialize(data)

			except SerializingException as e:
				# Error with serializing the data
				self.respond({'code': 21, 'error': "Serialization error. Data might be too big. Consider sending it in packets. [" + str(e) + "]"}, error=True)
				return

			# Create the payload
			payload = b'CSH'

			# Add the length of the data
			payload += int.to_bytes(len(binary), 8, byteorder="little")

			# Add the binary data
			payload += binary

			# Send the payload
			for chunk_start in range(0, len(payload), 1048576):
				# Send each chunk
				self.connection_socket.send(payload[chunk_start : chunk_start + 1048576])

			# End the socket
			if not keepalive:
				self.connection_socket.close()

		except Exception as e:
			# Exception with responding
			LOGGER.error("ERROR WITH RESPONDING: [" + str(e) + "]")

			if not error:
				# Respond with error
				self.respond({'code': 7, 'error': "Error responding: [" + str(e) + "]"}, error=True)

	def handle(self):

		"""Handle the connection."""

		# Check rate limiter
		if self.server.rate_limit:
			try:
				# Try to acquire the item
				self.server.rate_limiter.try_acquire(self.addr[0])

			except pyrate_limiter.BucketFullException:
				# Cannot make request, so send error back
				self.respond({'code': 20, 'error': "Exceeded rate limit."})
				return

		try:
			# Read the first three characters, which should be "CSH"
			if not self.connection_socket.recv(3) == b'CSH':
				self.respond({'code': 8, 'error': "Invalid CSH header."}, error=True)
				return

			# Get the length of the data
			length = int.from_bytes(self.connection_socket.recv(8), byteorder="little")

			# Get the rest of the data
			binary_data = bytearray()

			# Get each chunk
			while len(binary_data) < length:
				binary_data += self.connection_socket.recv(1048576)

			self.data = deserialize(binary_data)

			# Get the command ID
			if not 'command' in self.data:
				self.respond({'code': 9, 'error': "Command ID not in data."}, error=True)
				return

			self.command_id = self.data["command"]

			# Check for login or info commands, both of which do not require a session
			# Also check for an admin command, which is separate from regular commands
			# Also check for clear all user sessions commands, which do require logins but do not require sessions
			if self.command_id in ('L', 'I', 'A', 'CS'):
				if self.command_id == 'L':
					# Log in command
					self.log_in()

				elif self.command_id == 'I':
					# Get the server status
					self.status()

				elif self.command_id == 'A':
					# Run an administrator command
					self.admin()

				elif self.command_id == 'CS':
					# Clear all user sessions
					self.clear_user_sessions()

				return

			# Get the command
			if not self.command_id in self.server.ACCEPTABLE_COMMAND_IDS:
				self.respond({'code': 10, 'error': "Command ID is invalid."}, error=True)
				return

			# Get the session ID and username for the command
			if not ('username' in self.data and 'session_id' in self.data):
				# No username and session ID
				self.respond({'code': 15, 'error': "Commands must have username and session ID provided."}, error=True)
				return

			session_id = self.data['session_id']
			username = self.data['username']

			# Get the session object
			if not session_id in self.server.sessions:
				# Invalid session ID
				self.respond({'code': 16, 'error': "Invalid session ID."}, error=True)
				return

			session = self.server.sessions[session_id]

			# Check the session's username and address
			if not session.username == username or not session.addr[0] == self.addr[0]:
				# Invalid session
				self.respond({'code': 1, 'error': "Invalid session."}, error=True)
				return

			# Try to run the command
			try:
				command = self.command(username, session)

			except Exception as e:
				# Error while running command
				LOGGER.error("ERROR WITH PREFORMING COMMAND: [" + str(e) + "]")

				self.respond({'code': 17, 'error': "Error preforming command: [" + str(e) + "]"}, error=True)
				return

			# Get the output data and respond with it
			self.respond(command.data, error=(not command.data['code'] == 0))

		except Exception as e:
			# Exception with handling connection
			LOGGER.error("ERROR HANDLING CONNECTION: [" + str(e) + "]")

			self.respond({'code': 11, 'error': "Error handling connection: [" + str(e) + "]"}, error=True)

	def command(self, username, session):

		"""Preform a command.
		   Args: username -> The username for the command.
		         session -> The session for the command."""

		# Get the arguments for the command
		if not 'args' in self.data:
			# No arguments
			self.respond({'code': 16, 'error': "Arguments must be included in data."}, error=True)
			return

		args = self.data['args']

		LOGGER.info("PREFORMING [" + self.server.COMMANDS[self.command_id].__name__ + "] COMMAND - [" + username + "] - [" + ((str(args)[:75] + '...') if len(str(args)) > 75 else str(args)) + "]")

		# Create the command object
		try:
			command = self.server.COMMANDS[self.command_id](session, **args)
			
		except Exception as e:
			# Error with creating command
			self.respond({'code': 22, 'error': "Error with creating command: [" + str(e) + "]"}, error=True)
			return

		# Preform the command
		command.preform()

		# Return the command object
		return command

	def log_in(self):

		"""Accept a log in command."""

		LOGGER.info("LOG IN REQUEST FROM " + str(self.addr))

		# Check that the data has a username and password
		if not ('username' in self.data and 'password' in self.data):
			# No username and password
			self.respond({'code': 12, 'error': "Log in command must have username and password provided."}, error=True)

		# Get the username and password hash
		username, password_hash = self.data['username'], hash_password(self.data['password'])

		# Check the users data in the server
		if not username in self.server.users:
			# User doesn't exist
			self.respond({'code': 13, 'error': "User doesn't exist."}, error=True)

		# Check that the password hashes match
		if not self.server.users[username]['password_hash'] == password_hash:
			# Invalid password
			self.respond({'code': 14, 'error': "Invalid password."}, error=True)

		# Successfully authenticated, so create the session

		# Check if there are too many sessions for the user
		if self.server.session_limit:
			# Get number of existing sessions for user
			num_existing_sessions = [(1 if i.username == username else 0) for i in list(self.server.sessions.values())].count(1)

			if num_existing_sessions >= self.server.session_limit:
				# Too many sessions
				self.respond({'code': 24, 'error': "Too many sessions for user."}, error=True)
				return

		# Get a valid session ID by creating a session generation request
		req = SessionIDGenerationItem()

		# Add the request to the queue
		self.server.session_gen_queue.put(req)

		# Wait until the request is finished
		req.wait_until_finished()

		# Get a timestamp
		timestamp = datetime.datetime.now()

		# Get the expiration time
		if self.server.allow_change_expire:
			# Server allows changing expiration time, so get the time
			if 'expiration_time' in self.data:
				# Expiration time is in login request
				expiration_time = self.data['expiration_time']

			else:
				# Expiration time is not in data, so use default
				expiration_time = self.server.default_expire
		else:
			# Server does not allow changing expiration time
			expiration_time = self.server.default_expire

		# Create and add the new session
		self.server.sessions[req.session_id] = Session(self.addr, req.session_id, username, timestamp, self.server, expire_after=expiration_time)

		# Respond with the session ID and timestamp
		self.respond({'code': 0, 'session_id': req.session_id, 'timestamp': tuple(timestamp.utctimetuple())})

	def status(self):

		"""Accept a server status/ping command."""

		LOGGER.info("STATUS REQUEST FROM " + str(self.addr))

		self.respond({'code': 0, 'status': 'OK', 'timestamp': tuple(datetime.datetime.now().utctimetuple()), 'version': VERSION, 'name': self.server.server_name, 'os': os.name, 'language': LANG})

	def admin(self):

		"""Accept an administrator command."""

		LOGGER.info("ADMIN REQUEST FROM " + str(self.addr))

		# Check that the data has a username and password
		if not ('username' in self.data and 'password' in self.data):
			# No username and password
			self.respond({'code': 12, 'error': "Log in command must have username and password provided."}, error=True)

		# Get the username and password hash
		username, password_hash = self.data['username'], hash_password(self.data['password'])

		# Check the users data in the server
		if not username in self.server.users:
			# User doesn't exist
			self.respond({'code': 13, 'error': "User doesn't exist."}, error=True)

		# Check that the password hashes match
		if not self.server.users[username]['password_hash'] == password_hash:
			# Invalid password
			self.respond({'code': 14, 'error': "Invalid password."}, error=True)

		# Successfully authenticated, so preform the admin command

		# Get the admin command ID
		if not 'admin_command' in self.data:
			self.respond({'code': 9, 'error': "Command ID not in data."}, error=True)
			return

		self.admin_command_id = self.data["admin_command"]

		# Get the command
		if not self.admin_command_id in self.server.ACCEPTABLE_ADMIN_COMMAND_IDS:
			self.respond({'code': 10, 'error': "Command ID is invalid."}, error=True)
			return

		# Preform the command
		try:
			# Get the arguments for the command
			if not 'args' in self.data:
				# No arguments
				self.respond({'code': 16, 'error': "Arguments must be included in data."}, error=True)
				return

			args = self.data['args']

			LOGGER.info("PREFORMING ADMIN [" + self.server.ADMIN_COMMANDS[self.admin_command_id].__name__ + "] COMMAND - [" + username + "] - [" + ((str(args)[:75] + '...') if len(str(args)) > 75 else str(args)) + "]")

			# Create the command object
			try:
				command = self.server.ADMIN_COMMANDS[self.admin_command_id](self.server, **args)
				
			except Exception as e:
				# Error with creating command
				self.respond({'code': 22, 'error': "Error with creating command: [" + str(e) + "]"}, error=True)
				return

			# Preform the command
			command.preform()

		except Exception as e:
			# Error while running command
			self.respond({'code': 17, 'error': "Error preforming command: [" + str(e) + "]"}, error=True)
			return

		# Get the output data and respond with it
		self.respond(command.data, error=(not command.data['code'] == 0))

	def clear_user_sessions(self):

		"""Accept a clear user sessions command."""

		LOGGER.info("CLEAR USER SESSIONS REQUEST FROM " + str(self.addr))

		# Check that the data has a username and password
		if not ('username' in self.data and 'password' in self.data):
			# No username and password
			self.respond({'code': 12, 'error': "Clear user sessions command must have username and password provided."}, error=True)

		# Get the username and password hash
		username, password_hash = self.data['username'], hash_password(self.data['password'])

		# Check the users data in the server
		if not username in self.server.users:
			# User doesn't exist
			self.respond({'code': 13, 'error': "User doesn't exist."}, error=True)

		# Check that the password hashes match
		if not self.server.users[username]['password_hash'] == password_hash:
			# Invalid password
			self.respond({'code': 14, 'error': "Invalid password."}, error=True)

		# Successfully authenticated, so clear the sessions

		# Loop over each session
		for session_id, session in list(self.server.sessions.items()):
			# Check if the session is for the user
			if session.username == self.data['username']:
				# Delete the session
				del self.server.sessions[session_id]

		# Respond
		self.respond({'code': 0})

	def __repr__(self):

		"""Return a string representation of the object."""

		return "<Connection " + str(self.addr) + ">"

	def __str__(self):

		 """Return a string representation of the object."""

		 return self.__repr__()
