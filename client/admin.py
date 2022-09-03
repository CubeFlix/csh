"""

- CSH Client 'admin.py' Source Code -

(C) Cubeflix 2021 (CSH)

"""


# ---------- IMPORTS ----------

from .misc import *
from .binary import *


# ---------- CLASSES ----------

class AdminClient:

	"""The admin CSH client class."""

	def __init__(self, address, username, secure=False, ssl_version=ssl.PROTOCOL_TLSv1_2, ca_certs=None):

		"""Create the admin CSH client.
		   Args: address -> The address for the server, as a tuple.
		   		 username -> The username for the admin client.
		         secure -> If the server is secure. Defaults to False.
		         ssl_version -> The SSL version object for the client if it is secure.
		         ca_certs -> Certificate file for SSL verification."""

		self.address = address
		self.username = username
		self.secure = secure
		self.ssl_version = ssl_version
		self.ca_certs = ca_certs

	def request(self, data, keepalive=False):

		"""Send request data to the CSH server.
		   Args: data -> The data to send to the server.
		         keepalive -> If the connection socket should be kept alive after finishing the request."""

		# Convert the data to binary
		try:
			binary = serialize(data)

		except SerializingException as e:
			# Error with serializing the data
			raise CSHClientError("Serialization error. Data might be too big. Consider sending it in packets. [" + str(e) + "]")

		# Create the payload
		payload = b'CSH'

		# Add the length of the data
		payload += int.to_bytes(len(binary), 8, byteorder="little")

		# Add the binary data
		payload += binary
		
		# Create the request socket object
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			
		# If secure, wrap the socket with SSL
		if self.secure:
			client_socket = ssl.wrap_socket(client_socket,
	       	    ssl_version=self.ssl_version,
	       	    ca_certs=self.ca_certs)
		
		# Connect the socket
		client_socket.connect(self.address)
		
		# Send the payload
		for chunk_start in range(0, len(payload), 1048576):
			# Send each chunk
			client_socket.send(payload[chunk_start : chunk_start + 1048576])
		
		# Receive the data
		
		# Get the 'CSH' header
		try:
			header_bytes = client_socket.recv(3)
		except ConnectionResetError as e:
			# Connection reset
			raise CSHClientError("Connection reset. Check that the server is accessible and that you are using the right SSL version.")

		if not header_bytes == b'CSH':
			raise CSHClientError("Invalid response data from CSH server.")
		
		# Get the length of the data
		data_length = int.from_bytes(client_socket.recv(8), byteorder='little')
		
		# Get the rest of the data
		binary_data = bytearray()

		# Get each chunk
		while len(binary_data) < data_length:
			binary_data += client_socket.recv(1048576)
		
		# Parse and convert the binary data
		data = deserialize(binary_data)
		
		# End the socket
		if not keepalive:
			client_socket.close()
		
		# Return the data
		return data

	def command(self, command_id, password, args={}):

		"""Preform an admin command on the server that requires an admin account..
		   Args: command_id -> The command ID.
		   		 password -> The password to authenticate with.
		         args -> Arguments for the command. Defaults to an empty dictionary."""

		return self.request({'command': 'A', 'admin_command': command_id, 'username': self.username, 'password': password, 'args': args})

	def status(self):

		"""Send a status request/ping to the server."""

		# Make the status request
		response = self.request({'command': 'I'})

		if response['code'] != 0:
			raise CSHClientError("Error with getting status: [code " + str(response['code']) + ' - ' + response['error'] + ']')

		return StatusResponse(response)

	def shutdown(self, password):

		"""Shut down the CSH server.
		   Args: password -> The password for the command."""

		# Make the shutdown request
		response = self.command(0, password)

		if response['code'] != 0:
			raise CSHClientError("Error with shutting down server: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def create_user(self, password, username, new_password, permissions):

		"""Create a new user in the CSH server.
		   Args: password -> The password for the command.
		         username -> The username for the new user.
		         new_password -> The password for the new user.
		         permissions -> The permissions for the new user. Can be 'r', 'w', or 'a', for read, write, and admin privileges, respectively."""

		# Make the create user request
		response = self.command(1, password, {'username': username, 'password': new_password, 'permissions': permissions})

		if response['code'] != 0:
			raise CSHClientError("Error with creating new user: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def get_user(self, password, username):

		"""Get information on a user in the CSH server.
		   Args: password -> The password for the command.
		         username -> The username for the user to get information on."""

		# Make the get user data request
		response = self.command(2, password, {'username': username})

		if response['code'] != 0:
			raise CSHClientError("Error with getting user data: [code " + str(response['code']) + ' - ' + response['error'] + ']')

		return UserInfoResponse(response)

	def update_user(self, password, username, to_modify):

		"""Update user information on a user in the CSH server.
		   Args: password -> The password for the command.
		         username -> The username for the user to update.
		         to_modify -> A dictionary containing the fields to modify."""

		# Make the update user request
		response = self.command(3, password, {'username': username, 'to_modify': to_modify})

		if response['code'] != 0:
			raise CSHClientError("Error with updating user: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def delete_user(self, password, username):

		"""Delete a user in the CSH server.
		   Args: password -> The password for the command.
		         username -> The username for the user to delete."""

		# Make the delete user request
		response = self.command(4, password, {'username': username})

		if response['code'] != 0:
			raise CSHClientError("Error with deleting user: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def clear_sessions(self, password):

		"""Clear all sessions on the CSH server.
		   Args: password -> The password for the command."""

		# Make the clear sessions request
		response = self.command(5, password)

		if response['code'] != 0:
			raise CSHClientError("Error with clearing sessions: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def update_rate_limit(self, password, new_limit):

		"""Update the rate limit on the CSH server.
		   Args: password -> The password for the command.
		         new_limit -> If the CSH server should limit request rates, this should be a list of tuples, each of which contains a rate limit; the duration (seconds) and the number of requests for the duration. i.e. [(3600, 100), ...] If 
		         	we shouldn't limit rates, this should be set to None."""

		# Make the update rate limit request
		response = self.command(6, password, {'new_limit': new_limit})

		if response['code'] != 0:
			raise CSHClientError("Error with updating rate limit: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def update_server_name(self, password, name):

		"""Update the server name on the CSH server.
		   Args: password -> The password for the command.
		         name -> The new name for the server."""

		# Make the update server name request
		response = self.command(7, password, {'name': name})

		if response['code'] != 0:
			raise CSHClientError("Error with updating server name: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def update_session_expiration(self, password, default_expire, allow_change_expire):

		"""Update session expiration settings on the CSH server.
		   Args: password -> The password for the command.
		         default_expire -> If sessions should expire, this should be an integer containing the default number of seconds we should expire after without new commands. Defaults to None, meaning no expiration.
		         allow_change_expire -> If the server should allow users to change the session expiration time."""

		# Make the update session expiration settings request
		response = self.command(8, password, {'default_expire': default_expire, 'allow_change_expire': allow_change_expire})

		if response['code'] != 0:
			raise CSHClientError("Error with updating session expiration settings: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def format(self, password):

		"""Format the CSH server.
		   Args: password -> The password for the command."""

		# Make the format request
		response = self.command(9, password)

		if response['code'] != 0:
			raise CSHClientError("Error with formatting server: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def backup(self, password, path, replace=False):

		"""Backup the CSH server.
		   Args: password -> The password for the command.
		         path -> The path to place the backup file in.
		         replace -> Whether to replace an existing backup file. Defaults to False."""

		# Make the backup request
		response = self.command(10, password, {'path': path, 'replace': replace})

		if response['code'] != 0:
			raise CSHClientError("Error with backing up server: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def get_server_path(self, password):

		"""Get the CSH server path.
		   Args: password -> The password for the command."""

		# Make the get server path request
		response = self.command(11, password)

		if response['code'] != 0:
			raise CSHClientError("Error with getting server path: [code " + str(response['code']) + ' - ' + response['error'] + ']')

		return response['data']

	def run_shell(self, password, command):

		"""Run a shell command on the CSH server.
		   Args: password -> The password for the command.
		         command -> The shell command to run on the server."""

		# Make the run shell command request
		response = self.command(12, password, {'command': command})

		if response['code'] != 0:
			raise CSHClientError("Error with running command on the server: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def all_users(self, password):

		"""Get the list of all users on the CSH server.
		   Args: password -> The password for the command."""

		# Make the all users request
		response = self.command(13, password)

		if response['code'] != 0:
			raise CSHClientError("Error with getting all users: [code " + str(response['code']) + ' - ' + response['error'] + ']')

		return response['data']

	def update_session_limit(self, password, session_limit):

		"""Update the maximum session limit for the CSH server.
		   Args: password -> The password for the command.
		         session_limit -> The new session limit for the server."""

		# Make the update session limit request
		response = self.command(14, password, {'session_limit': session_limit})

		if response['code'] != 0:
			raise CSHClientError("Error with updating maximum session limit: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def get_all_settings(self, password):

		"""Get all the settings for the CSH server.
		   Args: password -> The password for the command."""

		# Make the get all settings request
		response = self.command(15, password)

		if response['code'] != 0:
			raise CSHClientError("Error with getting all settings: [code " + str(response['code']) + ' - ' + response['error'] + ']')

		return response['data']

