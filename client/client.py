"""

- CSH Client 'client.py' Source Code -

(C) Cubeflix 2021 (CSH)

"""


# ---------- IMPORTS ----------

from .misc import *
from .binary import *


# ---------- CLASSES ----------

class Client:

	"""The base CSH client class."""

	def __init__(self, address, secure=False, ssl_version=ssl.PROTOCOL_TLSv1_2, ca_certs=None):

		"""Create the CSH client.
		   Args: address -> The address for the server, as a tuple.
		         secure -> If the server is secure. Defaults to False.
		         ssl_version -> The SSL version object for the client if it is secure.
		         ca_certs -> Certificate file for SSL verification."""

		self.address = address
		self.secure = secure
		self.ssl_version = ssl_version
		self.ca_certs = ca_certs

		self.logged_in = False
		self.username = None
		self.session_id = None

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

	def command(self, command_id, args={}):

		"""Preform a command on the server that requires a session.
		   Args: command_id -> The command ID.
		         args -> Arguments for the command. Defaults to an empty dictionary."""

		if not self.logged_in:
			raise CSHClientError("Not logged in.")

		return self.request({'command': command_id, 'username': self.username, 'session_id': self.session_id, 'args': args})

	def status(self):

		"""Send a status request/ping to the server."""

		# Make the status request
		response = self.request({'command': 'I'})

		if response['code'] != 0:
			raise CSHClientError("Error with getting status: [code " + str(response['code']) + ' - ' + response['error'] + ']')

		return StatusResponse(response)

	def login(self, username, password, expiration_time=63072000):

		"""Log in to the server.
		   Args: username -> The username to log in with.
		         password -> The password to log in with.
		         expiration_time -> The expiration time for the session, in seconds. Defaults to 63072000, or two years."""

		# Check if the client is already logged in
		if self.logged_in:
			raise CSHClientError("Client is already logged in.")

		# Make the login request
		response = self.request({'command': 'L', 'username': username, 'password': password, 'expiration_time': expiration_time})

		if response['code'] != 0:
			raise CSHClientError("Authentication error: [code " + str(response['code']) + ' - ' + response['error'] + ']')

		# Load authentication information
		self.logged_in = True
		self.username = username
		self.session_id = response['session_id']

	def clear_user_sessions(self, username, password):

		"""Clear all sessions for the user.
		   Args: username -> The username for the command.
		         password -> The password for the command."""

		# Make the clear user sessions request
		response = self.request({'command': 'CS', 'username': username, 'password': password})

		if response['code'] != 0:
			raise CSHClientError("Error with clearing user sessions: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def logout(self):

		"""Log out of the server."""

		# Make the log out request
		response = self.command(0)

		if response['code'] != 0:
			# Manually log out
			self.logged_in = False
			self.session_id = None
			self.username = None

	# --- Individual CSH Commands ---

	def read(self, path, start=0, length=-1):

		"""Read a file from the CSH filesystem.
		   Args: path -> The path to read.
		         start -> The starting point to read from.
		         length -> The length of the data to read."""

		# Make the read request
		response = self.command(1, {'path': path, 'start': start, 'length': length})

		if response['code'] != 0:
			raise CSHClientError("Error with reading file: [code " + str(response['code']) + ' - ' + response['error'] + ']')

		return response['data']

	def write(self, path, data, mode='wb'):

		"""Write to a file from the CSH filesystem.
		   Args: path -> The path to write to.
		         data -> The data to write to the file as a bytes-like object.
		         mode -> The mode to open the file in. Defaults to 'wb', but can also be 'ab'."""

		if not type(data) in (bytes, bytearray):
			raise CSHClientError("Invalid data type for write data.")

		if not mode in ('wb', 'ab'):
			raise CSHClientError("Mode is invalid.")

		# Make the write request
		response = self.command(2, {'path': path, 'data': data, 'mode': mode})

		if response['code'] != 0:
			raise CSHClientError("Error with writing file: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def delete(self, path):

		"""Delete a file in the CSH filesystem.
		   Args: path -> The path to delete."""

		# Make the delete request
		response = self.command(3, {'path': path})

		if response['code'] != 0:
			raise CSHClientError("Error with deleting file: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def rename(self, path, new_name):

		"""Rename a path in the CSH filesystem.
		   Args: path -> The path to rename.
		         new_name -> The new name for the path."""

		# Make the rename request
		response = self.command(4, {'path': path, 'new_name': new_name})

		if response['code'] != 0:
			raise CSHClientError("Error with renaming path: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def create_directory(self, path):

		"""Create a directory in the CSH filesystem.
		   Args: path -> The path to create."""

		# Make the create directory request
		response = self.command(5, {'path': path})

		if response['code'] != 0:
			raise CSHClientError("Error with creating path: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def delete_directory(self, path):

		"""Delete a directory in the CSH filesystem.
		   Args: path -> The path to delete."""

		# Make the delete directory request
		response = self.command(6, {'path': path})

		if response['code'] != 0:
			raise CSHClientError("Error with deleting path: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def list_directory(self, path):

		"""List the contents of a directory in the CSH filesystem.
		   Args: path -> The path to list."""

		# Make the list directory request
		response = self.command(7, {'path': path})

		if response['code'] != 0:
			raise CSHClientError("Error with listing directory: [code " + str(response['code']) + ' - ' + response['error'] + ']')

		return response['data']

	def move(self, path, destination):

		"""Move a path in the CSH filesystem.
		   Args: path -> The path to move.
		         destination -> The destination path."""

		# Make the move path request
		response = self.command(8, {'path': path, 'destination': destination})

		if response['code'] != 0:
			raise CSHClientError("Error with moving path: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def copy(self, path, destination):

		"""Copy a path in the CSH filesystem.
		   Args: path -> The path to copy.
		         destination -> The destination path."""

		# Make the copy path request
		response = self.command(9, {'path': path, 'destination': destination})

		if response['code'] != 0:
			raise CSHClientError("Error with copying path: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def change_directory(self, path):

		"""Change the current CSH session directory.
		   Args: path -> The new path."""

		# Make the change directory request
		response = self.command(10, {'path': path})

		if response['code'] != 0:
			raise CSHClientError("Error with changing directory: [code " + str(response['code']) + ' - ' + response['error'] + ']')

	def current_directory(self):

		"""Get the current CSH session directory."""

		# Make the get current directory request
		response = self.command(11)

		if response['code'] != 0:
			raise CSHClientError("Error with getting current directory: [code " + str(response['code']) + ' - ' + response['error'] + ']')

		return response['path']

	def size(self, path):

		"""Get the size of a file in the CSH filesystem.
		   Args: path -> The file to get the size of."""

		# Make the get file size request
		response = self.command(12, {'path': path})

		if response['code'] != 0:
			raise CSHClientError("Error with getting file size: [code " + str(response['code']) + ' - ' + response['error'] + ']')

		return response['size']

	def exists(self, path):

		"""Check if a path exists in the CSH filesystem, and if it does, if it is a file or a folder.
		   Args: path -> The path to check."""

		# Make the path exists request
		response = self.command(13, {'path': path})

		if response['code'] != 0:
			raise CSHClientError("Error with checking path existence: [code " + str(response['code']) + ' - ' + response['error'] + ']')

		return PathExistence(response)

	# --- Handle Context Managers ---

	def __enter__(self):

		"""Enter the context."""

		return self

	def __exit__(self, exc_type, exc_value, exc_tb):

		"""Exit the context."""

		# Log out
		if self.logged_in:
			self.logout()

	def __repr__(self):

		"""Return a string representation of the object."""

		return "<Client " + str(self.address) + ">"

	def __str__(self):

		 """Return a string representation of the object."""

		 return self.__repr__()
