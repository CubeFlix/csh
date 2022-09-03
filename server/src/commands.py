"""

- CSH Server 'commands.py' Source Code -

(C) Cubeflix 2021 (CSH)

"""


# ---------- IMPORTS ----------

from .misc import *


# ---------- CLASSES ----------

class BaseCommand:

	"""The base command class."""

	def finish(self, data):

		"""Mark the command as finished, and return any data if necessary.
		   Args: data -> Any data to return. Generally should be in the following form: {'code': command exit code, ...}."""

		self.finished = True
		self.data = data

	def __repr__(self):

		"""Return a string representation of the object."""

		return "<Command " + self.__class__.__name__ + ">"

	def __str__(self):

		 """Return a string representation of the object."""

		 return self.__repr__()

	...


# --- Individual Commands ---

class LogOutCommand(BaseCommand):

	"""The main signing out command object."""

	def __init__(self, session):

		"""Log out and remove the session.
		   Args: session -> The session of the user preforming the command."""

		self.session = session
		
		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the log out command."""

		# Validate the session
		if not self.session.validate():
			# Invalid session, so finish and return
			self.finish({'code': 1, 'error': "Session invalid or expired."})
			return

		# Remove the session
		try:
			del self.session.server.sessions[self.session.session_id]

		except Exception as e:
			# Error with logging out
			self.finish({'code': 2, 'error': "Error with logging out."})

		# Finish and return with the data
		self.finish({'code': 0})


class ReadCommand(BaseCommand):

	"""The main reading command object."""

	def __init__(self, session, path, start=0, length=-1):

		"""Read a file from the file system.
		   Args: session -> The session of the user preforming the command.
		         path -> The path to read.
		         start -> The starting point to read from. Defaults to 0.
		         length -> The length of data to read. Defaults to -1, meaning the rest of the file."""

		self.session = session
		self.path = path
		self.start = start
		self.length = length
		
		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the read command."""

		# Validate the session
		if not self.session.validate():
			# Invalid session, so finish and return
			self.finish({'code': 1, 'error': "Session invalid or expired."})
			return

		# Check that the user has permission to preform this command
		if not self.session.server.users[self.session.username]['permissions'] in ('r', 'w', 'a'):
			# User does not have permission, so finish and return
			self.finish({'code': 19, 'error': "User does not have permission to preform this command."})
			return

		# Validate the path
		if not (self.session.validate_path(self.path) and os.path.isfile(self.session.get_full_path(self.path))):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid path."})
			return

		# Preform the read operation
		try:
			# Open the file and get a file handle
			file_handle = open(self.session.get_full_path(self.path), 'rb')

			# Seek to the start location
			file_handle.seek(self.start)

			# Read the data
			data = file_handle.read(self.length)

			# Close the file handle
			file_handle.close()

		except Exception as e:
			# Error while reading file

			# Check for a file not found error
			if isinstance(e, FileNotFoundError):
				# Finish and return, with a masked error name so as to not give away the local path
				self.finish({'code': 3, 'error': "File " + json.dumps(self.path) + " not found."})
				return

			# Finish and return the error
			self.finish({'code': 4, 'error': "Error with reading file: [" + str(e) + "]"})
			return

		# Finish and return with the data
		self.finish({'code': 0, 'data': data})


class WriteCommand(BaseCommand):

	"""The main writing command object."""

	def __init__(self, session, path, data, mode='wb'):

		"""Write to a file in the file system.
		   Args: session -> The session of the user preforming the command.
		         path -> The path to write to.
		         data -> The data to write to the file as a bytes-like object.
		         mode -> The mode to open the file in. Defaults to 'wb', but can also be 'ab'."""

		self.session = session
		self.path = path
		self.write_data = data
		self.mode = mode.lower()

		self.data = None
		self.finished = False

		if not type(self.write_data) in (bytes, bytearray):
			# Invalid write data type, so finish and return
			self.finish({'code': 5, 'error': "Invalid data type for write data."})
			return

		if not self.mode in ('wb', 'ab'):
			# Invalid mode, so finish and return
			self.finish({'code': 6, 'error': "Mode is invalid."})
			return

	def preform(self):

		"""Preform the write command."""

		# Validate the session
		if not self.session.validate():
			# Invalid session, so finish and return
			self.finish({'code': 1, 'error': "Session invalid or expired."})
			return

		# Check that the user has permission to preform this command
		if not self.session.server.users[self.session.username]['permissions'] in ('w', 'a'):
			# User does not have permission, so finish and return
			self.finish({'code': 19, 'error': "User does not have permission to preform this command."})
			return

		# Validate the path
		if not self.session.validate_path(self.path):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid path."})
			return

		# Preform the write operation
		try:
			# Open the file and get a file handle
			file_handle = open(self.session.get_full_path(self.path), self.mode)

			# Write the data
			file_handle.write(self.write_data)

			# Close the file handle
			file_handle.close()

		except Exception as e:
			# Error while writing to file

			# Check for a file not found error
			if isinstance(e, FileNotFoundError):
				# Finish and return, with a masked error name so as to not give away the local path
				self.finish({'code': 3, 'error': "File " + json.dumps(self.path) + " not found or not writable."})
				return

			# Finish and return the error
			self.finish({'code': 4, 'error': "Error with writing to file: [" + str(e) + "]"})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class DeleteCommand(BaseCommand):

	"""The main file deletion command object."""

	def __init__(self, session, path):

		"""Delete a file in the file system.
		   Args: session -> The session of the user preforming the command.
		         path -> The file to delete."""

		self.session = session
		self.path = path

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the deletion command."""

		# Validate the session
		if not self.session.validate():
			# Invalid session, so finish and return
			self.finish({'code': 1, 'error': "Session invalid or expired."})
			return

		# Check that the user has permission to preform this command
		if not self.session.server.users[self.session.username]['permissions'] in ('w', 'a'):
			# User does not have permission, so finish and return
			self.finish({'code': 19, 'error': "User does not have permission to preform this command."})
			return

		# Validate the path
		if not (self.session.validate_path(self.path) and os.path.isfile(self.session.get_full_path(self.path))):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid path."})
			return

		# Preform the delete operation
		try:
			# Delete the file
			os.unlink(self.session.get_full_path(self.path))

		except Exception as e:
			# Error while deleting file

			# Check for a file not found error
			if isinstance(e, FileNotFoundError):
				# Finish and return, with a masked error name so as to not give away the local path
				self.finish({'code': 3, 'error': "File " + json.dumps(self.path) + " not found."})
				return

			# Finish and return the error
			self.finish({'code': 4, 'error': "Error with deleting file: [" + str(e) + "]"})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class RenameCommand(BaseCommand):

	"""The main path renaming command object."""

	def __init__(self, session, path, new_name):

		"""Rename a path in the file system.
		   Args: session -> The session of the user preforming the command.
		         path -> The path to rename.
		         new_name -> The new name."""

		self.session = session
		self.path = path
		self.new_name = new_name

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the renaming command."""

		# Validate the session
		if not self.session.validate():
			# Invalid session, so finish and return
			self.finish({'code': 1, 'error': "Session invalid or expired."})
			return

		# Check that the user has permission to preform this command
		if not self.session.server.users[self.session.username]['permissions'] in ('w', 'a'):
			# User does not have permission, so finish and return
			self.finish({'code': 19, 'error': "User does not have permission to preform this command."})
			return

		# Validate the path
		if not (self.session.validate_path(self.path) and os.path.exists(self.session.get_full_path(self.path))):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid path."})
			return

		# Preform the rename operation
		try:
			# Rename the path
			os.rename(self.session.get_full_path(self.path), self.new_name)

		except Exception as e:
			# Error while renaming path

			# Check for a file not found error
			if isinstance(e, FileNotFoundError):
				# Finish and return, with a masked error name so as to not give away the local path
				self.finish({'code': 3, 'error': "Path " + json.dumps(self.path) + " not found."})
				return

			# Finish and return the error
			self.finish({'code': 4, 'error': "Error with renaming path: [" + str(e) + "]"})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class CreateDirectoryCommand(BaseCommand):

	"""The main path creation command object."""

	def __init__(self, session, path):

		"""Create a path in the file system.
		   Args: session -> The session of the user preforming the command.
		         path -> The path to create."""

		self.session = session
		self.path = path

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the path creation command."""

		# Validate the session
		if not self.session.validate():
			# Invalid session, so finish and return
			self.finish({'code': 1, 'error': "Session invalid or expired."})
			return

		# Check that the user has permission to preform this command
		if not self.session.server.users[self.session.username]['permissions'] in ('w', 'a'):
			# User does not have permission, so finish and return
			self.finish({'code': 19, 'error': "User does not have permission to preform this command."})
			return

		# Validate the path
		if not self.session.validate_path(self.path):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid path."})
			return

		# Preform the create operation
		try:
			# Create the path
			os.mkdir(self.session.get_full_path(self.path))

		except Exception as e:
			# Error while renaming path

			# Check for a file not found error
			if isinstance(e, FileNotFoundError):
				# Finish and return, with a masked error name so as to not give away the local path
				self.finish({'code': 3, 'error': "Path " + json.dumps(self.path) + " cannot be created."})
				return

			# Finish and return the error
			self.finish({'code': 4, 'error': "Error with creating path: [" + str(e) + "]"})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class DeleteDirectoryCommand(BaseCommand):

	"""The main directory deletion command object."""

	def __init__(self, session, path):

		"""Delete a path in the file system.
		   Args: session -> The session of the user preforming the command.
		         path -> The path to delete."""

		self.session = session
		self.path = path

		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the deletion command."""

		# Validate the session
		if not self.session.validate():
			# Invalid session, so finish and return
			self.finish({'code': 1, 'error': "Session invalid or expired."})
			return

		# Check that the user has permission to preform this command
		if not self.session.server.users[self.session.username]['permissions'] in ('w', 'a'):
			# User does not have permission, so finish and return
			self.finish({'code': 19, 'error': "User does not have permission to preform this command."})
			return

		# Validate the path
		if not (self.session.validate_path(self.path) and os.path.isdir(self.session.get_full_path(self.path))):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid path."})
			return

		# Preform the delete operation
		try:
			# Delete the path
			shutil.rmtree(self.session.get_full_path(self.path))

		except Exception as e:
			# Error while deleting path

			# Check for a file not found error
			if isinstance(e, FileNotFoundError):
				# Finish and return, with a masked error name so as to not give away the local path
				self.finish({'code': 3, 'error': "Path " + json.dumps(self.path) + " not found."})
				return

			# Finish and return the error
			self.finish({'code': 4, 'error': "Error with deleting path: [" + str(e) + "]"})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class ListDirectoryCommand(BaseCommand):

	"""The main list directory command object."""

	def __init__(self, session, path):

		"""List a directory from the file system.
		   Args: session -> The session of the user preforming the command.
		         path -> The path to list."""

		self.session = session
		self.path = path
		
		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the list directory command."""

		# Validate the session
		if not self.session.validate():
			# Invalid session, so finish and return
			self.finish({'code': 1, 'error': "Session invalid or expired."})
			return

		# Check that the user has permission to preform this command
		if not self.session.server.users[self.session.username]['permissions'] in ('r', 'w', 'a'):
			# User does not have permission, so finish and return
			self.finish({'code': 19, 'error': "User does not have permission to preform this command."})
			return

		# Validate the path
		if not (self.session.validate_path(self.path) and os.path.isdir(self.session.get_full_path(self.path))):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid path."})
			return

		# Preform the list directory operation
		try:
			# List the directory
			data = os.listdir(self.session.get_full_path(self.path))

		except Exception as e:
			# Error while listing directory

			# Check for a file not found error
			if isinstance(e, FileNotFoundError):
				# Finish and return, with a masked error name so as to not give away the local path
				self.finish({'code': 3, 'error': "Path " + json.dumps(self.path) + " not found."})
				return

			# Finish and return the error
			self.finish({'code': 4, 'error': "Error with listing directory: [" + str(e) + "]"})
			return

		# Finish and return with the data
		self.finish({'code': 0, 'data': data})


class MoveCommand(BaseCommand):

	"""The main move command object."""

	def __init__(self, session, path, destination):

		"""Move a path from the file system.
		   Args: session -> The session of the user preforming the command.
		         path -> The path to move.
		         destination -> The destination path."""

		self.session = session
		self.path = path
		self.destination = destination
		
		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the move command."""

		# Validate the session
		if not self.session.validate():
			# Invalid session, so finish and return
			self.finish({'code': 1, 'error': "Session invalid or expired."})
			return

		# Check that the user has permission to preform this command
		if not self.session.server.users[self.session.username]['permissions'] in ('w', 'a'):
			# User does not have permission, so finish and return
			self.finish({'code': 19, 'error': "User does not have permission to preform this command."})
			return

		# Validate the source path
		if not (self.session.validate_path(self.path) and os.path.exists(self.session.get_full_path(self.path))):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid path."})
			return

		# Validate the destination path
		if not self.session.validate_path(self.destination):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid destination path."})
			return

		# Preform the move operation
		try:
			# Move the path
			shutil.move(self.session.get_full_path(self.path), self.session.get_full_path(self.destination))

		except Exception as e:
			# Error while moving path

			# Check for a file not found error
			if isinstance(e, FileNotFoundError):
				# Finish and return, with a masked error name so as to not give away the local path
				self.finish({'code': 3, 'error': "Path " + json.dumps(self.path) + " not found."})
				return

			# Finish and return the error
			self.finish({'code': 4, 'error': "Error with moving path: [" + str(e) + "]"})
			return

		# Finish and return with the data
		self.finish({'code': 0})
		

class CopyCommand(BaseCommand):

	"""The main copy command object."""

	def __init__(self, session, path, destination):

		"""Copy a path from the file system.
		   Args: session -> The session of the user preforming the command.
		         path -> The path to copy.
		         destination -> The destination path."""

		self.session = session
		self.path = path
		self.destination = destination
		
		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the copy command."""

		# Validate the session
		if not self.session.validate():
			# Invalid session, so finish and return
			self.finish({'code': 1, 'error': "Session invalid or expired."})
			return

		# Check that the user has permission to preform this command
		if not self.session.server.users[self.session.username]['permissions'] in ('w', 'a'):
			# User does not have permission, so finish and return
			self.finish({'code': 19, 'error': "User does not have permission to preform this command."})
			return

		# Validate the source path
		if not (self.session.validate_path(self.path) and os.path.exists(self.session.get_full_path(self.path))):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid path."})
			return

		# Validate the destination path
		if not self.session.validate_path(self.destination):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid destination path."})
			return

		# Preform the copy operation
		try:
			# Copy the path
			shutil.copy(self.session.get_full_path(self.path), self.session.get_full_path(self.destination))

		except Exception as e:
			# Error while copying path

			# Check for a file not found error
			if isinstance(e, FileNotFoundError):
				# Finish and return, with a masked error name so as to not give away the local path
				self.finish({'code': 3, 'error': "Path " + json.dumps(self.path) + " not found."})
				return

			# Finish and return the error
			self.finish({'code': 4, 'error': "Error with copying path: [" + str(e) + "]"})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class ChangeDirectoryCommand(BaseCommand):

	"""The main change directory command object."""

	def __init__(self, session, path):

		"""Change the directory for the session.
		   Args: session -> The session of the user preforming the command.
		         path -> The path to change the directory to."""

		self.session = session
		self.path = path
		
		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the change directory command."""

		# Validate the session
		if not self.session.validate():
			# Invalid session, so finish and return
			self.finish({'code': 1, 'error': "Session invalid or expired."})
			return

		# Check that the user has permission to preform this command
		if not self.session.server.users[self.session.username]['permissions'] in ('r', 'w', 'a'):
			# User does not have permission, so finish and return
			self.finish({'code': 19, 'error': "User does not have permission to preform this command."})
			return

		# Validate the new path
		if not self.session.validate_path(self.path):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid path."})
			return

		# Check that the new path exists
		if not os.path.isdir(os.path.abspath(os.path.join(self.session.server.path, self.path))):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid path."})
			return

		# Preform the change directory operation
		try:
			# Change the directory
			if os.path.normpath(self.path).startswith('\\'):
				self.session.current_directory = os.path.normpath(self.path[1 : ])
			else:
				self.session.current_directory = os.path.normpath(os.path.join(self.session.current_directory, self.path))

		except Exception as e:
			# Error while setting path

			# Finish and return the error
			self.finish({'code': 4, 'error': "Error with changing directory: [" + str(e) + "]"})
			return

		# Finish and return with the data
		self.finish({'code': 0})


class CurrentDirectoryCommand(BaseCommand):

	"""The main get current directory command object."""

	def __init__(self, session):

		"""Get the directory for the session.
		   Args: session -> The session of the user preforming the command."""

		self.session = session
		
		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the get directory command."""

		# Validate the session
		if not self.session.validate():
			# Invalid session, so finish and return
			self.finish({'code': 1, 'error': "Session invalid or expired."})
			return

		# Check that the user has permission to preform this command
		if not self.session.server.users[self.session.username]['permissions'] in ('r', 'w', 'a'):
			# User does not have permission, so finish and return
			self.finish({'code': 19, 'error': "User does not have permission to preform this command."})
			return

		# Preform the get directory operation
		try:
			# Get the directory
			path = self.session.current_directory

		except Exception as e:
			# Error while getting path

			# Finish and return the error
			self.finish({'code': 4, 'error': "Error with getting directory: [" + str(e) + "]"})
			return

		# Finish and return with the data
		self.finish({'code': 0, 'path': path})


class SizeCommand(BaseCommand):

	"""The main file size command object."""

	def __init__(self, session, path):

		"""Get the size of a file.
		   Args: session -> The session of the user preforming the command.
		         path -> The path of the file to check."""

		self.session = session
		self.path = path
		
		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the get size command."""

		# Validate the session
		if not self.session.validate():
			# Invalid session, so finish and return
			self.finish({'code': 1, 'error': "Session invalid or expired."})
			return

		# Check that the user has permission to preform this command
		if not self.session.server.users[self.session.username]['permissions'] in ('r', 'w', 'a'):
			# User does not have permission, so finish and return
			self.finish({'code': 19, 'error': "User does not have permission to preform this command."})
			return

		# Validate the path
		if not (self.session.validate_path(self.path) and os.path.isfile(self.session.get_full_path(self.path))):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid path."})
			return

		# Preform the get size operation
		try:
			# Get the size
			size = os.path.getsize(self.session.get_full_path(self.path))

		except Exception as e:
			# Error while checking file size

			# Check for a file not found error
			if isinstance(e, FileNotFoundError):
				# Finish and return, with a masked error name so as to not give away the local path
				self.finish({'code': 3, 'error': "File " + json.dumps(self.path) + " not found."})
				return

			# Finish and return the error
			self.finish({'code': 4, 'error': "Error with getting file size: [" + str(e) + "]"})
			return

		# Finish and return with the data
		self.finish({'code': 0, 'size': size})


class ExistsCommand(BaseCommand):

	"""The path/file exists command object."""

	def __init__(self, session, path):

		"""Check if a path exists, and if so, whether it is a file or a folder.
		   Args: session -> The session of the user preforming the command.
		         path -> The path to check."""

		self.session = session
		self.path = path
		
		self.data = None
		self.finished = False

	def preform(self):

		"""Preform the exists command."""

		# Validate the session
		if not self.session.validate():
			# Invalid session, so finish and return
			self.finish({'code': 1, 'error': "Session invalid or expired."})
			return

		# Check that the user has permission to preform this command
		if not self.session.server.users[self.session.username]['permissions'] in ('r', 'w', 'a'):
			# User does not have permission, so finish and return
			self.finish({'code': 19, 'error': "User does not have permission to preform this command."})
			return

		# Validate the path
		if not (self.session.validate_path(self.path)):
			# Invalid path
			self.finish({'code': 18, 'error': "Invalid path."})
			return

		# Preform the exists command
		try:
			# Check if it exists
			exists = os.path.exists(self.session.get_full_path(self.path))

			isfile = False
			isdir = False

			# Check if it is a file or a folder
			if os.path.isfile(self.session.get_full_path(self.path)):
				isfile = True

			elif os.path.isdir(self.session.get_full_path(self.path)):
				isdir = True

		except Exception as e:
			# Error while checking file existence

			# Finish and return the error
			self.finish({'code': 4, 'error': "Error with getting file size: [" + str(e) + "]"})
			return

		# Finish and return with the data
		self.finish({'code': 0, 'exists': exists, 'isfile': isfile, 'isdir': isdir})
