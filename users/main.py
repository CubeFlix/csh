"""

- CSH User Tool Main Source Code -

(C) Cubeflix 2022 (CSH)

"""


# ---------- IMPORTS ----------

from src import UserTool, VERSION


# For command-line arguments
import argparse


# ---------- CONSTANTS ----------

PROG = 'cshuser'


DESCRIPTION = '''cshuser is a tool for managing CSH user data files. '''


# ---------- MAIN ----------

def main():

    """The main starting point for the CSH user tool."""

    # Command-line arguments

    # Create the argument parser
    parser = argparse.ArgumentParser(description=DESCRIPTION, prog=PROG)

    # Add the arguments
    parser.add_argument('file', help="The users file to use.")

    # Add the subparsers for each command
    subparser = parser.add_subparsers(dest='command')

    # Add each command
    add = subparser.add_parser('add', help="Add a user.")
    get = subparser.add_parser('get', help="Get information on a user.")
    edit = subparser.add_parser('edit', help="Edit a user's information.")
    remove = subparser.add_parser('remove', help="Remove a user.")
    new = subparser.add_parser('new', help="Make a new users file.")

    # Add the arguments for each command
    
    # Add command
    add.add_argument('-u', '--username', required=True, help="The username for the new user.")
    add.add_argument('-p', '--password', required=True, help="The password for the new user.")
    add.add_argument('-r', '--permissions', required=True, choices='rwa', help="The permissions for the new user.")

    # Get command
    get.add_argument('-u', '--username', required=True, help="The username to get information on.")
    
    # Edit command
    edit.add_argument('-u', '--username', required=True, help="The username to edit.")
    edit.add_argument('-p', '--password', help="The new password for the user.")
    edit.add_argument('-r', '--permissions', choices='rwa', help="The new permissions for the user.")

    # Remove command
    remove.add_argument('-u', '--username', required=True, help="The username to remove.")

    # Parse the arguments
    args = parser.parse_args()

    # Create the user tool
    if args.command != 'new':
        tool = UserTool(args.file)

    # Handle each command
    if args.command == 'add':
        # Add command
        tool.create_user(args.username, args.password, args.permissions)
        
        # Print output
        print("SUCESSFULLY CREATED USER: [" + args.username + "]")

    elif args.command == 'get':
        # Get command
        data = tool.get_user(args.username)

        # Print output
        print("USER [" + args.username + "]:")
        print("    HASH [" + data["password_hash"] + "]")
        print("    PERMISSIONS [" + data["permissions"].upper() + "]")

    elif args.command == 'edit':
        # Edit command
        tool.edit_user(args.username, 
                password=(args.password if hasattr(args, 'password') else None), 
                permissions=(args.permissions if hasattr(args, 'permissions') else None))

        # Print output
        print("SUCESSFULLY EDITED USER: [" + args.username + "]")
    
    elif args.command == 'remove':
        # Remove command
        tool.delete_user(args.username)

        # Print output
        print("SUCESSFULLY REMOVED USER: [" + args.username + "]")

    elif args.command == 'new':
        # New command
        file_handle = open(args.file, 'w')

        # Write to the file
        file_handle.write('{}')

        # Close the file
        file_handle.close()

        # Print output
        print("SUCESSFULLY CREATED NEW USERS FILE: [" + args.file + "]")


if __name__ == '__main__':
    # Run main
    try:
        main()
    except Exception as e:
        # Error with running main
        print("ERROR IN MAIN: [" + str(e) + "]")

