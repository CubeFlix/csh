"""

- CSH Server 'admin.py' Source Code -

(C) Cubeflix 2021 (CSH)

"""


# ---------- IMPORTS ----------

from .misc import *


# ---------- CLASSES ----------

class BaseAdminCommand:

	"""The base administrator command class."""

	def finish(self, data):

		"""Mark the command as finished, and return any data if necessary.
		   Args: data -> Any data to return. Generally should be in the following form: {'code': command exit code, ...}."""

		self.finished = True
		self.data = data

	def __repr__(self):

		"""Return a string representation of the object."""

		return "<AdminCommand " + self.__class__.__name__ + ">"

	def __str__(self):

		 """Return a string representation of the object."""

		 return self.__repr__()

	...


# --- Individual Commands ---

class ShutDownCommand(BaseAdminCommand):

	"""The main server shut down command object."""

	def __init__(self, server):

		"""Shut down the server.
		   Args: server -> The server for the command."""
		
		self.server = server

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the shut down command."""

		try:
			# Shut down the server
			self.server.stop_server()

			# Close the server socket
			self.server.server_socket.close()

			# Call runtime finish
			if self.server.runtime:
				self.server.runtime.finish()

			# Kill the process
			os.kill(os.getpid(), signal.SIGTERM)
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class CreateUserCommand(BaseAdminCommand):

	"""The main create user command object."""

	def __init__(self, server, username, password, permissions):

		"""Create a user.
		   Args: server -> The server for the command.
		         username -> The username for the new user.
		         password -> The password for the new user.
		         permissions -> The permissions for the new user."""
		
		self.server = server
		self.username = username
		self.password = password
		self.permissions = permissions

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the create user command."""

		try:
			self.server.create_user(self.username, self.password, self.permissions)
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class GetUserCommand(BaseAdminCommand):

	"""The main get user data command object."""

	def __init__(self, server, username):

		"""Get user data from the server.
		   Args: server -> The server for the command.
		         username -> The username for the user."""
		
		self.server = server
		self.username = username

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the get user data command."""

		try:
			password_hash = self.server.users[self.username]["password_hash"]
			permissions = self.server.users[self.username]["permissions"]
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0, 'password_hash': password_hash, 'permissions': permissions})


class UpdateUserCommand(BaseAdminCommand):

	"""The main update user command object."""

	def __init__(self, server, username, to_modify):

		"""Update a user.
		   Args: server -> The server for the command.
		   	     username -> The username for the user.
		         to_modify -> A dictionary containing the fields to modify."""
		
		self.server = server
		self.username = username
		self.to_modify = to_modify

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the update user command."""

		try:
			self.server.update_user(self.username, self.to_modify)
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class DeleteUserCommand(BaseAdminCommand):

	"""The main delete user command object."""

	def __init__(self, server, username):

		"""Delete a user.
		   Args: server -> The server for the command.
		   	     username -> The username for the user."""

		self.server = server
		self.username = username

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the delete user command."""

		try:
			self.server.delete_user(self.username)
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class ClearSessionsCommand(BaseAdminCommand):

	"""The main clear user sessions command object."""

	def __init__(self, server):

		"""Clear all sessions.
		   Args: server -> The server for the command."""

		self.server = server

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the clear sessions command."""

		try:
			self.server.sessions = {}
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class UpdateRateLimitCommand(BaseAdminCommand):

	"""The main update rate limit command object."""

	def __init__(self, server, new_limit):

		"""Update the rate limit. NOTE: Resets all current session rate limits.
		   Args: server -> The server for the command.
		         new_limit -> If the CSH server should limit request rates, this should be a list of tuples, each of which contains a rate limit; the duration (seconds) and the number of requests for the duration. i.e. [(3600, 100), ...] If 
		         	we shouldn't limit rates, this should be set to None."""

		self.server = server
		self.new_limit = new_limit

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the update rate limit command."""

		try:
			# Set the rate limiter
			self.server.rate_limit = self.new_limit

			# If we need to, set up the rate limiter
			if self.server.rate_limit:
				# Get each limit object
				limits = []

				for limit in self.server.rate_limit:
					limits.append(pyrate_limiter.RequestRate(limit[1], limit[0]))

				# Create the limiter
				self.server.rate_limiter = pyrate_limiter.Limiter(*limits)

			# Add it to the set of updated settings
			self.server.updated_settings.add('rate_limit')
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class UpdateServerNameCommand(BaseAdminCommand):

	"""The main update server name command object."""

	def __init__(self, server, name):

		"""Update the server name.
		   Args: server -> The server for the command.
		         name -> The name to change it to."""

		self.server = server
		self.name = name

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the update server name command."""

		try:
			self.server.server_name = self.name

			# Add it to the set of updated settings
			self.server.updated_settings.add('server_name')
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class UpdateSessionExpirationCommand(BaseAdminCommand):

	"""The main update session expiration settings command object."""

	def __init__(self, server, default_expire, allow_change_expire):

		"""Update the session expiration settings.
		   Args: server -> The server for the command.
		         default_expire -> If sessions should expire, this should be an integer containing the default number of seconds we should expire after without new commands. Defaults to None, meaning no expiration.
		         allow_change_expire -> If the server should allow users to change the session expiration time."""

		self.server = server
		self.default_expire = default_expire
		self.allow_change_expire = allow_change_expire

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the update session expiration settings command."""

		try:
			self.server.default_expire = self.default_expire
			self.server.allow_change_expire = self.allow_change_expire

			# Add it to the set of updated settings
			self.server.updated_settings.add('default_expire')

			# Add it to the set of updated settings
			self.server.updated_settings.add('allow_change_expire')
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class FormatCommand(BaseAdminCommand):

	"""The main format filesystem command object."""

	def __init__(self, server):

		"""Format the entire filesystem.
		   Args: server -> The server for the command."""

		self.server = server

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the format command."""

		try:
			# Format the filesystem
			shutil.rmtree(self.server.path)

			# Recreate the path
			os.mkdir(self.server.path)
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class BackupCommand(BaseAdminCommand):

	"""The main backup filesystem command object."""

	def __init__(self, server, path, replace=False):

		"""Backup the filesystem.
		   Args: server -> The server for the command.
		         path -> The path to place the backup file in.
		         replace -> Whether to replace an existing backup file. Defaults to False."""

		self.server = server
		self.path = path
		self.replace = replace

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the backup command."""

		try:
			# Get a name for the backup
			name = 'BACKUP-' + time.strftime("%Y%m%d-%H%M%S")

			# Check if another file with the same name already exists
			if os.path.exists(os.path.join(self.path, name + '.bak.zip')):
				# Already exists, so check if we should replace
				if replace:
					# Replace it
					pass

				else:
					# Exit with error
					self.finish({'code': 23, 'error': 'Backup already exists.'})
					return

			# Make the backup
			shutil.make_archive(os.path.join(self.path, name + '.bak'), 'zip', self.server.path)
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class GetServerPathCommand(BaseAdminCommand):

	"""The main get server path command object."""

	def __init__(self, server):

		"""Get the server path.
		   Args: server -> The server for the command."""

		self.server = server

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the get server path command."""

		try:
			data = self.server.path
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0, 'data': data})


class RunShellCommand(BaseAdminCommand):

	"""The main run shell command object."""

	def __init__(self, server, command):

		"""Run a shell command.
		   Args: server -> The server for the command.
		         command -> The command to run."""

		self.server = server
		self.command = command

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the run shell command."""

		try:
			os.system(self.command)
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class AllUsersCommand(BaseAdminCommand):

	"""The main get all usernames command object."""

	def __init__(self, server):

		"""Get all usernames.
		   Args: server -> The server for the command."""

		self.server = server

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the get all usernames command."""

		try:
			data = list(self.server.users.keys())
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0, 'data': data})


class UpdateMaxSessionsCommand(BaseAdminCommand):

	"""The main update maximum number of sessions command object."""

	def __init__(self, server, session_limit):

		"""Update the maximum number of sessions.
		   Args: server -> The server for the command.
		         session_limit -> The maximum number of sessions for the server."""

		self.server = server
		self.session_limit = session_limit

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the update maximum number of sessions command."""

		try:
			self.server.session_limit = self.session_limit

			# Add it to the set of updated settings
			self.server.updated_settings.add('session_limit')
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class GetAllSettings(BaseAdminCommand):

	"""The main get all server settings command."""

	def __init__(self, server):

		"""Get all settings for the server.
		   Args: server -> The server for the command."""

		self.server = server

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the get all server settings command."""

		try:
			data = {'server_name': self.server.server_name, 'secure': False if not self.server.secure else self.server.secure[2].name, 'rate_limit': self.server.rate_limit, 'session_limit': self.server.session_limit, 
				'default_expire': self.server.default_expire, 'allow_change_expire': self.server.allow_change_expire, 'session_expiration_delay': self.server.session_expiration_delay}
		
		except Exception as e:
			# Error
			self.finish({'code': 17, 'error': 'Error preforming command: [' + str(e) + ']'})
			return

		# Finish and return with the data
		self.finish({'code': 0, 'data': data})

