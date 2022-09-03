"""

- CSH Server 'server.py' Source Code -

(C) Cubeflix 2021 (CSH)

"""


# ---------- IMPORTS ----------

from .misc import *
from .connection import *
from .commands import *
from .auth import *
from .admin import *


# ---------- CLASSES ----------

class CSHServer:

	"""The main asynchronous CSH server processing class."""

	# Logger
	LOGGER = LOGGER

	# Command objects
	COMMANDS = [LogOutCommand, ReadCommand, WriteCommand, DeleteCommand, RenameCommand, 
		CreateDirectoryCommand, DeleteDirectoryCommand, ListDirectoryCommand, 
		MoveCommand, CopyCommand, ChangeDirectoryCommand, CurrentDirectoryCommand, 
		SizeCommand, ExistsCommand]

	# List of acceptable command IDs
	ACCEPTABLE_COMMAND_IDS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

	# Admin command objects
	ADMIN_COMMANDS = [ShutDownCommand, CreateUserCommand, GetUserCommand, UpdateUserCommand, 
		DeleteUserCommand, ClearSessionsCommand, UpdateRateLimitCommand, UpdateServerNameCommand,
		UpdateSessionExpirationCommand, FormatCommand, BackupCommand, GetServerPathCommand, 
		RunShellCommand, AllUsersCommand, UpdateMaxSessionsCommand, GetAllSettings]

	# List of acceptable command IDs
	ACCEPTABLE_ADMIN_COMMAND_IDS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

	def __init__(self, path, address, users_file, server_name, backlog=5, secure=False, rate_limit=None, session_limit=None, default_expire=None, allow_change_expire=True, session_expiration_delay=100, runtime=None):

		"""Create the CSH server object.
		   Args: path -> The path to run the CSH server on.
		         address -> The address to host the server on, as a tuple.
		         users_file -> A file path containing a JSON representation of all usernames and password hashes. If starting for the first time, CSH will create a users file at the path given.
		         server_name -> A string containing the server's name.
		         backlog -> The number of unaccepted connections the server should allow before refusing new connections. Defaults to 5.
		         secure -> If the CSH server should be secure, this should be a tuple containing the certificate path, key file path, and SSL protocol type. If not secure, it defaults to false.
		         rate_limit -> If the CSH server should limit request rates, this should be a list of tuples, each of which contains a rate limit; the duration (seconds) and the number of requests for the duration. i.e. [(3600, 100), ...] If 
		         	we shouldn't limit rates, this defaults to None.
		         session_limit -> If the CSH server should limit the number of sessions per user, it should be the number of sessions a user can have. Defaults to None, meaning no limit.
		         default_expire -> If sessions should expire, this should be an integer containing the default number of seconds we should expire after without new commands. Defaults to None, meaning no expiration.
		         allow_change_expire -> If the server should allow users to change the session expiration time.
		         session_expiration_delay -> The number of seconds to delay between each check for expired sessions. Defaults to 100.
		         runtime -> The optional runtime for the CSH server. Defaults to None."""

		self.path = path
		self.address = address
		self.users_file = users_file
		self.server_name = server_name
		self.backlog = backlog
		self.secure = secure
		self.rate_limit = rate_limit
		self.session_limit = session_limit
		self.default_expire = default_expire
		self.allow_change_expire = allow_change_expire
		self.session_expiration_delay = session_expiration_delay
		self.runtime = runtime

		# Load the users
		try:
			file_handle = open(self.users_file, 'r')
			user_data = file_handle.read()
			file_handle.close()

			if user_data == '':
				# Empty user data file
				self.init_users()
			else:
				# Load users
				self.users = json.loads(user_data)

			self.LOGGER.info("LOADED USERS FILE")

		except Exception as e:
			# Error while reading file

			# Try to create the file
			try:
				self.init_users()

			except Exception as e:
				# Error with creating users, so path is not accessible
				self.LOGGER.critical("ERROR LOADING/CREATING USERS FILE: [" + str(e) + "]")

				raise CSHError("ERROR LOADING/CREATING USERS FILE: [" + str(e) + "]")

		# Set up the rate limiter
		if self.rate_limit:
			# Get each limit object
			limits = []

			for limit in self.rate_limit:
				limits.append(pyrate_limiter.RequestRate(limit[1], limit[0]))

			# Create the limiter
			self.rate_limiter = pyrate_limiter.Limiter(*limits)

			self.LOGGER.info("SET UP RATE LIMITER")

		# Check for access permissions
		access = self.check_access()

		if not access:
			# Error with accessing file system, so path is not accessible
			self.LOGGER.critical("ERROR ACCESSING FILE SYSTEM: INVALID PERMISSIONS")

			raise CSHError("ERROR ACCESSING FILE SYSTEM: INVALID PERMISSIONS")

		self.LOGGER.info("SYSTEM ACCESS CHECK: VALID")

		# Variable to store if the server is currently running
		self.running = False

		# Sessions
		self.sessions = {}

		# Create the socket
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Allow immediate reuse of port
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# If secure, wrap the server socket
		if secure:
			# wrap the server socket with SSL security
			self.server_socket = ssl.wrap_socket(self.server_socket,
                server_side=True,
                certfile=self.secure[0],
                keyfile=self.secure[1],
                ssl_version=self.secure[2])

		# Bind the socket
		self.server_socket.bind(self.address)

		self.LOGGER.info("SET UP SERVER SOCKET")

		# Create the session generation queue
		self.session_gen_queue = queue.Queue()

		# Create the updated_settings set, to store the updated server settings
		self.updated_settings = set()

	def check_access(self):

		"""Check that CSH can access the file system."""

		# Check for read, write, create, and execute access in the file system path
		if not (os.access(os.path.abspath(self.path), os.R_OK) and os.access(os.path.abspath(self.path), os.W_OK) and \
			 os.access(os.path.abspath(self.path), os.X_OK) and os.access(os.path.abspath(self.path), os.X_OK | os.W_OK)):
			return False

		return True

	def run_server(self):

		"""Run the server's main process loop. Manage all connections asynchronously and use the connection object to manage handle them."""

		self.LOGGER.info('RUNNING SERVER AT ' + str(self.address))

		# Server is running
		self.running = True

		# Listen on the socket
		self.server_socket.listen(self.backlog)

		# Begin server main loop and continue until stopped with stop_server
		while self.running:
			# Use error catching so that the server will not stop if an error occurs
			try:
				# Await and then accept a connection
				connection_socket, addr = self.server_socket.accept()

				self.LOGGER.info('CONNECTION FROM ' + addr[0] + ' PORT ' + str(addr[1]))

				# Let the processor handle the request as a process
				process = threading.Thread(target=self.handle_connection, args=(connection_socket, addr))
				process.start()

			except Exception as exception:
				# Error has occurred
				self.LOGGER.error(str(exception))

		# Server has stopped
		self.LOGGER.info('SERVER HAS STOPPED')

	def handle_connection(self, connection_socket, addr):

		"""Handle a CSH connection.
		   Args: connection_socket -> The connection socket object.
		         addr -> The address of the connection."""

		# Create and run the connection handler
		connection = Connection(connection_socket, addr, self)
		connection.handle()

	def run_session_gen_worker(self):

		"""Run the session generation worker. This exists so that only one session will be generated at a time."""

		self.LOGGER.info('RUNNING SESSION GENERATION WORKER')

		while self.running:
			try:
				# Handle all session generation requests
				req = self.session_gen_queue.get()

				# Generate a session ID
				session_id = self.generate_session_id()

				# Finish the request with the session ID
				req.finish(session_id)
			
			except Exception as e:
				# Error with session generation
				self.LOGGER.error('SESSION GENERATION ERROR: [' + str(e) + ']')

		# Worker has stopped
		self.LOGGER.info('SESSION GENERATION WORKER HAS STOPPED')

	def run_session_expiration_worker(self):

		"""Run the session expiration worker. Loops over each session and removes expired ones."""

		self.LOGGER.info('RUNNING SESSION EXPIRATION WORKER')

		while self.running:
			try:
				# Loop over all sessions
				for session_id, session in list(self.sessions.items()):
					# Validate the expiration on the session object
					if session.expires:
						if datetime.datetime.now() > session.expires:
							# Expired, so not a valid session
							
							# Remove this session
							del self.sessions[session_id]
				
				# Delay
				time.sleep(self.session_expiration_delay)
			
			except Exception as e:
				# Error with session expiration
				self.LOGGER.error('SESSION EXPIRATION ERROR: [' + str(e) + ']')

		# Worker has stopped
		self.LOGGER.info('SESSION GENERATION WORKER HAS STOPPED')

	def start_server(self):

		"""Start the server's main process loop."""

		threading.Thread(target=self.run_server).start()
		threading.Thread(target=self.run_session_gen_worker).start()
		threading.Thread(target=self.run_session_expiration_worker).start()

		# Catch keyboard interrupts (Ctrl-C)
		try:
			while True:
				pass

		except KeyboardInterrupt:
			# Shut down the server
			self.stop_server()

			# Close the server socket
			self.server_socket.close()

			# Call runtime finish
			if self.runtime:
				self.runtime.finish()

			# Kill the process
			os.kill(os.getpid(), signal.SIGTERM)

	def stop_server(self):

		"""Stop the server's main process loop."""

		self.LOGGER.info('STOPPING SERVER')

		# Server is stopped
		self.running = False

	def generate_session_id(self):

		"""Generate a valid session ID."""

		# Continue to generate IDs until we get one that isn't taken
		session_id = generate_session_id()

		while session_id in self.sessions.keys():
			session_id = generate_session_id()

		# We now have a unused ID, so return it
		return session_id

	def update_users(self):

		"""Update the users file to reflect the current data."""

		file_handle = open(self.users_file, 'w')
		file_handle.write(json.dumps(self.users))
		file_handle.close()

	def init_users(self):

		"""Initialize the users file."""

		self.users = {}

		# Update users
		self.update_users()

	def create_user(self, username, password, permissions):

		"""Create a user in the users file.
		   Args: username -> The username for the new user.
		         password -> The password string for the user.
		         permissions -> A string containing the permissions for the new user. 'r' is for reading permissions, 'w' is for reading and writing permissions, and 'a' is for full admin permissions."""

		self.users[username] = {'username': username, 'password_hash': hash_password(password), 'permissions': permissions}

		# Update users
		self.update_users()

	def delete_user(self, username):

		"""Delete a user in the users file.
		   Args: username -> The username of the user."""

		del self.users[username]

		# Update users
		self.update_users()

	def update_user(self, username, to_modify):

		"""Update a user in the users file.
		   Args: username -> The username for the user.
		         to_modify -> A dictionary containing the fields to modify."""

		if "password" in to_modify:
			# Password is included
			to_modify["password"] = hash_password(to_modify["password"])

		self.users[username].update(to_modify)

		# Update users
		self.update_users()

	def __repr__(self):

		"""Return a string representation of the object."""

		return "<Server " + self.server_name + ">"

	def __str__(self):

		 """Return a string representation of the object."""

		 return self.__repr__()
