"""

- CSH Server 'runtime.py' Source Code -

(C) Cubeflix 2021 (CSH)

"""


# ---------- IMPORTS ----------

from .misc import *
from .server import *


# ---------- FUNCTIONS ----------

# TODO: I present a stupid, hacky method of getting the local IP address copied from
# https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def get_local_ip():

	"""Get the current local IP address for the host."""

	# Create a socket to connect with
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.settimeout(0)

	# Try to connect to ourselves
	try:
		s.connect(('10.255.255.255', 1))
		ip = s.getsockname()[0]

	except Exception:
		# Error with connecting, use default
		ip = '127.0.0.1'

	finally:
		# Close the socket
		s.close()

	# Return the IP
	return ip


# ---------- CLASSES ----------

class ServerRuntime:

	"""The main CSH server runtime class."""

	# Logger
	LOGGER = LOGGER

	def __init__(self, settings, args):

		"""Create the CSH server runtime.
		   Args: settings -> Either a filename pointing to a valid CSH settings file, or a dictionary containing settings for the CSH server.
		         args -> The command line arguments, to be joined with the settings."""

		if isinstance(settings, str):
			# Settings is a path
			self.original_file = settings
			self.settings = self.parse_settings_file(settings)

		else:
			self.settings = settings

		# Join the arguments and the settings
		self.settings = {**self.settings, **args}

		# Convert the two address fields into one
		# By default, it will host on localhost, port 8008
		if 'port' in self.settings and 'host' in self.settings:
			# Both are included, so combine them
			self.settings['address'] = (self.settings['host'], self.settings['port'])

			# Remove host and port
			del self.settings['host'], self.settings['port']

		else:
			# Check if port is not set
			if not 'port' in self.settings:
				self.settings['port'] = 8008

			# Check if host is not set
			if not 'host' in self.settings:
				self.settings['host'] = 'localhost'

			# Convert the two address fields into one
			self.settings['address'] = (self.settings['host'], self.settings['port'])

			# Remove host and port
			del self.settings['host'], self.settings['port']

		# Check for the path argument
		# By default, it will use the current working directory
		if not 'path' in self.settings:
			self.settings['path'] = os.getcwd()

		# Take out the update_settings setting
		if 'update_settings' in self.settings:
			# Take it out and save it as it's own variable
			self.update_settings = self.settings['update_settings']
			del self.settings['update_settings']

		else:
			# Else, set it to false
			self.update_settings = False

		# Check for the users_file argument
		# By default, it will use 'users.json'
		if not 'users_file' in self.settings:
			self.settings['users_file'] = 'users.json'

		# Check for the server_name argument
		# By default, it will use 'server'
		if not 'server_name' in self.settings:
			self.settings['server_name'] = '%HOSTNAME%'

		# Take out the update_settings setting
		if 'update_settings' in self.settings:
			# Take it out and save it as it's own variable
			self.update_settings = self.settings['update_settings']
			del self.settings['update_settings']

		else:
			# Else, set it to false
			self.update_settings = False

		# Take out the verbose setting
		if 'verbose' in self.settings:
			# Take it out and set verbosity
			set_verbose(self.settings['verbose'])
			del self.settings['verbose']

		# Take out the file_handler setting
		if 'file_handler' in self.settings:
			# Take it out and set the file handler
			set_file_handler(self.settings['file_handler'])
			del self.settings['file_handler']

		# Take out the level setting
		if 'level' in self.settings:
			# Take it out and set the level
			LOGGER.setLevel(getattr(logging, self.settings['level'].upper()))
			del self.settings['level']

		# Handle variable %HOSTNAME% in server name
		if 'server_name' in self.settings and self.settings['server_name'].upper() == '%HOSTNAME%':
			# Update it to the system's hostname
			self.settings['server_name'] = socket.gethostname()

		# Handle variable %IP% in host name
		if self.settings['address'][0].upper() == '%IP%':
			# Update it to the system's internal IP address
			self.settings['address'] = (get_local_ip(), self.settings['address'][1])

	@staticmethod
	def parse_settings_file(settings):

		"""Parse a settings file.
		   Args: settings -> The settings file path."""

		# Load the settings file data
		file_handle = open(settings, 'r')
		settings_parsed = json.load(file_handle)
		file_handle.close()

		# If 'secure' is included, parse it
		if 'secure' in settings_parsed and settings_parsed['secure']:
			# Turn the SSL version protocol string into an object
			ssl_protocol = getattr(ssl, settings_parsed['secure'][2])

			settings_parsed['secure'][2] = ssl_protocol

			# Turn it into a tuple
			settings_parsed['secure'] = tuple(settings_parsed['secure'])

		# Return the parsed settings
		return settings_parsed

	def create_server(self):

		"""Create the CSH server object based on the settings."""

		self.server = CSHServer(**self.settings, runtime=self)

	def start_server(self):

		"""Run the CSH server."""

		if hasattr(self, 'server'):
			self.server.start_server()

		else:
			# Server has not been created
			raise CSHError("Server has not been created with create_server.")

	def stop_server(self):

		"""Stop the CSH server."""

		if hasattr(self, 'server'):
			self.server.stop_server()

		else:
			# Server has not been created
			raise CSHError("Server has not been created with create_server.")

	def finish(self):

		"""Run the finish function from the server."""

		try:
			if not hasattr(self, 'server'):
				raise CSHError("Server has not been created with create_server.")

			# Check for changes in the server settings, and save them
				
			# Get the updated settings
			updated_settings = self.server.updated_settings

			# Check that there is a configuration file
			if hasattr(self, 'original_file'):
				# Save them in the original JSON file

				# Read the original file
				file_handle = open(self.original_file, 'r')
				settings_parsed = json.load(file_handle)
				file_handle.close()

				# Update the settings
				for setting in updated_settings:
					# Update it in the settings
					settings_parsed[setting] = getattr(self.server, setting)

				# Write the settings back
				file_handle = open(self.original_file, 'w')
				json.dump(settings_parsed, file_handle)
				file_handle.close()

		except Exception as e:
			# Error with finishing
			LOGGER.critical("ERROR WITH FINISHING ON RUNTIME: [" + str(e) + "]")

	def __repr__(self):

		"""Return a string representation of the object."""

		return "<ServerRuntime>"

	def __str__(self):

		 """Return a string representation of the object."""

		 return self.__repr__()
