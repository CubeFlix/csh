"""

- CSH Server Main Source Code -

(C) Cubeflix 2021 (CSH)

"""


# ---------- IMPORTS ----------

from src import ServerRuntime, VERSION, LANG


# For command-line arguments
import argparse


# ---------- CONSTANTS ----------

PROG = 'cshs'


DESCRIPTION = '''cshs is a tool for managing and hosting CSH network file servers. '''


ARGS = ['port', 'host', 'path', 'name', 'users', 'logfile', 'level']


# ---------- FUNCTIONS ----------

def empty_users():

	"""In case there is an empty users file, prompt the user to create an admin account."""

	# Ask if the user would like to create an admin
	input_data = input("NO USERS FOUND IN USERS FILE. WOULD YOU LIKE TO CREATE AN ADMIN USER (y/n)? ").lower()

	# Continually ask until we get a valid answer
	while len(input_data) == 0:
		input_data = input("NO USERS FOUND IN USERS FILE. WOULD YOU LIKE TO CREATE AN ADMIN USER (y/n)? ").lower()

	# Check the answer
	if input_data[0] == 'n':
		return

	# Ask for the new username
	username = input("USERNAME: ")

	# Continually ask until we get a valid answer
	while len(username) == 0:
		username = input("USERNAME: ")

	# Ask for a new password
	password = input("PASSWORD: ")

	# Continually ask until we get a valid answer
	while len(password) == 0:
		password = input("PASSWORD: ")

	# Return the user data
	return (username, password)


# ---------- MAIN ----------

def main():

	"""The main starting point for the CSH server."""

	# Command-line arguments

	# Create the argument parser
	parser = argparse.ArgumentParser(description=DESCRIPTION, prog=PROG)

	# Add the arguments
	parser.add_argument('config', nargs='?', default='config.json', help='The configuration file for the CSH server. Defaults to config.json.')
	parser.add_argument('-c', '--noconfig', action='store_true', help="Don't use a configuration file.")
	parser.add_argument('-p', '--port', type=int, help='Set the port to host on.')
	parser.add_argument('-o', '--host', help='Set the host name to host on.')
	parser.add_argument('-d', '--path', help='Set the path/working directory to use.')
	parser.add_argument('-n', '--name', help='Set the name of the server.')
	parser.add_argument('-u', '--users', help='The users file for the CSH server.')
	parser.add_argument('-l', '--logfile', help='Set the file the server should log to.')
	parser.add_argument('-e', '--level', help='Set the logging level.')

	# Add the version option
	parser.add_argument('-v', '--version', action='version', version=f'%(prog)s v{VERSION} {LANG}')

	# Parse the command-line arguments
	args = parser.parse_args()

	# Create a valid args dictionary
	args_dict = {}

	# Iterate over all arguments
	for arg in ARGS:
		# Check if the argument is defined in the command-line arguments
		if getattr(args, arg):
			# Check for the users argument
			if arg == 'users':
				# It needs a special name 
				args_dict['users_file'] = getattr(args, 'users')

			# Check for the logfile argument
			elif arg == 'logfile':
				# It needs a special name
				args_dict['file_handler'] = getattr(args, 'logfile')

			# Check for the name argument
			elif arg == 'name':
				# It needs a special name
				args_dict['server_name'] = getattr(args, 'name')

			else:
				# Add the argument to the dictionary
				args_dict[arg] = getattr(args, arg)

	# Check for the --noconfig option
	noconfig = args.noconfig

	# Create the runtime
	runtime = ServerRuntime({} if noconfig else args.config, args_dict)

	# Create the server
	runtime.create_server()

	# Check for an empty users file
	if runtime.server.users == {}:
		# Show the empty users file prompt
		print("\n----------")
		prompt_result = empty_users()
		print("----------\n")

		# Add the user to the file
		if prompt_result:
			# Add the user
			runtime.server.create_user(*prompt_result, 'a')

	# Run the server
	runtime.start_server()


if __name__ == '__main__':
	# Run main
	try:
		main()
	except Exception as e:
		# Error with running main
		print("ERROR IN MAIN: [" + str(e) + "]")
